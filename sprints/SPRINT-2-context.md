# Session Sprint 2 — Expérience principale TIE
**Chantier :** epistemic-impossibility-validation
**Durée estimée :** 2.5 jours
**Instance :** Jules (Google) ou Claude Code Web

> **Règle de session :** ce fichier est le seul contexte de cette session.
> Commence par : `git pull` + lecture de `STATUS.md` + lecture de
> `src/channels.py` et `src/calibration.py` (version Sprint 1, commités).
> La source de vérité est le repo — pas cette conversation.

> **Principe de cette session :** tu exécutes l'expérience principale.
> Les canaux sont implémentés et validés — tu ne les modifies pas.
> Ton seul objectif est de produire `results/raw_results.csv` et
> `results/conflict_results.csv` avec les données brutes, reproductibles,
> statistiquement exploitables.

---

## Ce que tu dois savoir sur ce sprint

Le projet compare trois canaux de communication entre agents IA :
- **Canal A (texte)** : encode l'état interne via softmax → token → embedding
- **Canal B (latent)** : transmet le vecteur d'état interne via connexion résiduelle
- **Canal C (CLAIM)** : transforme l'état interne en structure épistémique formelle

Sprint 1 a produit les implémentations. **Ce sprint les fait tourner.**

La question expérimentale centrale (Hypothèse alt. 1 dans `VARIABLES.md`) :
> *Le canal texte voit son jacobien s'effondrer quand l'entropie → 0 ;
> le canal latent maintient un jacobien ≥ c > 0 sur toute la plage d'entropie.*

Tu as besoin de connaître :
- Les trois classes de canaux dans `src/channels.py` (déjà commité)
- Les paramètres dans `VARIABLES.md` (déjà commité)
- Les contrats de `results/*.csv` définis ci-dessous

Tu n'as pas besoin de connaître :
- Le contenu de `theory/theorem71_formal.md`
- La structure du papier final
- Le Sprint 7 (lemme de non-circularité)
- Les corollaires (Sprints 5–6)

---

## Tâche 2.1 — Boucle expérimentale principale (1.5 jour)

**Fichier :** `src/experiment.py`

### Protocole expérimental

**Facteurs :**
- 3 canaux : TextChannel (A), LatentChannel (B), CLAIMChannel (C)
- 6 niveaux d'entropie : `{0.05, 0.1, 0.2, 0.5, 1.0, 2.0}` (voir `VARIABLES.md`)
- 50 runs par cellule (N = 50 minimum — voir R-STAT-02)

**Total lignes attendues :** 3 × 6 × 50 = **900 lignes minimum** dans `raw_results.csv`.

### Génération des vecteurs latents d'entrée

Pour chaque run, générer un vecteur latent `h` de shape `(1, 768)` contrôlé en entropie :

```python
def generate_latent_with_entropy(
    entropy_level: float,
    hidden_dim: int = 768,
    seed: int = 42,
    run_idx: int = 0
) -> torch.Tensor:
    """
    Génère un vecteur latent h dont la distribution softmax associée
    a une entropie proche de entropy_level.

    Stratégie : initialiser h aléatoirement, puis appliquer une
    transformation affine pour contrôler la concentration de la
    distribution softmax sur h.

    Contrat : déterministe pour (entropy_level, seed, run_idx) fixés.
    Contrat : torch.manual_seed utilisé — pas de randomness externe.
    """
```

> **Note R-REPRO-01 :** chaque `(entropy_level, run_idx)` doit avoir un seed
> dérivable de façon déterministe depuis `SEED_GLOBAL=42`. Forme recommandée :
> `seed_run = SEED_GLOBAL * 1000 + run_idx`. Ne jamais utiliser `random.random()`
> non seedé.

### Structure de la boucle principale

```python
def run_experiment(
    channels: dict[str, Channel],
    entropy_levels: list[float],
    n_runs: int = 50,
    seed_global: int = 42,
    output_path: str = "results/raw_results.csv"
) -> pd.DataFrame:
    """
    Exécute l'expérience complète : 3 canaux × 6 niveaux × 50 runs.

    Pour chaque cellule (canal, entropy_level, run_idx) :
      1. Générer h via generate_latent_with_entropy(entropy_level, seed_run)
      2. Mesurer channel.get_jacobian_norm(h) → jacobian_norm
      3. Mesurer channel.get_output_entropy(h)  → output_entropy
      4. Enregistrer la ligne dans le DataFrame

    Contrat : résultats écrits dans output_path à la fin — pas ligne par ligne.
    Contrat : barre de progression visible (tqdm ou print toutes les 50 lignes).
    Contrat : aucune exception silencieuse — tout échec de mesure est loggué.
    """
```

