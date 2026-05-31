"""
analysis.py — Sprint 3 & 5 : Figures, tables et tests statistiques.
Génère les figures et tables du papier EIP, ainsi que les tests des corollaires.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os
import json


# ---------- Fonctions communes ----------

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
            # Rank-biserial correlation r = 1 - (2U / (n1*n2))
            r = 1 - (2 * stat / (n1 * n2))
            rows.append({
                "comparison": f"text_vs_{canal_b}",
                "entropy_level": entropy_level,
                "statistic": round(stat, 4),
                "p_value": round(pval, 10),
                "effect_size_r": round(r, 4),
                "significant": pval < 0.05,
                "n_text": n1,
                f"n_{canal_b}": n2,
            })

    return pd.DataFrame(rows)


# ---------- Figure 1 ----------

def plot_figure1(
    df: pd.DataFrame,
    output_path: str = "figures/figure1_gradient_entropy.pdf"
) -> None:
    """
    Génère Figure 1 (Jacobien vs entropie) à partir de raw_results.csv.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    summary = compute_summary_stats(df)

    plt.figure(figsize=(6, 4))

    configs = [
        ("text", "Canal A (texte)", "#1f77b4", "o"),
        ("latent", "Canal B (latent)", "#2ca02c", "s"),
        ("claim", "Canal C (CLAIM)", "#d62728", "^"),
    ]

    for canal, label, color, marker in configs:
        sub = summary[summary["canal"] == canal].sort_values("entropy_level")
        if sub.empty:
            continue

        plt.errorbar(
            sub["entropy_level"],
            sub["median"],
            yerr=sub["iqr"]/2,
            label=label,
            color=color,
            marker=marker,
            capsize=4,
            alpha=0.8,
            elinewidth=1,
            markeredgewidth=1
        )
        # Fill IQR area
        plt.fill_between(
            sub["entropy_level"],
            sub["median"] - sub["iqr"] / 2,
            sub["median"] + sub["iqr"] / 2,
            color=color,
            alpha=0.2
        )

    plt.xscale("log")
    plt.yscale("linear")
    plt.xlabel("Entropy level (log scale)")
    plt.ylabel("Jacobian norm (median ± IQR/2)")
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)

    plt.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close()
    print(f"✅ Figure 1 générée : {output_path}")


# ---------- Tables 1, 2, 3 ----------

def generate_table1(
    df: pd.DataFrame,
    output_path: str = "figures/table1_main_results.md"
) -> None:
    """Génère Table 1 en Markdown."""
    summary = compute_summary_stats(df)
    entropy_levels = sorted(df["entropy_level"].unique())

    lines = [
        "# Table 1 — Jacobian norm par canal et niveau d'entropie (médiane ± IQR)",
        "",
        "| Entropie | Canal A (texte) | Canal B (latent) | Canal C (CLAIM) |",
        "|----------|----------------|-----------------|-----------------|"
    ]

    for ent in entropy_levels:
        row_str = f"| {ent:.2f}     "
        for canal in ["text", "latent", "claim"]:
            sub = summary[(summary["canal"] == canal) & (summary["entropy_level"] == ent)]
            if not sub.empty:
                med = sub.iloc[0]["median"]
                iqr = sub.iloc[0]["iqr"]
                row_str += f"| {med:.4f} ± {iqr:.4f} "
            else:
                row_str += "| N/A             "
        row_str += "|"
        lines.append(row_str)

    lines.append("")
    lines.append(f"*N = 50 runs par cellule. IQR = Q3 − Q1.*")
    lines.append(f"*Valeurs issues de results/raw_results.csv.*")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"✅ Table 1 générée : {output_path}")


def generate_table2(
    df: pd.DataFrame,
    output_path: str = "figures/table2_stats.md"
) -> None:
    """Génère Table 2 en Markdown."""
    tests = run_statistical_tests(df)
    entropy_levels = sorted(df["entropy_level"].unique())

    lines = [
        "# Table 2 — Tests statistiques (Mann-Whitney U, N=50 par groupe)",
        "",
        "| Entropie | A vs B : U | A vs B : p | A vs B : sig. | A vs B : r | A vs C : U | A vs C : p | A vs C : sig. | A vs C : r |",
        "|----------|-----------|-----------|--------------|-----------|-----------|-----------|--------------|-----------|"
    ]

    for ent in entropy_levels:
        row_str = f"| {ent:.2f}     "
        for canal_b in ["latent", "claim"]:
            sub = tests[(tests["entropy_level"] == ent) & (tests["comparison"] == f"text_vs_{canal_b}")]
            if not sub.empty:
                u = sub.iloc[0]["statistic"]
                p = sub.iloc[0]["p_value"]
                r = sub.iloc[0]["effect_size_r"]
                if p < 0.001:
                    sig = "***"
                elif p < 0.01:
                    sig = "**"
                elif p < 0.05:
                    sig = "*"
                else:
                    sig = "ns"
                row_str += f"| {u:.1f} | {p:.4f} | {sig} | {r:.4f} "
            else:
                row_str += "| N/A | N/A | ns | N/A "
        row_str += "|"
        lines.append(row_str)

    lines.append("")
    lines.append("*Significance : *** p<0.001 · ** p<0.01 · * p<0.05 · ns p≥0.05*")
    lines.append("*r = rank-biserial correlation (effect size)*")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"✅ Table 2 générée : {output_path}")


