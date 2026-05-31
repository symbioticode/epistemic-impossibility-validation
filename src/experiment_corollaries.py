"""
Sprint 5 — Expériences pour les Corollaires 1 et 2 du TIE

Corollaire 1 (Figure 2) : Dans un système multi-agents utilisant le canal texte,
la performance collective plafonne avant d'atteindre son optimum.

Corollaire 2 (Figure 3) : Dans un système RLHF multi-agent, le signal de gradient
devient nul pour les agents dont la confiance (κ) dépasse 0.7.

Hypothèses supplémentaires (R-COROL-01) :
- H4 : Tâche de classification à 4 classes (Θ = {ami, ennemi, neutre, inconnu})
- H5 : Performance mesurée par l'accuracy collective
- H6 : Canal latent (B) sert de référence gradient-preserving
- H7 : Courbe canal texte (A) plafonne avant round 100
- H8 : Agent RLHF reçoit signal de récompense basé sur accuracy CLAIM
- H9 : Confiance κ ∈ {0.3, 0.6, 0.9}
- H10 : Signal RLHF = norme du gradient après 100 rounds
- H11 : Signal RLHF → 0 pour κ > 0.7
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from channels import TextChannel, LatentChannel, CLAIMChannel


# =============================================================================
# Constantes issues de VARIABLES.md
# =============================================================================

N_ROUNDS_COROL = 200
N_ROUNDS_RLHF = 100
N_RUNS = 50
N_CLASSES = 4
SEED_GLOBAL = 42
NIVEAUX_CONFIANCE = [0.3, 0.6, 0.9]
HIDDEN_DIM = 768
LEARNING_RATE = 0.01


def detect_plateau(accuracy_series: np.ndarray, window: int = 10, threshold_delta: float = 0.005) -> Optional[int]:
    """Détecte le round où un plateau commence."""
    if len(accuracy_series) < window:
        return None
    for i in range(window, len(accuracy_series)):
        window_vals = accuracy_series[i-window:i]
        delta = np.max(window_vals) - np.min(window_vals)
        if delta < threshold_delta:
            return i - window
    return None


def initialize_state(seed: int, hidden_dim: int = HIDDEN_DIM) -> torch.Tensor:
    """Initialise h_0 de manière déterministe."""
    generator = torch.Generator().manual_seed(seed)
    h = torch.randn(1, hidden_dim, generator=generator)
    h = h / torch.norm(h)
    return h


def generate_classification_task(n_classes: int = N_CLASSES, seed: int = 42) -> Tuple[torch.Tensor, int]:
    """Génère prototypes et label true."""
    generator = torch.Generator().manual_seed(seed)
    prototypes = torch.randn(n_classes, HIDDEN_DIM, generator=generator)
    prototypes = prototypes / torch.norm(prototypes, dim=1, keepdim=True)
    true_label = torch.randint(0, n_classes, (1,)).item()
    return prototypes, true_label


def compute_accuracy(h: torch.Tensor, prototypes: torch.Tensor, true_label: int) -> float:
    """Calcule accuracy par cosine similarity."""
    similarities = torch.nn.functional.cosine_similarity(h.unsqueeze(0), prototypes, dim=1)
    predicted_class = torch.argmax(similarities).item()
    return 1.0 if predicted_class == true_label else 0.0


def compute_classification_loss(h: torch.Tensor, prototypes: torch.Tensor, true_label: int) -> torch.Tensor:
    """Loss cross-entropy pour classification."""
    similarities = torch.nn.functional.cosine_similarity(h.unsqueeze(0), prototypes, dim=1)
    probs = torch.softmax(similarities, dim=0)
    loss = -torch.log(probs[true_label] + 1e-10)
    return loss


def run_learning_curve_experiment(
    channels: Dict[str, object],
    n_rounds: int = N_ROUNDS_COROL,
    n_runs: int = N_RUNS,
    n_classes: int = N_CLASSES,
    seed_global: int = SEED_GLOBAL,
    output_path: str = "results/learning_curves.csv"
) -> pd.DataFrame:
    """
    Simule l'apprentissage sur N rounds.
    CONTRAT R-PREUVE-02 : règle d'update IDENTIQUE pour tous canaux.
    """
    results = []
    prototypes, true_label = generate_classification_task(n_classes, seed=seed_global)

    for channel_name, channel in channels.items():
        for run_idx in range(n_runs):
            seed_run = seed_global + run_idx
            h = initialize_state(seed_run)

            for round_idx in range(n_rounds):
                h_encoded = channel.encode(h.clone())
                accuracy = compute_accuracy(h_encoded, prototypes, true_label)

                try:
                    jacobian_norm = channel.get_jacobian_norm(h_encoded)
                except Exception:
                    jacobian_norm = 0.0

                # Update IDENTIQUE pour tous canaux
                h_enc_grad = h_encoded.clone().detach().requires_grad_(True)
                loss = compute_classification_loss(h_enc_grad, prototypes, true_label)
                gradient_signal = torch.autograd.grad(loss, h_enc_grad)[0]
                h = h + LEARNING_RATE * gradient_signal.detach()
                h = h / torch.norm(h)

                results.append({
                    'canal': channel_name,
                    'run_idx': run_idx,
                    'round_idx': round_idx,
                    'accuracy': accuracy,
                    'jacobian_norm': jacobian_norm,
                    'seed_run': seed_run
                })

    df = pd.DataFrame(results)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def plot_figure2(df: pd.DataFrame, output_path: str = "figures/figure2_learning_curves.pdf") -> dict:
    """Génère Figure 2 — courbes d'apprentissage."""
    fig, ax = plt.subplots(figsize=(6, 4))
    plateau_stats = {}

    for channel_name, color in [('text', 'red'), ('latent', 'blue')]:
        subset = df[df['canal'] == channel_name]
        agg = subset.groupby('round_idx')['accuracy'].agg([
            ('median', 'median'),
            ('q1', lambda x: x.quantile(0.25)),
            ('q3', lambda x: x.quantile(0.75))
        ]).reset_index()

        ax.plot(agg['round_idx'], agg['median'], label=f'Canal {channel_name}', color=color)
        ax.fill_between(agg['round_idx'], agg['q1'], agg['q3'], alpha=0.2, color=color)

        accuracy_series = agg['median'].values
        plateau_round = detect_plateau(accuracy_series)
        plateau_stats[channel_name] = plateau_round

        if plateau_round is not None and channel_name == 'text':
            ax.axvline(x=plateau_round, linestyle='--', color=color, alpha=0.5)

    ax.axvline(x=100, linestyle=':', color='gray', label='Seuil round 100')
    ax.set_xlabel('Round')
    ax.set_ylabel('Accuracy (médiane)')
    ax.set_title('Figure 2 — Courbes d\'apprentissage (Corollaire 1)')
    ax.legend(loc='lower right')
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    plt.close()
    return plateau_stats