### Schéma de `results/raw_results.csv`

| Colonne | Type | Description |
|---------|------|-------------|
| `canal` | str | `"text"`, `"latent"`, `"claim"` |
| `entropy_level` | float | Niveau d'entropie cible `∈ {0.05, 0.1, 0.2, 0.5, 1.0, 2.0}` |
| `run_idx` | int | Index du run `∈ [0, 49]` |
| `seed_run` | int | Seed utilisé pour ce run (traçabilité R-REPRO-01) |
| `jacobian_norm` | float | `‖J_C(h)‖₂` mesuré |
| `output_entropy` | float | `H(sortie)` mesuré |
| `duration_ms` | float | Durée de mesure en millisecondes |

> **Vérification rapide avant commit :** `wc -l results/raw_results.csv` doit
> retourner ≥ 901 (en-tête + 900 lignes de données).

---

## Tâche 2.2 — Expérience avec conflit injecté (Canal C) (0.5 jour)

**Fichier :** `src/experiment.py` — fonction `run_conflict_experiment`
**Output :** `results/conflict_results.csv`

### Protocole

Cette expérience s'exécute uniquement sur le Canal C (CLAIMChannel).
Elle mesure l'impact du niveau de conflit injecté sur le jacobien et l'entropie.

**Facteurs :**
- 1 canal : CLAIMChannel uniquement (R-CONFLIT-01)
- 4 niveaux de conflit : `{0.0, 0.2, 0.5, 0.8}` (voir `VARIABLES.md`)
- 6 niveaux d'entropie : `{0.05, 0.1, 0.2, 0.5, 1.0, 2.0}`
- 50 runs par cellule

**Total :** 1 × 4 × 6 × 50 = **1 200 lignes** dans `conflict_results.csv`.

### Schéma de `results/conflict_results.csv`

| Colonne | Type | Description |
|---------|------|-------------|
| `entropy_level` | float | Niveau d'entropie cible |
| `conflict_level` | float | Niveau de conflit injecté `∈ {0.0, 0.2, 0.5, 0.8}` |
| `run_idx` | int | Index du run |
| `seed_run` | int | Seed utilisé |
| `jacobian_norm` | float | `‖J_C(h)‖₂` avec conflit |
| `output_entropy` | float | `H(sortie)` avec conflit |
| `m_vide` | float | Masse de conflit effective `m(∅)` dans le CLAIM produit |