def generate_table3(calibration_data: dict, output_path: str = "figures/table3_calibration.md") -> None:
    """Génère Table 3 en Markdown à partir des données de calibration."""
    lines = [
        "# Table 3 — Résultats de calibration Canal C (γ_i)",
        "",
        "| Paramètre | Valeur |",
        "|-----------|--------|",
        f"| Méthode de calibration | {calibration_data.get('method', 'k-NN (k=5)')} |",
        f"| Corrélation calibration | {calibration_data.get('correlation', 0.0):.4f} |",
        f"| seed_check | {calibration_data.get('seed_check', False)} |",
        f"| N points de référence | {calibration_data.get('n_ref', 0)} |",
        "| Seuil d'alerte (QO-S1-01) | 0.50 |",
        f"| Statut | {'Calibré' if calibration_data.get('is_calibrated', False) else 'Non-calibré'} |",
        "",
        "*Source : résultats de verify_calibration() — Sprint 1.*"
    ]
    if calibration_data.get('correlation', 1.0) < 0.5:
        lines.append(f"*Alerte QO-S1-01 : corrélation < 0.50 ({calibration_data.get('correlation'):.4f})*")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"✅ Table 3 générée : {output_path}")


# ---------- Détection de plateau ----------

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


# ---------- Tests des corollaires ----------

def test_corollary_1(df_learning: pd.DataFrame) -> dict:
    """
    Test statistique pour Corollaire 1 (supériorité du canal latent).
    Compare les accuracy du canal texte vs latent aux rounds tardifs.
    """
    max_round = df_learning['round_idx'].max()
    late_rounds = df_learning[df_learning['round_idx'] >= max_round * 0.75]

    a_vals = late_rounds[late_rounds['canal'] == 'text']['accuracy']
    b_vals = late_rounds[late_rounds['canal'] == 'latent']['accuracy']

    if len(a_vals) < 2 or len(b_vals) < 2:
        return {"corollary_1_confirmed": False, "error": "insufficient data"}

    stat, pval = stats.mannwhitneyu(a_vals, b_vals, alternative='less')
    n1, n2 = len(a_vals), len(b_vals)
    r = 1 - (2 * stat / (n1 * n2))

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


# ---------- Point d'entrée principal ----------

if __name__ == "__main__":
    # Sprint 3 : génération des figures et tables à partir des résultats bruts
    path_raw = "results/raw_results.csv"
    if not os.path.exists(path_raw):
        print(f"❌ {path_raw} introuvable. Lancez d'abord l'expérience.")
        exit(1)

    print("--- Analyse Sprint 3 (raw_results.csv) ---")
    df_raw = pd.read_csv(path_raw)
    plot_figure1(df_raw)
    generate_table1(df_raw)
    generate_table2(df_raw)

    # Table 3 nécessite le fichier de calibration
    path_calib = "results/calibration_summary.json"
    if os.path.exists(path_calib):
        with open(path_calib, "r") as f:
            calib_data = json.load(f)
        generate_table3(calib_data)
    else:
        print("⚠️ Fichier calibration_summary.json absent. Table 3 non générée.")

    # Vérification du critère de variance
    summary = compute_summary_stats(df_raw)
    print("\n── Critère variance (IQR > 30% médiane) ──")
    problematic = check_variance_criterion(summary)
    if problematic:
        print(f"⚠️ QO-S2-02 : {len(problematic)} groupe(s) à variance élevée → N→100")
        for g in problematic:
            print(f"   {g}")
    else:
        print("✅ Tous les groupes dans les limites")

    # Tests statistiques Mann-Whitney
    print("\n── Tests statistiques Mann-Whitney U ──")
    tests = run_statistical_tests(df_raw)
    print(tests.to_string(index=False))
    sig = tests[tests["significant"]]
    print(f"\n✅ {len(sig)}/{len(tests)} comparaisons significatives (p < 0.05)")

    # Sprint 5 : tests des corollaires sur learning_curves.csv et rlhf_propagation.csv
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
        print("\n--- Analyse Corollaire 2 (RLHF) ---")
        df_rlhf = pd.read_csv(path_rlhf)
        res2 = test_corollary_2(df_rlhf)
        print(res2)
        if res2.get("corollary_2_confirmed"):
            print("✅ Corollaire 2 CONFIRMÉ")
        else:
            print("❌ Corollaire 2 NON CONFIRMÉ")