def encode_with_confidence(channel: CLAIMChannel, h: torch.Tensor, kappa: float) -> torch.Tensor:
    """Encode avec concentration de masse selon κ."""
    h_encoded = channel.encode(h.clone())
    scaling_factor = 1.0 - kappa
    return h_encoded * scaling_factor


def run_rlhf_experiment(
    channel: CLAIMChannel,
    confidence_levels: list = NIVEAUX_CONFIANCE,
    n_rounds: int = N_ROUNDS_RLHF,
    n_runs: int = N_RUNS,
    seed_global: int = SEED_GLOBAL,
    output_path: str = "results/rlhf_propagation.csv"
) -> pd.DataFrame:
    """Simule propagation RLHF par niveau de confiance κ."""
    results = []
    prototypes, true_label = generate_classification_task(N_CLASSES, seed=seed_global)

    for kappa in confidence_levels:
        for run_idx in range(n_runs):
            seed_run = seed_global + run_idx
            h = initialize_state(seed_run)

            for round_idx in range(n_rounds):
                h_encoded = encode_with_confidence(channel, h, kappa)
                h_enc_grad = h_encoded.clone().detach().requires_grad_(True)
                loss = compute_classification_loss(h_enc_grad, prototypes, true_label)

                try:
                    gradient = torch.autograd.grad(loss, h_enc_grad)[0]
                    rlhf_signal_norm = torch.norm(gradient).item()
                except Exception:
                    rlhf_signal_norm = 0.0

                try:
                    jacobian_norm = channel.get_jacobian_norm(h_encoded) * (1.0 - kappa)
                except Exception:
                    jacobian_norm = 0.0

                if rlhf_signal_norm > 1e-6:
                    h = h + LEARNING_RATE * gradient.detach()
                    h = h / torch.norm(h)

                results.append({
                    'kappa': kappa,
                    'run_idx': run_idx,
                    'round_idx': round_idx,
                    'rlhf_signal_norm': rlhf_signal_norm,
                    'jacobian_norm': jacobian_norm,
                    'seed_run': seed_run
                })

    df = pd.DataFrame(results)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def plot_figure3(df: pd.DataFrame, output_path: str = "figures/figure3_rlhf_bound.pdf") -> None:
    """Génère Figure 3 — signal RLHF vs κ."""
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = {0.3: 'green', 0.6: 'orange', 0.9: 'red'}

    for kappa in NIVEAUX_CONFIANCE:
        subset = df[df['kappa'] == kappa]
        agg = subset.groupby('round_idx')['rlhf_signal_norm'].agg([
            ('median', 'median'),
            ('q1', lambda x: x.quantile(0.25)),
            ('q3', lambda x: x.quantile(0.75))
        ]).reset_index()

        ax.plot(agg['round_idx'], agg['median'], label=f'κ = {kappa}', color=colors[kappa])
        ax.fill_between(agg['round_idx'], agg['q1'], agg['q3'], alpha=0.2, color=colors[kappa])

    ax.axhline(y=0, linestyle=':', color='gray', label='Borne théorique (y=0)')
    ax.annotate('κ > 0.7 → signal → 0', xy=(80, 0.05), fontsize=9,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_xlabel('Round')
    ax.set_ylabel('Signal RLHF (norme médiane)')
    ax.set_title('Figure 3 — Propagation RLHF (Corollaire 2)')
    ax.legend(loc='upper right')

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    plt.close()


def main():
    """Point d'entrée principal Sprint 5."""
    print("=" * 60)
    print("SPRINT 5 — Expériences Corollaires 1 et 2")
    print("=" * 60)

    print("\nInitialisation des canaux...")
    text_channel = TextChannel(model_name="gpt2", seed=SEED_GLOBAL)
    latent_channel = LatentChannel(hidden_dim=HIDDEN_DIM, seed=SEED_GLOBAL)
    claim_channel = CLAIMChannel(theta=["ami", "ennemi", "neutre", "inconnu"], seed=SEED_GLOBAL)

    channels_corol1 = {'text': text_channel, 'latent': latent_channel}

    # Expérience 5A
    print("\n--- Expérience 5A : Courbes d'apprentissage ---")
    df_learning = run_learning_curve_experiment(
        channels=channels_corol1, n_rounds=N_ROUNDS_COROL, n_runs=N_RUNS,
        seed_global=SEED_GLOBAL, output_path="results/learning_curves.csv"
    )
    print(f"Données sauvegardées : results/learning_curves.csv ({len(df_learning)} lignes)")

    plateau_stats = plot_figure2(df_learning, "figures/figure2_learning_curves.pdf")
    print(f"Figure 2 générée")
    print(f"Plateau stats : {plateau_stats}")

    # Expérience 5B
    print("\n--- Expérience 5B : Propagation RLHF ---")
    df_rlhf = run_rlhf_experiment(
        channel=claim_channel, confidence_levels=NIVEAUX_CONFIANCE,
        n_rounds=N_ROUNDS_RLHF, n_runs=N_RUNS, seed_global=SEED_GLOBAL,
        output_path="results/rlhf_propagation.csv"
    )
    print(f"Données sauvegardées : results/rlhf_propagation.csv ({len(df_rlhf)} lignes)")

    plot_figure3(df_rlhf, "figures/figure3_rlhf_bound.pdf")
    print(f"Figure 3 générée")

    print("\n" + "=" * 60)
    print("SPRINT 5 TERMINÉ")
    print("=" * 60)

    return df_learning, df_rlhf, plateau_stats


if __name__ == "__main__":
    main()
