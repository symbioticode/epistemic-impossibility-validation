# Session Sprint 3 — Figures et tables
**Chantier :** epistemic-impossibility-validation
**Durée estimée :** 1.5 jour
**Instance :** Jules (Google) ou Claude Code Web — Haiku pour les calculs de vérification

> **Règle de session :** ce fichier est le seul contexte de cette session.
> Commence par : `git pull` + lecture de `STATUS.md` + lecture de
> `results/raw_results.csv` et `results/conflict_results.csv` (Sprint 2, commités).
> La source de vérité est le repo — pas cette conversation.

> **Principe de cette session :** tu produis les figures et tables à partir
> des données brutes. Tu ne modifies pas les données, tu ne relances pas
> l'expérience. Ton seul objectif est que Figure 1 et les Tables 1–3
> soient lisibles, correctes par rapport aux données, et prêtes pour
> l'intégration dans le papier.

---

## Ce que tu dois savoir sur ce sprint

Les données expérimentales sont dans `results/raw_results.csv` (900+ lignes)
et `results/conflict_results.csv` (1 200 lignes). Elles ont été validées
par REV-S2 (reproductibilité et tests statistiques confirmés).

**Ce sprint produit quatre livrables visuels :**
- `figures/figure1_gradient_entropy.pdf` — résultat principal du TIE
- `figures/table1_main_results.md` — table principale des résultats
- `figures/table2_stats.md` — tests statistiques
- `figures/table3_calibration.md` — résultats de calibration γ_i

Tu as besoin de connaître :
- Le schéma de `results/raw_results.csv` et `conflict_results.csv` (Sprint 2)
- Les paramètres dans `VARIABLES.md` (déjà commité)
- Les contraintes de format ICLR définies ci-dessous

Tu n'as pas besoin de connaître :
- Le contenu de `theory/theorem71_formal.md`
- Le Sprint 7 (lemme de non-circularité)
- La structure complète du papier final

---

## Tâche 3.1 — Figure 1 : Gradient norm vs entropie (0.75 jour)

**Fichier :** `src/analysis.py` — compléter avec les fonctions de visualisation
**Output :** `figures/figure1_gradient_entropy.pdf`

### Ce que la figure doit montrer

Figure 1 valide visuellement l'Hypothèse alt. 1 :
> *Le canal texte voit son jacobien s'effondrer quand l'entropie → 0 ;
> le canal latent maintient un jacobien ≥ c > 0 sur toute la plage.*

**Structure de la figure :**
- Axe X : niveau d'entropie (échelle log recommandée : 0.05 → 2.0)
- Axe Y : médiane de `jacobian_norm` (échelle linéaire ou log selon résultats)
- 3 courbes : Canal A (texte), Canal B (latent), Canal C (CLAIM)
- Barres d'erreur : IQR (Q1–Q3) pour chaque point — R-STAT-01
- Légende explicite, axes labellisés, titre absent (convention ICLR)

### Contraintes visuelles

```python
def plot_figure1(
    df: pd.DataFrame,
    output_path: str = "figures/figure1_gradient_entropy.pdf"
) -> None:
    """
    Génère Figure 1 à partir de raw_results.csv.

    Contraintes :
    - Format PDF vectoriel (plt.savefig(..., format='pdf', bbox_inches='tight'))
    - DPI ≥ 300 (même pour PDF — préserve la qualité des polices)
    - Police : serif ou sans-serif standard (pas de LaTeX requis)
    - Taille de figure : (6, 4) pouces (format ICLR double-colonne)
    - 3 couleurs distinctes daltonien-compatibles :
        Canal A (texte)  : '#1f77b4' (bleu)
        Canal B (latent) : '#2ca02c' (vert)
        Canal C (CLAIM)  : '#d62728' (rouge)
    - Marqueurs distincts : 'o', 's', '^' pour A, B, C
    - Barres d'erreur : alpha=0.3, capsize=4

    Contrat : la figure est lisible en noir et blanc (R-TRL-PAPER-01).
    Contrat : les valeurs numériques dans la figure sont cohérentes avec
              les valeurs dans table1_main_results.md (vérification manuelle
              obligatoire avant commit).
    """
```

### Critère visuel de validation (R-TRL-PAPER-01)

La figure doit satisfaire ces critères visuellement identifiables :
- Canal A (texte) : courbe de jacobian_norm décroissante quand entropy_level → 0.05
- Canal B (latent) : courbe stable (horizontale ou quasi-horizontale) sur toute la plage
- Canal C (CLAIM) : courbe ≤ Canal B pour toutes les valeurs d'entropie

