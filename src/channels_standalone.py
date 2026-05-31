"""
channels_standalone.py — Implémentation autonome des trois canaux EIP
Compatible Sprint 1 (contrats API SPRINT-1-context.md).
Sans dépendance HuggingFace Hub.

get_jacobian_norm : power iteration via jvp/vjp (O(n_vecs) passes).
  - TextChannel  : vocab sous-échantillonné à 2048 tokens (seed fixe),
                   n_vecs=2 → ~43ms/run
  - LatentChannel: direct, n_vecs=5 → ~10ms/run
  - CLAIMChannel : direct sur la tête linéaire, n_vecs=5 → ~2ms/run
"""

import torch
import math
from dataclasses import dataclass
from typing import Literal, Dict, FrozenSet
from itertools import chain, combinations


# ── CLAIM ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CLAIM:
    proposition: str
    belief_mass: Dict[FrozenSet, float]
    belnap_state: Literal["T", "F", "B", "N"]
    illocution: Literal["OBSERVE", "INFER", "DEDUCE", "ASSUME"]
    freshness: tuple
    provenance: str


# ── Utilitaire : power iteration (jvp/vjp) ────────────────────────────────

def _spectral_norm_power(fn, h: torch.Tensor, n_vecs: int = 5) -> float:
    """
    Estime la norme spectrale ‖J_fn(h)‖₂ via power iteration.
    O(n_vecs) appels jvp + vjp. Précision ~5% sur n_vecs=5.
    """
    h_base = h.clone().detach()
    torch.manual_seed(0)  # déterministe entre appels
    v = torch.randn_like(h_base)
    v = v / (v.norm() + 1e-10)
    sigma = 0.0
    for _ in range(n_vecs):
        try:
            _, jv = torch.autograd.functional.jvp(
                fn, h_base, v, create_graph=False, strict=False
            )
            sigma = jv.norm().item()
            if sigma < 1e-10:
                return 0.0
            _, vjh = torch.autograd.functional.vjp(
                fn, h_base, (jv / sigma).detach(), create_graph=False
            )
            v = vjh / (vjh.norm() + 1e-10)
        except Exception:
            return 0.0
    try:
        _, jv_final = torch.autograd.functional.jvp(
            fn, h_base, v, create_graph=False, strict=False
        )
        return max(jv_final.norm().item(), 0.0)
    except Exception:
        return sigma


# ── TextChannel ────────────────────────────────────────────────────────────

class TextChannel:
    VOCAB_SIZE = 50257
    HIDDEN_DIM = 768
    _VOCAB_SAMPLE = 2048   # sous-ensemble fixe pour jacobien (13x plus rapide)

    def __init__(self, model_name: str = "gpt2", seed: int = 42):
        self.seed = seed
        gen = torch.Generator().manual_seed(seed)
        # Matrice wte fixe (remplace les poids GPT-2 réels)
        self.wte = torch.randn(self.VOCAB_SIZE, self.HIDDEN_DIM, generator=gen) * 0.02
        self.hidden_dim = self.HIDDEN_DIM
        # Sous-ensemble fixe pour le jacobien (déterministe)
        gen_sub = torch.Generator().manual_seed(seed + 99)
        self._vocab_idx = torch.randperm(self.VOCAB_SIZE, generator=gen_sub)[:self._VOCAB_SAMPLE]
        self._wte_sub = self.wte[self._vocab_idx]  # (2048, 768)

    def encode(self, h: torch.Tensor) -> torch.Tensor:
        h = h.clone()
        logits = torch.matmul(h, self.wte.T)
        probs = torch.softmax(logits, dim=-1)
        tokens = torch.argmax(probs, dim=-1)
        return self.wte[tokens]

    def _soft_encode_sub(self, h: torch.Tensor) -> torch.Tensor:
        """Version différentiable sur sous-vocab (pour jacobien)."""
        logits = torch.matmul(h, self._wte_sub.T)
        probs = torch.softmax(logits, dim=-1)
        return torch.matmul(probs, self._wte_sub)

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        return _spectral_norm_power(self._soft_encode_sub, h, n_vecs=2)

    def get_output_entropy(self, h: torch.Tensor) -> float:
        with torch.no_grad():
            logits = torch.matmul(h, self.wte.T)
            probs = torch.softmax(logits, dim=-1)
            p = torch.clamp(probs[0], min=1e-10)
            return (-torch.sum(p * torch.log(p))).item()


# ── LatentChannel ──────────────────────────────────────────────────────────

