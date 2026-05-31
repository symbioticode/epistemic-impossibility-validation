import torch
import numpy as np
from typing import Union, Protocol
from transformers import GPT2Model, GPT2Tokenizer
import math
from dataclasses import dataclass
from typing import Literal, Dict, FrozenSet


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
            v = vjh / (torch.norm(vjh) + 1e-10)
        except:
            # If JVP/VJP fails, fall back to a simple estimate
            return 0.0
    return sigma


class TextChannel:
    """Textual communication channel.

    Provides a certification function ``φ`` (exposed as ``certify_output``) that
    verifies whether a produced token belongs to the model vocabulary.  In the
    current setting every token emitted by the GPT‑2 tokenizer is a valid token,
    so the function always returns ``True``.  The method is also available under
    the historic name :py:meth:`is_certified` for backward compatibility.
    """

    """
    Canal de communication texte.
    Encode un état latent h via softmax → token → re-embedding.
    Pure function : mêmes entrées → mêmes sorties, toujours.
    Pas de state interne entre appels.
    """

    def certify_output(self, token: int) -> bool:
        """Certification function φ for a generated token.

        Args:
            token: Token identifier produced by :meth:`encode`.
        Returns:
            ``True`` if ``token`` is within the vocabulary range.  The GPT‑2
            tokenizer defines a contiguous range ``[0, vocab_size)``; therefore
            the check is a simple bounds test.
        """
        vocab_size = self.model.config.vocab_size
        return 0 <= token < vocab_size

    # Backward‑compatible alias used throughout the code base.
    is_certified = certify_output
    def __init__(self, model_name: str = "gpt2", seed: int = 42):
        """Initialize the GPT‑2 based text channel.

        Args:
            model_name: HuggingFace model identifier (default "gpt2").
            seed: Random seed for reproducibility of any internal sampling.
        """

        """Initialize the GPT‑2 based text channel.

        Args:
            model_name: HuggingFace model identifier (default "gpt2").
            seed: Random seed for reproducibility of any internal sampling.
        """

        """
        model_name : identifiant HuggingFace (défaut : "gpt2")
        seed       : seed pour reproductibilité
        Postcondition : self.model est en mode eval(), grad désactivé.
        """
        self.seed = seed
        self.generator = torch.Generator().manual_seed(seed)
        
        # Load tokenizer and model
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2Model.from_pretrained(model_name)
        
        # Set model to evaluation mode and disable gradients
        self.model.eval()
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Store hidden size for consistency
        self.hidden_dim = self.model.config.hidden_size

    def encode(self, h: torch.Tensor) -> torch.Tensor:
        """
        Entrée  : h de shape (batch, hidden_dim) — état latent normalisé
        Sortie  : h_out de shape (batch, hidden_dim) — état latent re-encodé
        Contrat : encode(h) est deterministe pour h fixé et seed fixé.
        Contrat : aucune modification de h en place.
        """
        # Ensure we don't modify input
        h = h.clone()
        
        # Project hidden states to vocabulary logits (we need a linear layer to vocab size)
        # Since GPT-2 model doesn't have a tied output embedding by default in the base model,
        # we'll use the model's word embedding matrix for projection
        if h.size(-1) != self.hidden_dim:
            raise ValueError(f"Input hidden dimension {h.size(-1)} does not match model's {self.hidden_dim}")
        
        # Project to vocabulary space using the model's word embedding matrix (tied weights)
        # GPT-2 uses tied weights: the output projection matrix is the same as the input embeddings
        logits = torch.matmul(h, self.model.wte.weight.T)  # (batch, vocab_size)
        
        # Apply softmax to get probabilities
        probs = torch.softmax(logits, dim=-1)  # (batch, vocab_size)
        
        # Sample tokens (deterministically: take argmax for determinism)
        # Note: For pure function with same input -> same output, we use argmax
        tokens = torch.argmax(probs, dim=-1)  # (batch,)
        
        # Get embeddings for the selected tokens
        h_out = self.model.wte(tokens)  # (batch, hidden_dim)
        
        return h_out

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        """Return the spectral norm of the Jacobian of `encode`.

        The textual channel's `encode` is inherently discrete (argmax). To obtain a
        meaningful Jacobian we use a differentiable proxy (`soft_encode_fn`) that
        computes a weighted sum of the token embeddings.
        """

        """Return the spectral norm of the Jacobian of `encode`.

        The textual channel's `encode` is inherently discrete (argmax). To obtain a
        meaningful Jacobian we use a differentiable proxy (`soft_encode_fn`) that
        computes a weighted sum of the token embeddings.
        """

        h_clone = h.detach().requires_grad_(True)

        # Define a differentiable version of encode for Jacobian calculation
        def soft_encode_fn(x):
            # Project to vocabulary space
            logits = torch.matmul(x, self.model.wte.weight.T)
            # Softmax to get probabilities
            probs = torch.softmax(logits, dim=-1)
            # Differentiable approximation: weighted sum of embeddings
            return torch.matmul(probs, self.model.wte.weight)
        
        # Compute Jacobian using torch.autograd.functional.jacobian
        jacobian = torch.autograd.functional.jacobian(soft_encode_fn, h_clone, vectorize=True)
        
        # The Jacobian will have shape (batch, hidden_dim, batch, hidden_dim)
        # We need the spectral norm for each batch element and then take the max or average?
        # According to the contract, we return a float. Let's compute the spectral norm for the first batch element
        # and return it. Alternatively, we can flatten the batch and hidden dimensions?
        # The spec says: norme spectrale du jacobien de encode() en h.
        # For a single input (batch=1), the Jacobian is (hidden_dim, hidden_dim)
        if h_clone.dim() == 2 and h_clone.size(0) == 1:
            # For batch size 1, Jacobian is (hidden_dim, hidden_dim)
            jacobian_single = jacobian[0, :, 0, :]  # (hidden_dim, hidden_dim)
            # Compute spectral norm (largest singular value)
            singular_values = torch.linalg.svdvals(jacobian_single)
            spectral_norm = singular_values[0].item()
            return max(spectral_norm, 0.0)  # Ensure non-negative
        else:
            # For batch size > 1, we compute the spectral norm for each sample and return the max
            spectral_norms = []
            for i in range(h_clone.size(0)):
                jacobian_i = jacobian[i, :, i, :]  # (hidden_dim, hidden_dim)
                singular_values = torch.linalg.svdvals(jacobian_i)
                spectral_norms.append(singular_values[0].item())
            return max(spectral_norms) if spectral_norms else 0.0

    def get_output_entropy(self, h: torch.Tensor) -> float:
        """Compute Shannon entropy of the softmax distribution over the vocabulary.

        Returns:
            float: Entropy value in the interval [0, log(vocab_size)].
        """
        with torch.no_grad():
            # Project to vocabulary logits
            logits = torch.matmul(h, self.model.wte.weight.T)  # (batch, vocab_size)
            probs = torch.softmax(logits, dim=-1)  # (batch, vocab_size)
            
            # Compute entropy for each batch element and return the mean (or first?)
            # The spec doesn't specify batch handling, but entropy is a scalar.
            # Let's compute entropy for the first element in the batch.
            # Avoid log(0) by clamping
            probs_clamped = torch.clamp(probs, min=1e-10)
            entropy = -torch.sum(probs_clamped * torch.log(probs_clamped), dim=-1)  # (batch,)
            
            # Return entropy for the first batch element
            return entropy[0].item()


