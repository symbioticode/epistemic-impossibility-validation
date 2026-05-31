import torch
import pandas as pd
import numpy as np
import time
from tqdm import tqdm
from typing import Dict, List
from src.channels import Channel, TextChannel, LatentChannel, CLAIMChannel


def generate_latent_with_entropy(
    entropy_level: float,
    hidden_dim: int = 768,
    seed_global: int = 42,
    run_idx: int = 0
) -> torch.Tensor:
    """
    Génère un vecteur latent h dont la distribution softmax associée
    a une entropie proche de entropy_level.
    """
    seed_run = seed_global * 1000 + run_idx
    generator = torch.Generator().manual_seed(seed_run)

    # Generate random latent vector
    h = torch.randn(1, hidden_dim, generator=generator)

    # Stratégie pour contrôler l'entropie :
    # Plus entropy_level est petit, plus on veut des logits larges (plus de concentration).
    scale = 1.0 / (entropy_level + 1e-5)
    h = h * scale

    return h


def run_experiment(
    channels: Dict[str, Channel],
    entropy_levels: List[float],
    n_runs: int = 500,
    seed_global: int = 42,
    output_path: str = "results/raw_results.csv"
) -> pd.DataFrame:
    """
    Exécute l'expérience complète : 3 canaux × 6 niveaux × 100 runs.
    """
    results = []

    total_iterations = len(channels) * len(entropy_levels) * n_runs
    pbar = tqdm(total=total_iterations, desc="Running main experiment")

    for canal_name, channel in channels.items():
        for entropy_level in entropy_levels:
            for run_idx in range(n_runs):
                seed_run = seed_global * 1000 + run_idx

                start_time = time.time()

                # 1. Generate h
                h = generate_latent_with_entropy(entropy_level, seed_global=seed_global, run_idx=run_idx)

                # 2. Measure Jacobian norm
                try:
                    jacobian_norm = channel.get_jacobian_norm(h)
                except Exception as e:
                    # print(f"Error measuring Jacobian for {canal_name}, entropy {entropy_level}, run {run_idx}: {e}")
                    jacobian_norm = np.nan

                # 3. Measure output entropy
                try:
                    output_entropy = channel.get_output_entropy(h)
                except Exception as e:
                    # print(f"Error measuring Entropy for {canal_name}, entropy {entropy_level}, run {run_idx}: {e}")
                    output_entropy = np.nan

                duration_ms = (time.time() - start_time) * 1000

                # 4. Record result
                results.append({
                    "canal": canal_name,
                    "entropy_level": entropy_level,
                    "run_idx": run_idx,
                    "seed_run": seed_run,
                    "jacobian_norm": jacobian_norm,
                    "output_entropy": output_entropy,
                    "duration_ms": duration_ms
                })

                pbar.update(1)

    pbar.close()

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    return df


def run_conflict_experiment(
    channel_c: CLAIMChannel,
    entropy_levels: List[float],
    conflict_levels: List[float],
    n_runs: int = 500,
    seed_global: int = 42,
    output_path: str = "results/conflict_results.csv"
) -> pd.DataFrame:
    """
    Exécute l'expérience de conflit sur le Canal C.
    """
    results = []

    total_iterations = len(conflict_levels) * len(entropy_levels) * n_runs
    pbar = tqdm(total=total_iterations, desc="Running conflict experiment")

    for conflict_level in conflict_levels:
        for entropy_level in entropy_levels:
            for run_idx in range(n_runs):
                seed_run = seed_global * 1000 + run_idx

                # Generate h
                h = generate_latent_with_entropy(entropy_level, seed_global=seed_global, run_idx=run_idx)

                # Inject conflict and measure
                try:
                    claim = channel_c.inject_conflict(h, conflict_level=conflict_level)
                    m_vide = claim.belief_mass.get(frozenset(), 0.0)

                    jacobian_norm = channel_c.get_jacobian_norm(h)

                    # For entropy, we calculate it on the masses after conflict injection
                    masses = list(claim.belief_mass.values())
                    masses = [max(m, 1e-10) for m in masses]
                    output_entropy = -sum(m * np.log(m) for m in masses)

                except Exception as e:
                    # print(f"Error in conflict experiment: {e}")
                    jacobian_norm = np.nan
                    output_entropy = np.nan
                    m_vide = np.nan

                results.append({
                    "entropy_level": entropy_level,
                    "conflict_level": conflict_level,
                    "run_idx": run_idx,
                    "seed_run": seed_run,
                    "jacobian_norm": jacobian_norm,
                    "output_entropy": output_entropy,
                    "m_vide": m_vide
                })
                pbar.update(1)

    pbar.close()

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    from src.variables_loader import load_variables
    vars = load_variables()

    # Initialize channels
    channels = {
        "text": TextChannel(seed=vars["SEED_GLOBAL"]),
        "latent": LatentChannel(seed=vars["SEED_GLOBAL"]),
        "claim": CLAIMChannel(theta=["ami", "ennemi", "neutre", "inconnu"], seed=vars["SEED_GLOBAL"])
    }

    entropy_levels = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]

    # Tâche 2.1
    print("Starting Task 2.1...")
    df_raw = run_experiment(channels, entropy_levels, n_runs=50, seed_global=vars["SEED_GLOBAL"])

    # Tâche 2.2
    print("Starting Task 2.2...")
    conflict_levels = [0.0, 0.2, 0.5, 0.8]
    df_conflict = run_conflict_experiment(channels["claim"], entropy_levels, conflict_levels, n_runs=50, seed_global=vars["SEED_GLOBAL"])

    print("Experiments completed.")
