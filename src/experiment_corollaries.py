"""
Sprint 5 — Expériences pour les Corollaires 1 et 2 du TIE
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, Any
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from channels import TextChannel, LatentChannel, CLAIMChannel


# =============================================================================
# Constantes issues de VARIABLES.md
# =============================================================================

N_ROUNDS_COROL = 50
N_ROUNDS_RLHF = 30
N_RUNS = 10
# High‑priority run count for Corollary 1 and 3 (task 4.1)
N_RUNS_HIGH = 50
N_CLASSES = 4
SEED_GLOBAL = 42
NIVEAUX_CONFIANCE = [0.3, 0.6, 0.9]
HIDDEN_DIM = 768
LEARNING_RATE = 0.05


def detect_plateau(accuracy_series: np.ndarray, window: int = 5, threshold_delta: float = 0.01) -> Optional[int]:
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
    similarities = torch.nn.functional.cosine_similarity(h, prototypes, dim=1)
    predicted_class = torch.argmax(similarities).item()
    return 1.0 if predicted_class == true_label else 0.0


def compute_classification_loss(h: torch.Tensor, prototypes: torch.Tensor, true_label: int) -> torch.Tensor:
    """Loss cross-entropy pour classification."""
    similarities = torch.nn.functional.cosine_similarity(h, prototypes, dim=1)
    probs = torch.softmax(similarities * 5, dim=0)
    loss = -torch.log(probs[true_label] + 1e-10)
    return loss


def encode_with_confidence_soft(channel: CLAIMChannel, h: torch.Tensor, kappa: float) -> torch.Tensor:
    """Version différentiable simplifiée."""
    channel._ensure_linear_layer(h.size(-1))
    logits = channel.linear(h)
    masses = torch.softmax(logits, dim=-1)

    if kappa <= 0:
        return masses

    with torch.no_grad():
        singleton_indices = [channel._frozenset_to_index[frozenset([label])] for label in channel.theta]
        singleton_masses = masses[0, singleton_indices]
        max_idx_in_singletons = torch.argmax(singleton_masses)
        max_idx = singleton_indices[max_idx_in_singletons]

    if kappa > 0.7:
        res = torch.zeros_like(masses)
        res[0, max_idx] = 1.0
        return res.detach()

    m_max = masses[0, max_idx]
    other_sum = 1.0 - m_max
    mask = torch.ones_like(masses)
    mask[0, max_idx] = 0
    new_masses = masses * (1.0 - kappa) / (other_sum + 1e-10) * mask
    k_tensor = torch.zeros_like(masses)
    k_tensor[0, max_idx] = kappa
    return new_masses + k_tensor


def get_soft_output(channel: Any, h: torch.Tensor) -> torch.Tensor:
    if isinstance(channel, LatentChannel):
        return channel.encode(h)
    elif isinstance(channel, TextChannel):
        logits = torch.matmul(h, channel.model.wte.weight.T)
        probs = torch.softmax(logits, dim=-1)
        return torch.matmul(probs, channel.model.wte.weight)
    elif isinstance(channel, CLAIMChannel):
        return encode_with_confidence_soft(channel, h, 0.0)
    return h


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
    """Run learning curve experiment with optional high‑priority run count.

    If ``corollary_id`` is 1 or 3 (the corollaries targeted by task 4.1), the number of
    runs is increased to ``N_RUNS_HIGH`` (50) to improve statistical power.
    """
    if corollary_id in {1, 3}:
        n_runs = N_RUNS_HIGH
    results = []
    prototypes, true_label = generate_classification_task(n_classes, seed=seed_global)

    for channel_name, channel in channels.items():
        print(f"  Simulation canal : {channel_name}")
        for run_idx in range(n_runs):
            seed_run = seed_global + run_idx
            h = initialize_state(seed_run)

            for round_idx in range(n_rounds):
                with torch.no_grad():
                    h_encoded = channel.encode(h.clone())
                    accuracy = compute_accuracy(h_encoded, prototypes, true_label)

                h_for_grad = h.clone().detach().requires_grad_(True)
                h_soft = get_soft_output(channel, h_for_grad)
                loss = compute_classification_loss(h_soft, prototypes, true_label)

                try:
                    grads = torch.autograd.grad(loss, h_for_grad)
                    gradient_signal = grads[0].detach() if grads[0] is not None else torch.zeros_like(h)
                except Exception:
                    gradient_signal = torch.zeros_like(h)

                h = h - LEARNING_RATE * gradient_signal
                h = h / (torch.norm(h) + 1e-10)

                results.append({
                    'canal': channel_name, 'run_idx': run_idx, 'round_idx': round_idx,
                    'accuracy': accuracy, 'seed_run': seed_run
                })

    df = pd.DataFrame(results)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def plot_figure2(df: pd.DataFrame, output_path: str = "figures/figure2_learning_curves.pdf") -> dict:
    fig, ax = plt.subplots(figsize=(6, 4))
    plateau_stats = {}
    for channel_name, color in [('text', 'red'), ('latent', 'blue')]:
        subset = df[df['canal'] == channel_name]
        agg = subset.groupby('round_idx')['accuracy'].agg([('median', 'median'), ('q1', lambda x: x.quantile(0.25)), ('q3', lambda x: x.quantile(0.75))]).reset_index()
        ax.plot(agg['round_idx'], agg['median'], label=f'Canal {channel_name}', color=color)
        ax.fill_between(agg['round_idx'], agg['q1'], agg['q3'], alpha=0.2, color=color)
        plateau_stats[channel_name] = detect_plateau(agg['median'].values)
    ax.set_xlabel('Round')
    ax.set_ylabel('Accuracy (médiane)')
    ax.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    plt.close()
    return plateau_stats


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
    """Run RLHF propagation experiment with optional high‑priority run count.

    For ``corollary_id`` 1 or 3, ``n_runs`` is overridden to ``N_RUNS_HIGH``.
    """
    if corollary_id in {1, 3}:
        n_runs = N_RUNS_HIGH
    results = []
    for kappa in confidence_levels:
        print(f"  Simulation κ = {kappa}")
        for run_idx in range(n_runs):
            seed_run = seed_global + run_idx
            # Prototypes changent par run pour éviter de stagner sur une tâche facile
            prototypes, true_label = generate_classification_task(N_CLASSES, seed=seed_run)
            true_singleton_idx = channel._frozenset_to_index[frozenset([channel.theta[true_label]])]

            # h0 aléatoire décalé
            generator = torch.Generator().manual_seed(seed_run + 1000)
            h = torch.randn(1, HIDDEN_DIM, generator=generator)
            h = h / torch.norm(h)

            for round_idx in range(n_rounds):
                h_for_grad = h.clone().detach().requires_grad_(True)
                # Passage par le canal (potentiellement détaché si kappa > 0.7)
                masses = encode_with_confidence_soft(channel, h_for_grad, kappa)

                # Calcul du signal RLHF (norme du gradient)
                loss = -torch.log(masses[0, true_singleton_idx] + 1e-10)
                try:
                    grads = torch.autograd.grad(loss, h_for_grad)
                    gradient = grads[0] if grads[0] is not None else torch.zeros_like(h)
                    rlhf_signal_norm = torch.norm(gradient).item()
                except Exception:
                    effective_gradient = torch.zeros_like(h)
                    rlhf_signal_norm = 0.0
                    gradient = torch.zeros_like(h)

                # Mesure du Jacobien (indépendant de la tâche)
                try:
                    if kappa > 0.7:
                        jacobian_norm = 0.0
                    else:
                        def soft_fn(x): return encode_with_confidence_soft(channel, x, kappa)
                        # On utilise autograd.functional.jacobian sur h pour mesurer J_C(h)
                        jacobian = torch.autograd.functional.jacobian(soft_fn, h.clone().detach(), vectorize=True)
                        jacobian_matrix = jacobian[0, :, 0, :]
                        jacobian_norm = torch.linalg.svdvals(jacobian_matrix)[0].item()
                except Exception:
                    jacobian_norm = 0.0

                # Apprentissage RLHF : mise à jour de h si signal présent
                if rlhf_signal_norm > 1e-10:
                    # On utilise h_for_grad.detach() ou juste h ? h est le state persistant.
                    h = h.detach() - LEARNING_RATE * gradient.detach()
                    h = h / (torch.norm(h) + 1e-10)

                results.append({
                    'kappa': kappa, 'run_idx': run_idx, 'round_idx': round_idx,
                    'rlhf_signal_norm': rlhf_signal_norm, 'jacobian_norm': jacobian_norm, 'seed_run': seed_run
                })
    df = pd.DataFrame(results)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


# ---------------------------------------------------------------------------
# CIFAR-10 classification experiment (Task 4.2)
# ---------------------------------------------------------------------------

def run_cifar10_classification_experiment(
    channel: TextChannel,
    epochs: int = 5,
    batch_size: int = 64,
    seed_global: int = SEED_GLOBAL,
    output_path: str = "results/cifar10_experiment.csv",
) -> pd.DataFrame:
    """Simple CIFAR‑10 experiment using the provided ``channel``.

    Images are encoded to the hidden dimension, passed through ``channel.encode``,
    and a linear probe is trained to predict the 10 classes.  The function returns
    a DataFrame with the final test accuracy.
    """
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader

    torch.manual_seed(seed_global)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    train_set = datasets.CIFAR10(root="./data", train=True, download=True, transform=transform)
    test_set = datasets.CIFAR10(root="./data", train=False, download=True, transform=transform)
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False)

    class ImageEncoder(nn.Module):
        def __init__(self, hidden_dim: int = HIDDEN_DIM):
            super().__init__()
            self.conv = nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1)),
            )
            self.fc = nn.Linear(64, hidden_dim)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = self.conv(x)
            x = x.view(x.size(0), -1)
            return self.fc(x)

    encoder = ImageEncoder().eval()
    for p in encoder.parameters():
        p.requires_grad = False

    probe = nn.Linear(HIDDEN_DIM, 10)
    optimizer = optim.Adam(probe.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        probe.train()
        for imgs, labels in train_loader:
            with torch.no_grad():
                latent = encoder(imgs)
                channel_out = channel.encode(latent)
            optimizer.zero_grad()
            logits = probe(channel_out)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

    # Evaluation
    probe.eval()
    correct = total = 0
    with torch.no_grad():
        for imgs, labels in test_loader:
            latent = encoder(imgs)
            channel_out = channel.encode(latent)
            logits = probe(channel_out)
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    accuracy = correct / total
    df = pd.DataFrame([{"seed": seed_global, "accuracy": accuracy}])
    _os.makedirs(_os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ CIFAR‑10 experiment completed – accuracy={accuracy:.4f} → {output_path}")
    return df

def plot_figure3(df: pd.DataFrame, output_path: str = "figures/figure3_rlhf_bound.pdf") -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = {0.3: 'green', 0.6: 'orange', 0.9: 'red'}
    for kappa in NIVEAUX_CONFIANCE:
        subset = df[df['kappa'] == kappa]
        agg = subset.groupby('round_idx')['rlhf_signal_norm'].agg([('median', 'median'), ('q1', lambda x: x.quantile(0.25)), ('q3', lambda x: x.quantile(0.75))]).reset_index()
        ax.plot(agg['round_idx'], agg['median'], label=f'κ = {kappa}', color=colors[kappa])
        ax.fill_between(agg['round_idx'], agg['q1'], agg['q3'], alpha=0.2, color=colors[kappa])
    ax.set_xlabel('Round')
    ax.set_ylabel('Signal RLHF')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, format='pdf')
    plt.close()


def main():
    print("Initialisation...")
    text_channel = TextChannel(model_name="gpt2", seed=SEED_GLOBAL)
    latent_channel = LatentChannel(hidden_dim=HIDDEN_DIM, seed=SEED_GLOBAL)
    claim_channel = CLAIMChannel(theta=["ami", "ennemi", "neutre", "inconnu"], seed=SEED_GLOBAL)
    df_learning = run_learning_curve_experiment({'text': text_channel, 'latent': latent_channel})
    plot_figure2(df_learning)
    df_rlhf = run_rlhf_experiment(claim_channel)
    plot_figure3(df_rlhf)
    print("Fini.")


if __name__ == "__main__":
    main()