> **Invariant à vérifier :** `abs(m_vide - conflict_level) < 0.01` pour chaque ligne.
> Si ce n'est pas le cas, le `inject_conflict()` du Canal C a un bug — logguer
> dans `QO-S2-01` et continuer (ne pas bloquer l'expérience).

---

## Tâche 2.3 — Analyse statistique intermédiaire (0.25 jour)

**Fichier :** `src/analysis.py`

### Fonctions à implémenter

```python
def compute_summary_stats(
    df: pd.DataFrame,
    groupby: list[str] = ["canal", "entropy_level"]
) -> pd.DataFrame:
    """
    Calcule pour chaque groupe : médiane, IQR, min, max, count de jacobian_norm.
    Utilisé pour détecter les groupes à variance élevée (R-STAT-02).
    """

def check_variance_criterion(
    summary: pd.DataFrame,
    threshold_iqr_ratio: float = 0.30
) -> list[dict]:
    """
    Retourne les groupes où IQR > 30% de la médiane (R-STAT-02).
    Pour chaque groupe problématique : {"canal", "entropy_level", "iqr_ratio"}
    Si des groupes sont retournés → logguer QO-S2-02 et augmenter N à 100.
    """

def run_statistical_tests(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Test de Mann-Whitney U (non-paramétrique) entre :
    - Canal A vs Canal B sur jacobian_norm, pour chaque entropy_level
    - Canal A vs Canal C sur jacobian_norm, pour chaque entropy_level

    Retourne un DataFrame avec colonnes :
    comparison, entropy_level, statistic, p_value, significant (bool, seuil 0.05)

    R-STAT-01 : inclure p-value et effet size (Cohen's d ou rank-biserial r).
    """
```

> **Critère de détection variance élevée (R-STAT-02) :** si `check_variance_criterion()`
> retourne des groupes, relancer `run_experiment()` avec `n_runs=100` pour ces groupes
> uniquement, et compléter `raw_results.csv` (append, pas remplacement).

---

## Tâche 2.4 — Vérification de reproductibilité (0.25 jour)

Avant de commiter les résultats, exécuter deux fois `run_experiment()` avec
`seed_global=42` sur un sous-ensemble de 3 cellules (canal A, entropy 0.05,
runs 0–4) et vérifier que les sorties sont identiques à la précision numérique.

```python
def verify_reproducibility(
    channel: Channel,
    entropy_level: float = 0.05,
    n_runs: int = 5,
    seed_global: int = 42
) -> bool:
    """
    Exécute deux fois la mesure sur les mêmes 5 runs.
    Retourne True si jacobian_norm identique à 1e-6 près.
    Logguer QO-S2-03 si False (violation R-REPRO-01).
    """
```

---

## Analyste Sprint 2 — questions soumises

Invoquer une **instance Opus séparée** (sans accès à la conversation de travail)
avec uniquement `src/experiment.py`, `src/analysis.py`, `results/raw_results.csv`,
`results/conflict_results.csv` commités, et ces deux questions :

**Q1 — Reproductibilité :**
En lisant `src/experiment.py` uniquement : le protocole de génération des vecteurs
latents est-il entièrement déterministe à partir de `SEED_GLOBAL=42` et de
`(entropy_level, run_idx)` ? Identifier toute source de non-déterminisme résiduelle
(opérations CUDA, hash Python, appels externes non seedés).

**Q2 — Validité statistique :**
Le test de Mann-Whitney U tel qu'implémenté dans `src/analysis.py` est-il
approprié pour comparer les distributions de `jacobian_norm` entre canaux ?
Existe-t-il une hypothèse de distribution implicite qui invaliderait ce choix ?
Si N=50 révèle une variance élevée sur certaines cellules, la procédure
d'extension à N=100 préserve-t-elle la validité des tests ?

Commiter le rapport Analyste dans `reviews/REV-S2.md`.

---

## Livrables Sprint 2

```
src/experiment.py           ← Boucle expérimentale + conflit + reproductibilité
src/analysis.py             ← Summary stats + variance check + tests statistiques
results/raw_results.csv     ← Données remplies (≥ 900 lignes)
results/conflict_results.csv ← Données remplies (1 200 lignes)
reviews/REV-S2.md           ← Rapport Analyste (Q1, Q2)
```

**Commit final :** `[SPRINT-2] run main TIE experiment : results/raw_results.csv`
`STATUS.md` mis à jour : Sprint courant = 3, statut = PRÊT.

---

## Critère de passage Sprint 2

> **`results/raw_results.csv` : ≥ 900 lignes (3 canaux × 6 niveaux × 50 runs).**
> **IQR ≤ 30% de la médiane sur toutes les cellules (sinon N → 100, QO-S2-02 ouvert).**
> **Tests statistiques : p < 0.05 sur comparaison canal A vs canal B.**
> **REV-S2 : reproductibilité confirmée (Q1), tests valides (Q2).**
> **Score GNG-PAPER ≥ 60 sur Solidité expérimentale + Reproductibilité.**

**No-Go partiel :** si la reproductibilité est violée (Q1 NON), ouvrir `QO-S2-03`
et résoudre avant de passer à Sprint 3. Les figures de Sprint 3 construites sur
des données non-reproductibles sont invalides.

---

## Paramètres techniques de référence

Tous issus de `VARIABLES.md` (source de vérité) :

| Paramètre | Valeur |
|-----------|--------|
| Modèle base | GPT-2 small (117M, `"gpt2"`) |
| `hidden_dim` | 768 |
| `SEED_GLOBAL` | 42 |
| Niveaux d'entropie | `{0.05, 0.1, 0.2, 0.5, 1.0, 2.0}` |
| Niveaux de conflit | `{0.0, 0.2, 0.5, 0.8}` |
| N runs (minimum) | 50 par cellule |
| N runs (si variance élevée) | 100 par cellule |
| Seuil IQR/médiane | 30% |
| Seuil p-value | 0.05 |

---

## Règles applicables à cette session

| Règle | Application concrète |
|-------|----------------------|
| `R-REPRO-01` | Chaque run est seedé de façon déterministe depuis `SEED_GLOBAL` |
| `R-REPRO-02` | Canal C bit-à-bit identique entre deux runs avec même seed |
| `R-STAT-01` | Toute comparaison inclut p-value + effet size |
| `R-STAT-02` | N=50 minimum ; IQR > 30% médiane → N=100 |
| `R-CONFLIT-01` | Condition D (conflit injecté) systématiquement exécutée sur Canal C |
| `#16 Pure Function Contract` | `generate_latent_with_entropy` est une fonction pure — même args → même sortie |
| `#4 No Hidden State` | Tout paramètre expérimental est déclaré dans la signature des fonctions |
| `#18 Debt Visibility` | Toute anomalie (variance élevée, reproductibilité cassée) → `QO-S2-XX` ouvert |

---

*Fichier de session — ne pas modifier après la session*
*Sprint 2 — v4 — Mai 2026*