class LatentChannel:
    def __init__(self, hidden_dim: int = 768, seed: int = 42):
        self.hidden_dim = hidden_dim
        self.seed = seed
        gen = torch.Generator().manual_seed(seed)
        mid = hidden_dim // 4
        self.fc1 = torch.nn.Linear(hidden_dim, mid)
        self.fc2 = torch.nn.Linear(mid, hidden_dim)
        self.gelu = torch.nn.GELU()

        def xavier_(w, g):
            fi, fo = torch.nn.init._calculate_fan_in_and_fan_out(w)
            a = math.sqrt(3.0) * math.sqrt(2.0 / (fi + fo))
            with torch.no_grad():
                w.uniform_(-a, a, generator=g)

        xavier_(self.fc1.weight, gen)
        torch.nn.init.zeros_(self.fc1.bias)
        xavier_(self.fc2.weight, gen)
        torch.nn.init.zeros_(self.fc2.bias)

        for p in list(self.fc1.parameters()) + list(self.fc2.parameters()):
            p.requires_grad = False

    def encode(self, h: torch.Tensor) -> torch.Tensor:
        h = h.clone()
        return h + self.fc2(self.gelu(self.fc1(h)))

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        return _spectral_norm_power(self.encode, h, n_vecs=5)

    def get_output_entropy(self, h: torch.Tensor) -> float:
        with torch.no_grad():
            h_out = self.encode(h)[0]
            h_norm = (h_out - h_out.min()) / (h_out.max() - h_out.min() + 1e-8)
            bins = torch.linspace(0, 1, 50)
            dist = torch.abs(h_norm.unsqueeze(-1) - bins.unsqueeze(0))
            soft = torch.softmax(-dist / 0.1, dim=-1)
            hist = soft.sum(0)
            probs = torch.clamp(hist / hist.sum(), min=1e-10)
            return (-torch.sum(probs * torch.log(probs))).item()


# ── CLAIMChannel ───────────────────────────────────────────────────────────

class CLAIMChannel:
    def __init__(self, theta: list = None, seed: int = 42):
        if theta is None:
            theta = ["ami", "ennemi", "neutre", "inconnu"]
        self.theta = theta
        self.seed = seed
        self.powerset_size = 2 ** len(theta)
        subsets = list(chain.from_iterable(
            combinations(theta, r) for r in range(len(theta) + 1)
        ))
        self._idx2fs = {i: frozenset(s) for i, s in enumerate(subsets)}
        self._fs2idx = {v: k for k, v in self._idx2fs.items()}
        self.linear = None
        self.hidden_dim = None
        self._gen = torch.Generator().manual_seed(seed)

    def _ensure_linear(self, hidden_dim: int):
        if self.linear is None or self.hidden_dim != hidden_dim:
            self.hidden_dim = hidden_dim
            self.linear = torch.nn.Linear(hidden_dim, self.powerset_size)
            fi, fo = torch.nn.init._calculate_fan_in_and_fan_out(self.linear.weight)
            a = math.sqrt(3.0) * math.sqrt(2.0 / (fi + fo))
            with torch.no_grad():
                self.linear.weight.uniform_(-a, a, generator=self._gen)
                torch.nn.init.zeros_(self.linear.bias)
            for p in self.linear.parameters():
                p.requires_grad = False

    def _masses(self, h: torch.Tensor) -> torch.Tensor:
        self._ensure_linear(h.size(-1))
        return torch.softmax(self.linear(h), dim=-1)

    def encode(self, h: torch.Tensor) -> CLAIM:
        h = h.clone()
        with torch.no_grad():
            masses = self._masses(h).squeeze(0)
        bm = {self._idx2fs[i]: masses[i].item() for i in range(self.powerset_size)}
        return self._build_claim(bm)

    def inject_conflict(self, h: torch.Tensor, conflict_level: float) -> CLAIM:
        h = h.clone()
        with torch.no_grad():
            masses = self._masses(h).squeeze(0)
        bm = {self._idx2fs[i]: masses[i].item() for i in range(self.powerset_size)}
        empty = frozenset()
        bm[empty] = conflict_level
        non_empty_sum = sum(v for k, v in bm.items() if k != empty)
        if non_empty_sum > 1e-8:
            scale = (1.0 - conflict_level) / non_empty_sum
            bm = {k: (v * scale if k != empty else v) for k, v in bm.items()}
        return self._build_claim(bm)

    def _build_claim(self, bm: dict) -> CLAIM:
        best, best_m = "inconnu", 0.0
        for fs, m in bm.items():
            if len(fs) == 1 and m > best_m:
                best_m = m; best = next(iter(fs))
        conflict = bm.get(frozenset(), 0.0)
        if conflict > 0.5:
            bs = "B"
        else:
            ts = sum(m for fs, m in bm.items() if fs == frozenset(["ami"]))
            fs_ = sum(m for fs, m in bm.items() if fs == frozenset(["ennemi"]))
            bs = "T" if ts > fs_ + 0.2 else ("F" if fs_ > ts + 0.2 else "N")
        return CLAIM(
            proposition=best, belief_mass=bm, belnap_state=bs,
            illocution="OBSERVE", freshness=(0.0, 1.0), provenance="chain_0"
        )

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        self._ensure_linear(h.size(-1))
        for p in self.linear.parameters():
            p.requires_grad_(True)
        try:
            return _spectral_norm_power(self._masses, h, n_vecs=5)
        finally:
            for p in self.linear.parameters():
                p.requires_grad_(False)

    def get_output_entropy(self, h: torch.Tensor) -> float:
        claim = self.encode(h)
        return -sum(max(m, 1e-10) * math.log(max(m, 1e-10))
                    for m in claim.belief_mass.values())
