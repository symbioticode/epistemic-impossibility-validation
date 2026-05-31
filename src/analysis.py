"""
analysis.py — Sprint 5 : Tests statistiques pour les Corollaires 1 et 2.
"""

import pandas as pd
import numpy as np
from scipy import stats
import os


def compute_summary_stats(
    df: pd.DataFrame,
    groupby: list = ["canal", "entropy_level"],
) -> pd.DataFrame:
    """
    Calcule médiane, IQR, min, max, count de jacobian_norm par groupe.
    """
    def iqr(x):
        return float(np.percentile(x.dropna(), 75) - np.percentile(x.dropna(), 25))

    summary = (
        df.groupby(groupby)["jacobian_norm"]
        .agg(
            median="median",
            iqr=iqr,
            min="min",
            max="max",
            count="count",
        )
        .reset_index()
    )
    summary["iqr_ratio"] = summary["iqr"] / (summary["median"].abs() + 1e-10)
    return summary


def check_variance_criterion(
    summary: pd.DataFrame,
    threshold_iqr_ratio: float = 0.30,
) -> list:
    """
    Retourne les groupes où IQR > 30% de la médiane (R-STAT-02).
    """
    problematic = summary[summary["iqr_ratio"] > threshold_iqr_ratio]
    result = []
    for _, row in problematic.iterrows():
        entry = {"iqr_ratio": round(row["iqr_ratio"], 4)}
        for col in ["canal", "entropy_level", "conflict_level"]:
            if col in row.index:
                entry[col] = row[col]
        result.append(entry)
    return result


