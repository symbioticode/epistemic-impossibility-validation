# REV-S2 — Rapport d'Analyse Sprint 2

**Date :** 2026-05-31
**Analyste :** Instance isolée (Claude Sonnet 4.6)
**Sprint :** 2 — Expérience principale TIE
**Fichiers examinés :** `src/experiment.py`, `src/analysis.py`,
`results/raw_results.csv` (900 lignes), `results/conflict_results.csv` (1200 lignes)

---

## Q1 — Reproductibilité

**Question :** Le protocole de génération des vecteurs latents est-il entièrement
déterministe à partir de `SEED_GLOBAL=42` et de `(entropy_level, run_idx)` ?

**Analyse :**

La fonction `generate_latent_with_entropy` dérive chaque seed via
`seed_run = SEED_GLOBAL * 1000 + run_idx`, puis instancie un générateur local
`torch.Generator().manual_seed(seed_run)`. Aucun appel à `random.random()`,
`np.random.rand()` non seedé, ou opération CUDA non déterministe n'a été détecté.

La vérification `verify_reproducibility` a été exécutée sur le LatentChannel
(ε=0.05, 5 runs) avec résultat : **✅ Reproductible** (différences < 1e-6).

Le calcul du jacobien via power iteration (`_spectral_norm_power`) utilise
`torch.manual_seed(0)` en début de fonction, ce qui le rend déterministe
entre appels sur le même `h`. Ce seed interne est indépendant du seed global
du run — acceptable car il n'affecte que la convergence de la norme spectrale,
pas les données de l'expérience.

**Note :** `channels_standalone.py` remplace les poids GPT-2 réels par une
matrice `wte` initialisée aléatoirement avec `seed=42`. Ce choix est documenté
et cohérent avec l'objectif d'isolation HuggingFace. La norme du jacobien du
canal texte mesure la sensibilité de la tête softmax → embedding, ce qui est
le signal d'intérêt du TIE.

**Verdict : GO** — Protocole déterministe à partir de `(SEED_GLOBAL, entropy_level, run_idx)`.

---

## Q2 — Validité statistique

**Question :** Le test de Mann-Whitney U est-il approprié ? L'extension N=50 → N=100
préserve-t-elle la validité des tests ?

**Analyse :**

Les distributions de `jacobian_norm` sont clairement non-gaussiennes (valeurs
bornées à zéro, asymétrie forte pour le canal texte). Le test de Mann-Whitney U
(non-paramétrique) est approprié — il ne suppose pas de distribution normale et
teste correctement la stochasticité ordinale entre les deux échantillons.

**Résultats :** 12/12 comparaisons (text vs latent et text vs claim, pour 6 niveaux
d'entropie) sont significatives avec p=0.0 et effect size r=-1.0 (rang biserial).
La séparation est totale — aucun chevauchement entre les distributions.

**QO-S2-02 (ouvert) :** deux groupes présentent IQR > 30% de la médiane :
- `claim, ε=0.05` : IQR/médiane = 0.484
- `text, ε=0.05` : IQR/médiane = 0.503

Ces deux groupes correspondent au niveau d'entropie le plus bas, où la
génération des vecteurs latents est plus sensible aux variations de seed.
Conformément à R-STAT-02, ces cellules devraient être étendues à N=100 dans
un sprint suivant. Cela n'invalide pas les tests actuels car la séparation
entre canaux reste totale même à N=50.

**Extension N→100 :** si elle est appliquée par append (pas remplacement),
le pool combiné reste valide pour Mann-Whitney U — l'hypothèse nulle et la
statistique U sont invariantes à l'augmentation de taille d'échantillon.

**Verdict : GO conditionnel** — Tests valides. QO-S2-02 ouvert pour ε=0.05
(claim et text). Extension N→100 recommandée pour ces deux cellules avant Sprint 3.

---

## Résultats clés

| Canal  | Médiane jacobian_norm | IQR   | Signal TIE |
|--------|----------------------|-------|------------|
| text   | 0.0010               | 0.0005| ✅ Effondrement confirmé |
| latent | 2.5513               | 0.0913| ✅ Stable sur toute la plage |
| claim  | 0.2321               | 0.1144| ✅ Intermédiaire (non gradient-preserving) |

**Invariant R-CONFLIT-01 :** max(|m_vide - conflict_level|) = 0.000000 — ✅ parfait.

---

## Critère de passage Sprint 2

| Critère | Statut |
|---------|--------|
| raw_results.csv ≥ 900 lignes | ✅ 900 lignes |
| IQR ≤ 30% médiane toutes cellules | ⚠️ QO-S2-02 ouvert (2 cellules ε=0.05) |
| Tests statistiques p < 0.05 (A vs B) | ✅ 12/12 p=0.0 |
| Reproductibilité confirmée (Q1) | ✅ GO |
| Tests valides (Q2) | ✅ GO conditionnel |

**Verdict global : GO conditionnel** — Sprint 3 peut démarrer.
QO-S2-02 à résoudre en parallèle (N→100 sur 2 cellules) sans bloquer Sprint 3.

---

*Sprint 2 — instance isolée — 2026-05-31*
