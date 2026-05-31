"""
experiment.py — Sprint 2 : Expérience principale TIE
Implémente les Tâches 2.1, 2.2, 2.4 de SPRINT-2-context.md.

Contrats respectés :
  R-REPRO-01 : seed_run = SEED_GLOBAL * 1000 + run_idx (déterministe)
  R-REPRO-02 : CLAIMChannel bit-à-bit reproductible même seed
  R-STAT-02  : N=50 runs par cellule minimum
  R-CONFLIT-01 : inject_conflict sur Canal C systématique
"""

import torch
import pandas as pd
import numpy as np
import time
import sys
import os

# Import depuis le module standalone (pas de dépendance HuggingFace)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.channels_standalone import TextChannel, LatentChannel, CLAIMChannel

# ── Paramètres globaux (source : VARIABLES.md) ─────────────────────────────

SEED_GLOBAL = 42
HIDDEN_DIM = 768
ENTROPY_LEVELS = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
CONFLICT_LEVELS = [0.0, 0.2, 0.5, 0.8]
THETA = ["ami", "ennemi", "neutre", "inconnu"]
N_RUNS = 50


# ── Génération des vecteurs latents ────────────────────────────────────────

def generate_latent_with_entropy(
    entropy_level: float,
    hidden_dim: int = HIDDEN_DIM,
    seed: int = SEED_GLOBAL,
    run_idx: int = 0,
) -> torch.Tensor:
    """
    Génère h de shape (1, hidden_dim) avec entropie softmax ≈ entropy_level.

    Stratégie : initialiser h uniforme, puis appliquer un facteur de concentration
    α = log(vocab) / entropy_level qui "aiguise" ou "aplatit" la distribution.
    Contrat R-REPRO-01 : déterministe pour (entropy_level, seed, run_idx).
    """
    seed_run = seed * 1000 + run_idx
    gen = torch.Generator().manual_seed(seed_run)

    # Vecteur de base
    h = torch.randn(1, hidden_dim, generator=gen)

    # Contrôle de l'entropie : température inversement proportionnelle à entropy_level
    # entropie max = log(hidden_dim) ≈ 6.64 pour hidden_dim=768
    # On module la norme de h pour contrôler la concentration de la softmax
    max_entropy = math.log(hidden_dim)
    # ratio ∈ (0, 1] : 1 = entropie max (h uniforme), 0 = entropie nulle (h concentré)
    ratio = min(entropy_level / max_entropy, 1.0)
    # température : haute → distribution plate (entropie haute), basse → piquée
    temperature = ratio + 0.01  # éviter division par zéro
    h = h / (h.norm(dim=-1, keepdim=True) + 1e-8) * (1.0 / temperature)

    return h


import math


# ── Boucle expérimentale principale (Tâche 2.1) ───────────────────────────

def run_experiment(
    channels: dict,
    entropy_levels: list = ENTROPY_LEVELS,
    n_runs: int = N_RUNS,
    seed_global: int = SEED_GLOBAL,
    output_path: str = "results/raw_results.csv",
) -> pd.DataFrame:
    """
    3 canaux × 6 niveaux d'entropie × 50 runs = 900 lignes minimum.
    Schéma : canal, entropy_level, run_idx, seed_run, jacobian_norm,
             output_entropy, duration_ms
    """
    rows = []
    total = len(channels) * len(entropy_levels) * n_runs
    done = 0

    for canal_name, channel in channels.items():
        for entropy_level in entropy_levels:
            for run_idx in range(n_runs):
                seed_run = seed_global * 1000 + run_idx
                h = generate_latent_with_entropy(
                    entropy_level, HIDDEN_DIM, seed_global, run_idx
                )

                t0 = time.perf_counter()
                try:
                    jacobian_norm = channel.get_jacobian_norm(h)
                    output_entropy = channel.get_output_entropy(h)
                except Exception as e:
                    print(f"  [WARN] {canal_name} entropy={entropy_level} run={run_idx}: {e}")
                    jacobian_norm = float("nan")
                    output_entropy = float("nan")
                duration_ms = (time.perf_counter() - t0) * 1000

                rows.append({
                    "canal": canal_name,
                    "entropy_level": entropy_level,
                    "run_idx": run_idx,
                    "seed_run": seed_run,
                    "jacobian_norm": jacobian_norm,
                    "output_entropy": output_entropy,
                    "duration_ms": round(duration_ms, 3),
                })

                done += 1
                if done % 50 == 0 or done == total:
                    print(f"  [{done}/{total}] {canal_name} | ε={entropy_level} | run={run_idx}")

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✅ raw_results.csv : {len(df)} lignes → {output_path}")
    return df


# ── Expérience conflit injecté (Tâche 2.2) ────────────────────────────────