def run_statistical_tests(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mann-Whitney U entre canal A vs B et A vs C sur jacobian_norm,
    pour chaque entropy_level.
    """
    rows = []
    if "entropy_level" not in df.columns:
        return pd.DataFrame()

    for entropy_level in sorted(df["entropy_level"].unique()):
        sub = df[df["entropy_level"] == entropy_level]
        for canal_b in ["latent", "claim"]:
            a_vals = sub[sub["canal"] == "text"]["jacobian_norm"].dropna()
            b_vals = sub[sub["canal"] == canal_b]["jacobian_norm"].dropna()
            if len(a_vals) < 2 or len(b_vals) < 2:
                continue
            stat, pval = stats.mannwhitneyu(a_vals, b_vals, alternative="two-sided")
            n1, n2 = len(a_vals), len(b_vals)
            r = (2 * stat / (n1 * n2)) - 1
            rows.append({
                "comparison": f"text_vs_{canal_b}",
                "entropy_level": entropy_level,
                "statistic": round(stat, 4),
                "p_value": round(pval, 6),
                "effect_size_r": round(r, 4),
                "significant": pval < 0.05,
                "n_text": n1,
                f"n_{canal_b}": n2,
            })

    return pd.DataFrame(rows)


def detect_plateau(accuracy_series: np.ndarray, window: int = 5, threshold_delta: float = 0.01) -> int | None:
    """Détecte le round où un plateau commence."""
    if len(accuracy_series) < window:
        return None
    for i in range(window, len(accuracy_series)):
        window_vals = accuracy_series[i-window:i]
        delta = np.max(window_vals) - np.min(window_vals)
        if delta < threshold_delta:
            return i - window
    return None


def test_corollary_1(df_learning: pd.DataFrame) -> dict:
    """
    Test statistique pour Corollaire 1 (plafonnement).
    Compare l'accuracy du Canal A (text) vs Canal B (latent) aux rounds tardifs.
    """
    max_round = df_learning['round_idx'].max()
    late_rounds = df_learning[df_learning['round_idx'] >= max_round * 0.75]

    a_vals = late_rounds[late_rounds['canal'] == 'text']['accuracy']
    b_vals = late_rounds[late_rounds['canal'] == 'latent']['accuracy']

    if len(a_vals) < 2 or len(b_vals) < 2:
        return {"corollary_1_confirmed": False, "error": "insufficient data"}

    # Test Mann-Whitney U (unilatéral : A < B)
    stat, pval = stats.mannwhitneyu(a_vals, b_vals, alternative='less')
    n1, n2 = len(a_vals), len(b_vals)
    r = 1 - (2 * stat / (n1 * n2))

    # Détection de plateau sur la médiane
    agg = df_learning.groupby(['canal', 'round_idx'])['accuracy'].median().reset_index()
    plateau_a = detect_plateau(agg[agg['canal'] == 'text']['accuracy'].values)
    plateau_b = detect_plateau(agg[agg['canal'] == 'latent']['accuracy'].values)

    confirmed = (pval < 0.05) and (plateau_a is not None)

    return {
        "p_value_late": float(pval),
        "effect_size_r": float(r),
        "plateau_round_A": plateau_a,
        "plateau_round_B": plateau_b,
        "corollary_1_confirmed": bool(confirmed)
    }


def test_corollary_2(df_rlhf: pd.DataFrame) -> dict:
    """
    Test statistique pour Corollaire 2 (borne RLHF).
    Compare rlhf_signal_norm entre κ=0.3 et κ=0.9 aux rounds tardifs.
    """
    max_round = df_rlhf['round_idx'].max()
    late_rounds = df_rlhf[df_rlhf['round_idx'] >= max_round * 0.8]

    vals_03 = late_rounds[late_rounds['kappa'] == 0.3]['rlhf_signal_norm']
    vals_09 = late_rounds[late_rounds['kappa'] == 0.9]['rlhf_signal_norm']

    if len(vals_03) < 2 or len(vals_09) < 2:
         return {"corollary_2_confirmed": False, "error": "insufficient data"}

    # Test Mann-Whitney U (unilatéral : 0.9 < 0.3)
    stat, pval = stats.mannwhitneyu(vals_09, vals_03, alternative='less')
    n1, n2 = len(vals_09), len(vals_03)
    r = 1 - (2 * stat / (n1 * n2))

    mean_03 = float(vals_03.mean())
    mean_09 = float(vals_09.mean())

    confirmed = (pval < 0.05) and (mean_09 < 0.01)

    return {
        "p_value": float(pval),
        "effect_size_r": float(r),
        "mean_signal_kappa_03": mean_03,
        "mean_signal_kappa_09": mean_09,
        "corollary_2_confirmed": bool(confirmed)
    }


if __name__ == "__main__":
    # Sprint 2 compatibility
    path_raw = "results/raw_results.csv"
    if os.path.exists(path_raw):
        print(f"--- Analyse Sprint 2 ({path_raw}) ---")
        df_s2 = pd.read_csv(path_raw)
        summary = compute_summary_stats(df_s2)
        print(summary.to_string(index=False))
        tests_s2 = run_statistical_tests(df_s2)
        print(tests_s2.to_string(index=False))

    # Sprint 5
    path_learning = "results/learning_curves.csv"
    path_rlhf = "results/rlhf_propagation.csv"

    if os.path.exists(path_learning):
        print("\n--- Analyse Corollaire 1 (Learning Curves) ---")
        df_learning = pd.read_csv(path_learning)
        res1 = test_corollary_1(df_learning)
        print(res1)
        if res1.get("corollary_1_confirmed"):
            print("✅ Corollaire 1 CONFIRMÉ")
        else:
            print("❌ Corollaire 1 NON CONFIRMÉ")

    if os.path.exists(path_rlhf):
        print("\n--- Analyse Corollaire 2 (RLHF Propagation) ---")
        df_rlhf = pd.read_csv(path_rlhf)
        res2 = test_corollary_2(df_rlhf)
        print(res2)
        if res2.get("corollary_2_confirmed"):
            print("✅ Corollaire 2 CONFIRMÉ")
        else:
            print("❌ Corollaire 2 NON CONFIRMÉ")