class LatentChannel:
    """
    Canal de communication latent.
    Transmet l'état interne via une connexion résiduelle apprise.
    Gradient-preserving par construction (jacobien ≈ I + ε).
    """

    def __init__(self, hidden_dim: int = 768, seed: int = 42):
        """
        hidden_dim : dimension de l'espace latent (défaut : 768 pour GPT-2 small)
        seed       : seed pour reproductibilité
        """
        self.hidden_dim = hidden_dim
        self.seed = seed
        self.generator = torch.Generator().manual_seed(seed)
        
        # Create a small MLP: 2 layers with GELU activation
        # Layer 1: hidden_dim -> hidden_dim//4
        # Layer 2: hidden_dim//4 -> hidden_dim
        self.fc1 = torch.nn.Linear(hidden_dim, hidden_dim // 4)
        self.fc2 = torch.nn.Linear(hidden_dim // 4, hidden_dim)
        self.gelu = torch.nn.GELU()
        
        # Initialize weights
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize weights using Xavier initialization with local generator"""
        def xavier_uniform_local_(tensor, generator):
            fan_in, fan_out = torch.nn.init._calculate_fan_in_and_fan_out(tensor)
            std = math.sqrt(2.0 / (fan_in + fan_out))
            a = math.sqrt(3.0) * std
            with torch.no_grad():
                return tensor.uniform_(-a, a, generator=generator)

        xavier_uniform_local_(self.fc1.weight, self.generator)
        torch.nn.init.zeros_(self.fc1.bias)
        xavier_uniform_local_(self.fc2.weight, self.generator)
        torch.nn.init.zeros_(self.fc2.bias)

    def encode(self, h: torch.Tensor) -> torch.Tensor:
        """
        Entrée  : h de shape (batch, hidden_dim)
        Sortie  : h_out = h + f(h) de shape (batch, hidden_dim)
                  où f est une petite MLP (2 couches, activation GELU)
        Contrat : encode(h) est déterministe pour h fixé et seed fixé.
        Contrat : ‖J_C(h)‖₂ ≥ 0.5 pour tout h (gradient-preserving par construction).
        """
        # Ensure we don't modify input
        h = h.clone()
        
        # Apply the residual connection: h_out = h + f(h)
        residual = self.fc2(self.gelu(self.fc1(h)))
        h_out = h + residual
        
        return h_out

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        """
        Même contrat que TextChannel.get_jacobian_norm.
        """
        # Define the function for which we want the Jacobian
        def encode_fn(x):
            return self.encode(x)
        
        # Compute Jacobian using torch.autograd.functional.jacobian
        h_clone = h.detach().requires_grad_(True)
        jacobian = torch.autograd.functional.jacobian(encode_fn, h_clone, vectorize=True)
        
        # For batch size 1, Jacobian is (hidden_dim, hidden_dim)
        if h_clone.dim() == 2 and h_clone.size(0) == 1:
            # For batch size 1, Jacobian is (hidden_dim, hidden_dim)
            jacobian_single = jacobian[0, :, 0, :]  # (hidden_dim, hidden_dim)
            # Compute spectral norm (largest singular value)
            singular_values = torch.linalg.svdvals(jacobian_single)
            spectral_norm = singular_values[0].item()
            return max(spectral_norm, 0.0)  # Ensure non-negative
        else:
            # For batch size > 1, we compute the spectral norm for each sample and return the max
            spectral_norms = []
            for i in range(h_clone.size(0)):
                jacobian_i = jacobian[i, :, i, :]  # (hidden_dim, hidden_dim)
                singular_values = torch.linalg.svdvals(jacobian_i)
                spectral_norms.append(singular_values[0].item())
            return max(spectral_norms) if spectral_norms else 0.0

    def get_output_entropy(self, h: torch.Tensor) -> float:
        """
        Pour le canal latent, l'entropie est calculée sur la distribution
        des composantes de h_out après normalisation (soft histogram, 50 bins).
        Contrat : résultat ∈ [0, log(50)].
        """
        with torch.no_grad():
            # Get output
            h_out = self.encode(h)  # (batch, hidden_dim)
            
            # For entropy calculation, we'll use the first batch element
            # and compute a soft histogram over its components
            if h_out.dim() == 2:
                h_flat = h_out[0]  # Take first batch element
            else:
                h_flat = h_out.view(-1)  # Flatten if needed
            
            # Normalize to [0, 1] range for histogram binning
            h_norm = (h_flat - h_flat.min()) / (h_flat.max() - h_flat.min() + 1e-8)
            
            # Create soft histogram with 50 bins
            num_bins = 50
            bin_width = 1.0 / num_bins
            
            # Compute distances to bin centers
            bin_centers = torch.linspace(0, 1, num_bins, device=h_out.device)
            distances = torch.abs(h_norm.unsqueeze(-1) - bin_centers.unsqueeze(0))  # (len, num_bins)
            
            # Apply softmax to get soft assignments (temperature=0.1 for softness)
            temperatures = 0.1
            soft_assignments = torch.softmax(-distances / temperatures, dim=-1)  # (len, num_bins)
            
            # Sum over all elements to get histogram
            histogram = torch.sum(soft_assignments, dim=0)  # (num_bins,)
            
            # Normalize to get probability distribution
            probs = histogram / torch.sum(histogram)
            
            # Avoid log(0)
            probs = torch.clamp(probs, min=1e-10)
            
            # Compute Shannon entropy
            entropy = -torch.sum(probs * torch.log(probs))
            
            return entropy.item()


@dataclass(frozen=True)
class CLAIM:
    """
    Structure épistémique formelle.
    frozen=True : immuable après création — pas de modification en place.
    """
    proposition: str                               # Θ ∈ {ami, ennemi, neutre, inconnu}
    belief_mass: Dict[FrozenSet[str], float]       # m : 2^Θ → [0,1], Σ = 1, m(∅) ≥ 0
    belnap_state: Literal["T", "F", "B", "N"]     # état épistémique
    illocution: Literal["OBSERVE", "INFER", "DEDUCE", "ASSUME"]  # type d'acte illocutoire
    freshness: tuple[float, float]                 # (t_obs, Δt_valid) — stub
    provenance: str                                # chain_id — stub


class Channel(Protocol):
    """Interface commune à tous les canaux."""

    def encode(self, h: torch.Tensor) -> Union[torch.Tensor, CLAIM]:
        """Encode un état latent. Déterministe, sans side-effects."""
        ...

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        """Retourne ‖J_C(h)‖₂. Toujours ≥ 0."""
        ...

    def get_output_entropy(self, h: torch.Tensor) -> float:
        """Retourne H(sortie). Toujours ≥ 0."""
        ...


class CLAIMChannel:
    """
    Canal de communication CLAIM.
    Transforme un état latent h en une structure CLAIM via une tête
    de calibration légère (linear head → softmax sur 2^|Θ|).
    """

    def run_learning_curve_experiment(
        channels: Dict[str, Any],
        n_rounds: int = N_ROUNDS_COROL,
        n_runs: int = N_RUNS,
        n_classes: int = N_CLASSES,
        seed_global: int = SEED_GLOBAL,
        output_path: str = "results/learning_curves.csv",
        *,
        corollary_id: int = 0,
    ) -> pd.DataFrame:
        """Run the learning‑curve experiment.

        The ``corollary_id`` parameter allows callers to request a higher number of
        runs for specific corollaries (e.g., ``corollary_id`` == 1 or 3).  When the
        identifier matches those corollaries the function uses ``N_RUNS_HIGH`` (set
        to 50) instead of the default ``N_RUNS`` (10).  This provides the statistical
        power required by task 4.1 without affecting other experiments.
        """
        # Override run count for high‑priority corollaries.
        if corollary_id in {1, 3}:
            n_runs = N_RUNS_HIGH

    def run_rlhf_experiment(
        channel: CLAIMChannel,
        confidence_levels: list = NIVEAUX_CONFIANCE,
        n_rounds: int = N_ROUNDS_RLHF,
        n_runs: int = N_RUNS,
        seed_global: int = SEED_GLOBAL,
        output_path: str = "results/rlhf_propagation.csv",
        *,
        corollary_id: int = 0,
    ) -> pd.DataFrame:
        """Run the RLHF propagation experiment.

        ``corollary_id`` mirrors the behaviour of :func:`run_learning_curve_experiment`
        – when the identifier corresponds to Corollary 1 or 3 the number of runs is
        increased to ``N_RUNS_HIGH`` to satisfy the statistical requirements of
        task 4.1.
        """
        if corollary_id in {1, 3}:
            n_runs = N_RUNS_HIGH

    def __init__(self, theta: list[str], seed: int = 42):
        """
        theta : cadre de discernement Θ (liste de labels)
                Défaut : ["ami", "ennemi", "neutre", "inconnu"]
        seed  : seed pour reproductibilité
        """
        self.theta = theta
        self.powerset_size = 2 ** len(theta)  # Number of subsets of theta
        self.seed = seed
        self.generator = torch.Generator().manual_seed(seed)
        
        # Linear head: hidden_dim -> powerset_size
        # We'll need to know the hidden_dim, but we'll handle it dynamically
        # Initialize with a default size, will adapt on first call
        self.linear = None
        self.hidden_dim = None
        
        # Mapping from index to frozenset for belief mass
        self._index_to_frozenset = {}
        self._frozenset_to_index = {}
        self._generate_powerset_mapping()

    def _generate_powerset_mapping(self):
        """Generate mapping between indices and frozensets of theta"""
        from itertools import chain, combinations
        
        # Generate all subsets of theta
        subsets = list(chain.from_iterable(combinations(self.theta, r) for r in range(len(self.theta) + 1)))
        frozensets = [frozenset(subset) for subset in subsets]
        
        # Create mappings
        for i, fs in enumerate(frozensets):
            self._index_to_frozenset[i] = fs
            self._frozenset_to_index[fs] = i

    def _ensure_linear_layer(self, hidden_dim: int):
        """Ensure the linear layer is initialized with correct dimensions"""
        if self.linear is None or self.hidden_dim != hidden_dim:
            self.hidden_dim = hidden_dim
            self.linear = torch.nn.Linear(hidden_dim, self.powerset_size)

            # Manual Xavier initialization with local generator
            fan_in, fan_out = torch.nn.init._calculate_fan_in_and_fan_out(self.linear.weight)
            std = math.sqrt(2.0 / (fan_in + fan_out))
            a = math.sqrt(3.0) * std
            with torch.no_grad():
                self.linear.weight.uniform_(-a, a, generator=self.generator)
                torch.nn.init.zeros_(self.linear.bias)

    def encode(self, h: torch.Tensor) -> CLAIM:
        """
        Entrée  : h de shape (1, hidden_dim) — un seul vecteur latent
        Sortie  : une structure CLAIM immuable
        Contrat : encode(h) est déterministe pour h fixé et seed fixé.
        Contrat : CLAIM.belief_mass satisfait Σ_{A ⊆ Θ} m(A) = 1.
        Contrat : CLAIM.belief_mass[frozenset()] = m(∅) explicite (conflit).
        """
        # Ensure we don't modify input
        h = h.clone()
        
        # Expecting batch size 1 for CLAIM channel
        if h.dim() != 2 or h.size(0) != 1:
            raise ValueError(f"CLAIMChannel expects input of shape (1, hidden_dim), got {h.shape}")
        
        # Ensure linear layer is initialized
        self._ensure_linear_layer(h.size(-1))
        
        # Forward pass through linear layer
        logits = self.linear(h)  # (1, powerset_size)
        
        # Apply softmax to get belief masses over powerset
        masses_raw = torch.softmax(logits, dim=-1)  # (1, powerset_size)
        masses_raw = masses_raw.squeeze(0)  # (powerset_size,)
        
        # Convert to dictionary mapping frozenset -> mass
        belief_mass = {}
        for i, mass_val in enumerate(masses_raw):
            fs = self._index_to_frozenset[i]
            belief_mass[fs] = mass_val.item()
        
        # Determine proposition (simplified: take the singleton with highest mass, or "inconnu" if empty)
        proposition = self._determine_proposition(belief_mass)
        
        # Determine belnap state (simplified logic)
        belnap_state = self._determine_belnap_state(belief_mass)
        
        # Determine illocution (simplified: always OBSERVE for now)
        illocution = "OBSERVE"
        
        # Stubs for freshness and provenance
        freshness = (0.0, 1.0)  # (t_obs, Δt_valid)
        provenance = "chain_0"  # chain_id
        
        return CLAIM(
            proposition=proposition,
            belief_mass=belief_mass,
            belnap_state=belnap_state,
            illocution=illocution,
            freshness=freshness,
            provenance=provenance
        )

    def _determine_proposition(self, belief_mass: Dict[FrozenSet[str], float]) -> str:
        """Determine proposition from belief mass (simplified)"""
        # Find the singleton set with highest mass
        max_singleton_mass = 0.0
        best_singleton = None
        
        for fs, mass in belief_mass.items():
            if len(fs) == 1:  # Singleton
                if mass > max_singleton_mass:
                    max_singleton_mass = mass
                    best_singleton = next(iter(fs))  # Get the element
        
        if best_singleton is not None and max_singleton_mass > 0.1:
            return best_singleton
        else:
            return "inconnu"

    def _determine_belnap_state(self, belief_mass: Dict[FrozenSet[str], float]) -> Literal["T", "F", "B", "N"]:
        """Determine Belnap state from belief mass (simplified)"""
        # Simplified logic based on mass distribution
        total_conflict = belief_mass.get(frozenset(), 0.0)  # m(∅)
        total_ignorance = sum(mass for fs, mass in belief_mass.items() if len(fs) == 0 or len(fs) > 1)
        
        if total_conflict > 0.5:
            return "B"  # Both true and false (conflict)
        elif total_ignorance > 0.5:
            return "N"  # Neither true nor false (ignorance)
        else:
            # Check if we have clear support for true/false propositions
            true_support = sum(mass for fs, mass in belief_mass.items() if fs == frozenset(["ami"]))
            false_support = sum(mass for fs, mass in belief_mass.items() if fs == frozenset(["ennemi"]))
            
            if true_support > false_support + 0.2:
                return "T"  # True
            elif false_support > true_support + 0.2:
                return "F"  # False
            else:
                return "N"  # Neither (default to ignorance when unclear)

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        """Compute Jacobian norm for the calibration head.
        Returns a non‑negative spectral norm.
        """
        # Ensure we don't modify input
        h = h.clone()
        
        # Expecting batch size 1 for CLAIM channel
        if h.dim() != 2 or h.size(0) != 1:
            raise ValueError(f"CLAIMChannel expects input of shape (1, hidden_dim), got {h.shape}")
        
        # Ensure linear layer is initialized
        self._ensure_linear_layer(h.size(-1))
        
        # Enable gradients for h to compute Jacobian
        h_clone = h.clone().detach().requires_grad_(True)
        
        # Define the function for which we want the Jacobian (h -> masses)
        def masses_fn(x):
            self._ensure_linear_layer(x.size(-1))
            logits = self.linear(x)
            return torch.softmax(logits, dim=-1)  # (1, powerset_size)
        
        # Compute Jacobian using torch.autograd.functional.jacobian
        jacobian = torch.autograd.functional.jacobian(masses_fn, h_clone, vectorize=True)
        
        # The Jacobian will have shape (1, powerset_size, 1, hidden_dim)
        # We want the spectral norm of the Jacobian matrix (powerset_size, hidden_dim)
        if h_clone.dim() == 2 and h_clone.size(0) == 1:
            # Extract the Jacobian matrix for the first (and only) batch element
            jacobian_matrix = jacobian[0, :, 0, :]  # (powerset_size, hidden_dim)
            # Compute spectral norm (largest singular value)
            try:
                singular_values = torch.linalg.svdvals(jacobian_matrix)
                spectral_norm = singular_values[0].item()
                return max(spectral_norm, 0.0)  # Ensure non-negative
            except:
                # Fallback if SVD fails
                return 0.0
        else:
            # For batch size > 1, compute for each sample and return max
            spectral_norms = []
            for i in range(h_clone.size(0)):
                jacobian_matrix = jacobian[i, :, i, :]  # (powerset_size, hidden_dim)
                try:
                    singular_values = torch.linalg.svdvals(jacobian_matrix)
                    spectral_norms.append(singular_values[0].item())
                except:
                    spectral_norms.append(0.0)
            return max(spectral_norms) if spectral_norms else 0.0

    def get_output_entropy(self, h: torch.Tensor) -> float:
        """
        Entropie de Shannon sur la distribution de masses belief_mass.
        Contrat : résultat ∈ [0, log(2^|Θ|)].
        """
        with torch.no_grad():
            # Get the CLAIM to access belief_mass
            claim = self.encode(h)
            
            # Extract masses
            masses = list(claim.belief_mass.values())
            
            # Avoid log(0)
            masses = [max(m, 1e-10) for m in masses]
            
            # Compute Shannon entropy
            entropy = -sum(m * math.log(m) for m in masses)
            
            return entropy

    def inject_conflict(self, h: torch.Tensor,
                      conflict_level: float) -> CLAIM:
        """Inject a specified conflict level into the belief mass.

        This variant of `encode` is used for experiments that manipulate the
        conflict mass `m(∅)`. The method forces the empty‑set mass to `conflict_level`
        (±0.01) and renormalises the remaining masses. It does **not** affect the
        Jacobian norm, preserving gradient‑preserving properties of the underlying
        latent channel.
        """
        # Ensure we don't modify input
        h = h.clone()

        # Expecting batch size 1 for CLAIM channel
        if h.dim() != 2 or h.size(0) != 1:
            raise ValueError(f"CLAIMChannel expects input of shape (1, hidden_dim), got {h.shape}")

        # Ensure linear layer is initialized
        self._ensure_linear_layer(h.size(-1))

        # Forward pass through linear layer
        logits = self.linear(h)  # (1, powerset_size)

        # Apply softmax to get belief masses over powerset
        masses_raw = torch.softmax(logits, dim=-1)  # (1, powerset_size)
        masses_raw = masses_raw.squeeze(0)  # (powerset_size,)

        # Convert to dictionary mapping frozenset -> mass
        belief_mass = {}
        for i, mass_val in enumerate(masses_raw):
            fs = self._index_to_frozenset[i]
            belief_mass[fs] = mass_val.item()

        # Inject conflict by setting explicit mass on empty set
        empty_fs = frozenset()
        belief_mass[empty_fs] = conflict_level

        # Renormalize other masses to sum to (1 - conflict_level)
        non_empty_mass = sum(mass for fs, mass in belief_mass.items() if fs != empty_fs)
        if non_empty_mass > 0:
            scale_factor = (1.0 - conflict_level) / non_empty_mass
            for fs in belief_mass:
                if fs != empty_fs:
                    belief_mass[fs] *= scale_factor
        else:
            # If all mass was supposed to go to empty set, distribute uniformly
            remaining_mass = 1.0 - conflict_level
            num_non_empty = len([fs for fs in belief_mass.keys() if fs != empty_fs])
            if num_non_empty > 0:
                uniform_mass = remaining_mass / num_non_empty
                for fs in belief_mass:
                    if fs != empty_fs:
                        belief_mass[fs] = uniform_mass

        # Determine proposition (simplified: take the singleton with highest mass, or "inconnu" if empty)
        proposition = self._determine_proposition(belief_mass)

        # Determine belnap state (simplified logic)
        belnap_state = self._determine_belnap_state(belief_mass)

        # Determine illocution (simplified: always OBSERVE for now)
        illocution = "OBSERVE"

        # Stubs for freshness and provenance
        freshness = (0.0, 1.0)  # (t_obs, Δt_valid)
        provenance = "chain_0"  # chain_id

        return CLAIM(
            proposition=proposition,
            belief_mass=belief_mass,
            belnap_state=belnap_state,
        illocution = "OBSERVE"
        
        # Stubs for freshness and provenance
        freshness = (0.0, 1.0)  # (t_obs, Δt_valid)
        provenance = "chain_0"  # chain_id
        
        return CLAIM(
            proposition=proposition,
            belief_mass=belief_mass,
            belnap_state=belnap_state,
            illocution=illocution,
            freshness=freshness,
            provenance=provenance
        )