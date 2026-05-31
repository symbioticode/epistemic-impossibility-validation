"""
analysis.py — Sprint 2 Tâche 2.3 : Analyse statistique intermédiaire
Implémente compute_summary_stats, check_variance_criterion, run_statistical_tests.
Source : SPRINT-2-context.md §Tâche 2.3
"""

import pandas as pd
import numpy as np
from scipy import stats


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
    Si non vide → logguer QO-S2-02 et augmenter N à 100.
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
    R-STAT-01 : inclure p-value + rank-biserial r (effect size).
    """
    rows = []
    for entropy_level in sorted(df["entropy_level"].unique()):
        sub = df[df["entropy_level"] == entropy_level]
        for canal_b in ["latent", "claim"]:
            a_vals = sub[sub["canal"] == "text"]["jacobian_norm"].dropna()
            b_vals = sub[sub["canal"] == canal_b]["jacobian_norm"].dropna()
            if len(a_vals) < 2 or len(b_vals) < 2:
                continue
            stat, pval = stats.mannwhitneyu(a_vals, b_vals, alternative="two-sided")
            # Rank-biserial r = 2U / (n1*n2) - 1
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


if __name__ == "__main__":
    import os
    path = "results/raw_results.csv"
    if not os.path.exists(path):
        print(f"❌ {path} introuvable — lancer experiment.py d'abord")
        exit(1)

    df = pd.read_csv(path)
    print(f"Chargé {len(df)} lignes depuis {path}\n")

    print("── Statistiques par canal / entropie ──")
    summary = compute_summary_stats(df)
    print(summary.to_string(index=False))

    print("\n── Critère variance (IQR > 30% médiane) ──")
    problematic = check_variance_criterion(summary)
    if problematic:
        print(f"⚠️  QO-S2-02 : {len(problematic)} groupe(s) à variance élevée → N→100")
        for g in problematic:
            print(f"   {g}")
    else:
        print("✅ Tous les groupes dans les limites")

    print("\n── Tests statistiques Mann-Whitney U ──")
    tests = run_statistical_tests(df)
    print(tests.to_string(index=False))
    sig = tests[tests["significant"]]
    print(f"\n✅ {len(sig)}/{len(tests)} comparaisons significatives (p < 0.05)")
