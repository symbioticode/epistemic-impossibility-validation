import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict
import torch
from src.channels import Channel


def compute_summary_stats(
    df: pd.DataFrame,
    groupby: List[str] = ["canal", "entropy_level"]
) -> pd.DataFrame:
    """
    Calcule pour chaque groupe : médiane, IQR, min, max, count de jacobian_norm.
    """
    def iqr(x):
        return np.percentile(x, 75) - np.percentile(x, 25)

    summary = df.groupby(groupby)["jacobian_norm"].agg([
        "median",
        iqr,
        "min",
        "max",
        "count"
    ]).reset_index()

    summary["iqr_ratio"] = summary["iqr"] / (summary["median"] + 1e-8)

    return summary


def check_variance_criterion(
    summary: pd.DataFrame,
    threshold_iqr_ratio: float = 0.30
) -> List[Dict]:
    """
    Retourne les groupes où IQR > 30% de la médiane (R-STAT-02).
    """
    problematic = summary[summary["iqr_ratio"] > threshold_iqr_ratio]
    return problematic.to_dict("records")


def run_statistical_tests(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Test de Mann-Whitney U entre Canal A vs B et A vs C.
    """
    results = []

    entropy_levels = df["entropy_level"].unique()

    for entropy in entropy_levels:
        df_ent = df[df["entropy_level"] == entropy]

        data_a = df_ent[df_ent["canal"] == "text"]["jacobian_norm"].dropna().values
        data_b = df_ent[df_ent["canal"] == "latent"]["jacobian_norm"].dropna().values
        data_c = df_ent[df_ent["canal"] == "claim"]["jacobian_norm"].dropna().values

        # A vs B
        if len(data_a) > 0 and len(data_b) > 0:
            stat, p = stats.mannwhitneyu(data_a, data_b, alternative='two-sided')
            r = 1 - (2 * stat / (len(data_a) * len(data_b)))

            results.append({
                "comparison": "A_vs_B",
                "entropy_level": entropy,
                "statistic": stat,
                "p_value": p,
                "effect_size": r,
                "significant": p < 0.05
            })

        # A vs C
        if len(data_a) > 0 and len(data_c) > 0:
            stat, p = stats.mannwhitneyu(data_a, data_c, alternative='two-sided')
            r = 1 - (2 * stat / (len(data_a) * len(data_c)))

            results.append({
                "comparison": "A_vs_C",
                "entropy_level": entropy,
                "statistic": stat,
                "p_value": p,
                "effect_size": r,
                "significant": p < 0.05
            })

    return pd.DataFrame(results)


def verify_reproducibility(
    channel: Channel,
    entropy_level: float = 0.05,
    n_runs: int = 5,
    seed_global: int = 42
) -> bool:
    """
    Exécute deux fois la mesure sur les mêmes 5 runs.
    """
    from src.experiment import generate_latent_with_entropy

    results1 = []
    results2 = []

    # Run 1
    for run_idx in range(n_runs):
        h = generate_latent_with_entropy(entropy_level, seed_global=seed_global, run_idx=run_idx)
        results1.append(channel.get_jacobian_norm(h))

    # Run 2
    for run_idx in range(n_runs):
        h = generate_latent_with_entropy(entropy_level, seed_global=seed_global, run_idx=run_idx)
        results2.append(channel.get_jacobian_norm(h))

    for r1, r2 in zip(results1, results2):
        if abs(r1 - r2) > 1e-6:
            return False

    return True


if __name__ == "__main__":
    import os

    # Task 2.3
    if os.path.exists("results/raw_results.csv"):
        print("Analyzing raw results...")
        df_raw = pd.read_csv("results/raw_results.csv")
        summary = compute_summary_stats(df_raw)
        print("\nSummary Statistics:")
        print(summary)

        problematic = check_variance_criterion(summary)
        if problematic:
            print("\nWARNING: High variance detected in groups:")
            for p in problematic:
                print(f"  - {p['canal']} at entropy {p['entropy_level']}: IQR ratio {p['iqr_ratio']:.4f}")
        else:
            print("\nVariance criterion satisfied for all groups (IQR <= 30% of median).")

        stats_df = run_statistical_tests(df_raw)
        print("\nStatistical Tests (Mann-Whitney U):")
        print(stats_df)

    # Task 2.4 Verification of reproducibility
    print("\nVerifying reproducibility...")
    from src.channels import TextChannel, LatentChannel, CLAIMChannel
    from src.variables_loader import load_variables
    vars = load_variables()

    channels_to_verify = [
        TextChannel(seed=vars["SEED_GLOBAL"]),
        LatentChannel(seed=vars["SEED_GLOBAL"]),
        CLAIMChannel(theta=["ami", "ennemi", "neutre", "inconnu"], seed=vars["SEED_GLOBAL"])
    ]

    all_reproducible = True
    for ch in channels_to_verify:
        name = ch.__class__.__name__
        repro = verify_reproducibility(ch, seed_global=vars["SEED_GLOBAL"])
        print(f"  - {name}: {'REPRODUCIBLE' if repro else 'NOT REPRODUCIBLE'}")
        if not repro:
            all_reproducible = False

    if all_reproducible:
        print("\nReproduction verification PASSED.")
    else:
        print("\nReproduction verification FAILED.")