Si Canal A ne montre pas d'effondrement visible à entropie basse :
- Logguer `QO-S3-01` avec les valeurs numériques observées
- Ne pas modifier les données ni la figure pour forcer le pattern
- Documenter comme résultat négatif (R-TRL-PAPER-01 : ne pas survendre)

---

## Tâche 3.2 — Table 1 : Résultats principaux (0.25 jour)

**Output :** `figures/table1_main_results.md`

### Schéma de la table

Pour chaque combinaison (canal, entropy_level) : médiane de `jacobian_norm`,
IQR, et ratio IQR/médiane.

```markdown
# Table 1 — Jacobian norm par canal et niveau d'entropie (médiane ± IQR)

| Entropie | Canal A (texte) | Canal B (latent) | Canal C (CLAIM) |
|----------|----------------|-----------------|-----------------|
| 0.05     | X.XX ± Y.YY    | X.XX ± Y.YY     | X.XX ± Y.YY     |
| 0.10     | ...            | ...             | ...             |
| 0.20     | ...            | ...             | ...             |
| 0.50     | ...            | ...             | ...             |
| 1.00     | ...            | ...             | ...             |
| 2.00     | ...            | ...             | ...             |

*N = 50 runs par cellule. IQR = Q3 − Q1.*
*Valeurs issues de results/raw_results.csv (commité [hash]).*
```

> **Cohérence obligatoire :** les valeurs de Table 1 doivent correspondre
> exactement aux points plotés dans Figure 1. Vérification : calculer les
> médianes depuis `raw_results.csv` et comparer manuellement à la figure.
> Tout écart est tracé comme `QO-S3-02`.

---

## Tâche 3.3 — Table 2 : Tests statistiques (0.25 jour)

**Output :** `figures/table2_stats.md`

### Schéma de la table

Résultats des tests de Mann-Whitney U (produits par `src/analysis.py` en Sprint 2)
entre Canal A vs Canal B, et Canal A vs Canal C, pour chaque niveau d'entropie.

```markdown
# Table 2 — Tests statistiques (Mann-Whitney U, N=50 par groupe)

| Entropie | A vs B : U | A vs B : p | A vs B : sig. | A vs B : r | A vs C : U | A vs C : p | A vs C : sig. | A vs C : r |
|----------|-----------|-----------|--------------|-----------|-----------|-----------|--------------|-----------|
| 0.05     | ...       | ...       | ***          | ...       | ...       | ...       | ***          | ...       |
| ...      |           |           |              |           |           |           |              |           |

*Significance : *** p<0.001 · ** p<0.01 · * p<0.05 · ns p≥0.05*
*r = rank-biserial correlation (effet size)*
```

> **Note R-STAT-01 :** l'effet size (r) est obligatoire. Un p < 0.05 sans effet
> size est insuffisant pour ICLR — déclarer les deux.

---

## Tâche 3.4 — Table 3 : Calibration γ_i (0.25 jour)

**Output :** `figures/table3_calibration.md`

### Contenu

Table 3 rapporte les résultats de `verify_calibration()` (Sprint 1) sur le Canal C.
Elle montre que la calibration γ_i est stable et reproductible.

```markdown
# Table 3 — Résultats de calibration Canal C (γ_i)

| Paramètre | Valeur |
|-----------|--------|
| Méthode de calibration | k-NN (k=5) ou Deep EK-NN (selon BR-002) |
| Corrélation calibration | X.XX |
| seed_check | True / False |
| N points de référence | XX |
| Seuil d'alerte (QO-S1-01) | 0.50 |
| Statut | Calibré / Non-calibré |

*Source : results de verify_calibration() — Sprint 1.*
*Si corrélation < 0.50 : voir QO-S1-01 dans BR-002.*
```