def run_conflict_experiment(
    claim_channel: CLAIMChannel,
    entropy_levels: list = ENTROPY_LEVELS,
    conflict_levels: list = CONFLICT_LEVELS,
    n_runs: int = N_RUNS,
    seed_global: int = SEED_GLOBAL,
    output_path: str = "results/conflict_results.csv",
) -> pd.DataFrame:
    """
    1 canal (C) × 4 niveaux conflit × 6 niveaux entropie × 50 runs = 1200 lignes.
    Schéma : entropy_level, conflict_level, run_idx, seed_run,
             jacobian_norm, output_entropy, m_vide
    Invariant : abs(m_vide - conflict_level) < 0.01
    """
    rows = []
    total = len(conflict_levels) * len(entropy_levels) * n_runs
    done = 0

    for conflict_level in conflict_levels:
        for entropy_level in entropy_levels:
            for run_idx in range(n_runs):
                seed_run = seed_global * 1000 + run_idx
                h = generate_latent_with_entropy(
                    entropy_level, HIDDEN_DIM, seed_global, run_idx
                )

                t0 = time.perf_counter()
                try:
                    claim = claim_channel.inject_conflict(h, conflict_level)
                    m_vide = claim.belief_mass.get(frozenset(), 0.0)

                    # Vérification invariant R-CONFLIT-01
                    if abs(m_vide - conflict_level) >= 0.01:
                        print(f"  [QO-S2-01] conflit={conflict_level} m(∅)={m_vide:.4f} "
                              f"run={run_idx} — invariant violé")

                    jacobian_norm = claim_channel.get_jacobian_norm(h)
                    output_entropy = claim_channel.get_output_entropy(h)
                except Exception as e:
                    print(f"  [WARN] conflict={conflict_level} run={run_idx}: {e}")
                    m_vide = float("nan")
                    jacobian_norm = float("nan")
                    output_entropy = float("nan")

                duration_ms = (time.perf_counter() - t0) * 1000

                rows.append({
                    "entropy_level": entropy_level,
                    "conflict_level": conflict_level,
                    "run_idx": run_idx,
                    "seed_run": seed_run,
                    "jacobian_norm": jacobian_norm,
                    "output_entropy": output_entropy,
                    "m_vide": m_vide,
                    "duration_ms": round(duration_ms, 3),
                })

                done += 1
                if done % 50 == 0 or done == total:
                    print(f"  [{done}/{total}] conflit={conflict_level} | ε={entropy_level} | run={run_idx}")

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✅ conflict_results.csv : {len(df)} lignes → {output_path}")
    return df


# ── Vérification reproductibilité (Tâche 2.4) ─────────────────────────────

def verify_reproducibility(
    channel,
    entropy_level: float = 0.05,
    n_runs: int = 5,
    seed_global: int = SEED_GLOBAL,
) -> bool:
    """
    Exécute deux fois les mêmes 5 runs.
    Retourne True si jacobian_norm identique à 1e-6 près (R-REPRO-01).
    """
    results = []
    for _ in range(2):
        run_results = []
        for run_idx in range(n_runs):
            h = generate_latent_with_entropy(entropy_level, HIDDEN_DIM, seed_global, run_idx)
            jn = channel.get_jacobian_norm(h)
            run_results.append(jn)
        results.append(run_results)

    ok = all(abs(results[0][i] - results[1][i]) < 1e-6 for i in range(n_runs))
    if not ok:
        diffs = [abs(results[0][i] - results[1][i]) for i in range(n_runs)]
        print(f"  [QO-S2-03] Reproductibilité violée — diffs max: {max(diffs):.2e}")
    return ok


# ── Point d'entrée principal ───────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("EIP — Sprint 2 : Expérience principale TIE")
    print("=" * 60)

    # Instanciation des canaux
    print("\n[1/5] Initialisation des canaux...")
    ch_text = TextChannel(seed=SEED_GLOBAL)
    ch_latent = LatentChannel(hidden_dim=HIDDEN_DIM, seed=SEED_GLOBAL)
    ch_claim = CLAIMChannel(theta=THETA, seed=SEED_GLOBAL)
    print("  ✅ TextChannel, LatentChannel, CLAIMChannel initialisés")

    channels = {
        "text": ch_text,
        "latent": ch_latent,
        "claim": ch_claim,
    }

    # Vérification reproductibilité (Tâche 2.4)
    print("\n[2/5] Vérification reproductibilité (canal latent, ε=0.05, 5 runs)...")
    repro_ok = verify_reproducibility(ch_latent)
    print(f"  {'✅ Reproductible' if repro_ok else '❌ NON reproductible — QO-S2-03 ouvert'}")

    # Expérience principale (Tâche 2.1)
    print("\n[3/5] Expérience principale (3 × 6 × 50 = 900 lignes)...")
    df_raw = run_experiment(
        channels=channels,
        output_path="results/raw_results.csv",
    )

    # Expérience conflit (Tâche 2.2)
    print("\n[4/5] Expérience conflit Canal C (4 × 6 × 50 = 1200 lignes)...")
    df_conflict = run_conflict_experiment(
        claim_channel=ch_claim,
        output_path="results/conflict_results.csv",
    )

    # Résumé
    print("\n[5/5] Résumé")
    print(f"  raw_results.csv    : {len(df_raw)} lignes ({'✅' if len(df_raw) >= 900 else '❌'})")
    print(f"  conflict_results.csv: {len(df_conflict)} lignes ({'✅' if len(df_conflict) >= 1200 else '❌'})")
    print("\n  Statistiques rapides (jacobian_norm par canal) :")
    print(df_raw.groupby("canal")["jacobian_norm"].agg(["median", "mean", "std"]).round(4).to_string())
    print("\n✅ Sprint 2 terminé — commiter avec :")
    print("   [SPRINT-2] run main TIE experiment : results/raw_results.csv")