> **Si `QO-S1-01` est ouvert (corrélation < 0.50) :** le mentionner explicitement
> dans Table 3 avec la valeur observée. Ne pas masquer. (R-TRL-PAPER-01, #18 Debt Visibility)

---

## Tâche 3.5 — Vérification numérique indépendante (Haiku)

Après production des quatre livrables, soumettre à une **instance Haiku** uniquement :
- `results/raw_results.csv`
- `figures/table1_main_results.md`
- `figures/table2_stats.md`

avec la question : *Vérifier que les valeurs numériques de Table 1 et Table 2 sont
cohérentes avec les données de raw_results.csv. Lister tout écart > 1e-4.*

> R-CALC-01 : tout calcul numérique est vérifié par Haiku indépendamment.
> Un écart détecté → corriger la table (pas les données).

---

## Analyste Sprint 3 — questions soumises

Invoquer une **instance Opus séparée** (sans accès à la conversation de travail)
avec `figures/figure1_gradient_entropy.pdf`, `figures/table1_main_results.md`,
`figures/table2_stats.md`, `results/raw_results.csv` commités, et ces deux questions :

**Q1 — Cohérence figure / données :**
Les valeurs numériques dans Table 1 et les points visualisés dans Figure 1
sont-ils cohérents avec `raw_results.csv` ? Identifier tout écart ou
transformation non déclarée des données (agrégation cachée, filtrage non documenté).

**Q2 — Lisibilité ICLR :**
La Figure 1, telle que produite, permet-elle à un lecteur de vérifier visuellement
l'hypothèse centrale (effondrement du jacobien pour le canal texte à entropie basse) ?
Identifier tout problème de lisibilité : barres d'erreur illisibles, axes mal labellisés,
couleurs indistinguables en noir et blanc, ou pattern attendu non visible.

Commiter le rapport Analyste dans `reviews/REV-S3.md`.

---

## Livrables Sprint 3

```
src/analysis.py                       ← Complété avec fonctions de visualisation
figures/figure1_gradient_entropy.pdf  ← Figure principale (PDF vectoriel)
figures/table1_main_results.md        ← Table résultats principaux
figures/table2_stats.md               ← Table tests statistiques
figures/table3_calibration.md         ← Table calibration γ_i
reviews/REV-S3.md                     ← Rapport Analyste (Q1, Q2)
```

**Commit final :** `[SPRINT-3] produce figure1 and tables 1-3 : figures/`
`STATUS.md` mis à jour : Sprint courant = 7, statut = PRÊT.

> **Note de séquence :** après Sprint 3, le prochain sprint est **Sprint 7**
> (lemme de non-circularité), pas Sprint 4. Sprint 4 (rédaction) est bloqué
> sur REV-S7 (R-SEQ-01). Ne pas démarrer Sprint 4 avant le verdict GO de REV-S7.

---

## Critère de passage Sprint 3

> **Figure 1 : canal A jacobien décroissant quand entropie → 0 (visible visuellement).**
> **Figure 1 : canal B jacobien stable (≥ 0.5 référence) sur toute la plage d'entropie.**
> **Tables 1–3 : valeurs cohérentes avec `raw_results.csv` (vérification Haiku).**
> **REV-S3 : cohérence confirmée (Q1), lisibilité confirmée (Q2).**
> **Score GNG-PAPER ≥ 65 sur Solidité expérimentale + Reproductibilité + Clarté rédactionnelle.**

**No-Go partiel :** si Figure 1 ne montre pas l'effondrement du canal A à entropie basse,
logguer `QO-S3-01` et escalader au PI avant de passer à Sprint 7. Ce pattern est
la validation visuelle centrale du TIE — son absence remet en question l'hypothèse
expérimentale (pas les données).

---

## Paramètres techniques de référence

| Paramètre | Valeur |
|-----------|--------|
| Format figure | PDF vectoriel, (6, 4) pouces |
| DPI | ≥ 300 |
| Couleurs canaux | A='#1f77b4', B='#2ca02c', C='#d62728' |
| Barres d'erreur | IQR (Q1–Q3), alpha=0.3 |
| Test statistique | Mann-Whitney U, seuil p < 0.05 |
| Effet size | rank-biserial correlation r |
| Seuil alerte calibration | corrélation < 0.50 |

---

## Règles applicables à cette session

| Règle | Application concrète |
|-------|----------------------|
| `R-TRL-PAPER-01` | Ne pas modifier les données pour forcer le pattern — documenter tel quel |
| `R-STAT-01` | Toute comparaison inclut p-value ET effet size (r) |
| `R-CALC-01` | Vérification numérique indépendante par Haiku avant commit |
| `#1 Ground Truth or Silence` | Si le pattern n'est pas visible : β=F documenté, pas masqué |
| `#4 No Hidden State` | Toute transformation des données (agrégation, filtrage) est déclarée |
| `#18 Debt Visibility` | Tout écart entre figure et données → `QO-S3-XX` ouvert |
| `#17 Validate Before Automate` | Vérifier manuellement un point de Table 1 avant de scripter la génération complète |

---

*Fichier de session — ne pas modifier après la session*
*Sprint 3 — v4 — Mai 2026*
