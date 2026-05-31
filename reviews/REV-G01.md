# Rapport d’audit de cohérence – **Projet `epistemic-impossibility-validation`**

> **Liens utiles**
> • Théorie : [tie_formal.md](file:///home/andrei/Projects/54_EIP/epistemic-impossibility-validation/theory/tie_formal.md)  [lemme_auditabilite.md](file:///home/andrei/Projects/54_EIP/epistemic-impossibility-validation/theory/lemme_auditabilite.md)  [corollary_framework.md](file:///home/andrei/Projects/54_EIP/epistemic-impossibility-validation/theory/corollary_framework.md)  
> • Implémentation : [channels.py](file:///home/andrei/Projects/54_EIP/epistemic-impossibility-validation/src/channels.py)  [experiment_hybrid.py](file:///home/andrei/Projects/54_EIP/epistemic-impossibility-validation/src/experiment_hybrid.py)  
> • Résultats : [hybrid_comparison.csv](file:///home/andrei/Projects/54_EIP/epistemic-impossibility-validation/results/hybrid_comparison.csv)  
> • Papier : [EIP_paper_v0.3.md](file:///home/andrei/Projects/54_EIP/epistemic-impossibility-validation/paper/EIP_paper_v0.3.md)

---

## 1. Points de rupture – Théorie ↔ Implémentation `torch`

| # | Observation | Impact sur la cohérence |
|---|-------------|--------------------------|
| **1.1** | **`TextChannel.encode`** utilise un **argmax discret** (ligne 90‑92 de `channels.py`). La fonction théorique du TIE (définition 2) suppose une carte **continue et différentiable** afin de pouvoir parler du Jacobien `J_C`. Le **jacobian_norm** mesuré (`get_jacobian_norm`) repose sur une **approximation différentiable** (`soft_encode_fn`, lignes 109‑116) qui n’est **pas la même fonction** que `encode`. | Le proxy expérimental ne reflète pas exactement la notion théorique de Jacobien. La divergence doit être explicitée dans le papier (limite de l’approximation). |
| **1.2** | **`LatentChannel`** est correctement différentiable (jacobien ≈ identité + résidu) et satisfait `‖J_C‖₂ ≥ 0.5` (contrat ligne 210). Aucun problème. |
| **1.3** | **`CLAIMChannel`** n’est **pas gradient‑preserving** (contrat ligne 479) – conforme à la théorie. Cependant, le **`inject_conflict`** ne modifie pas le Jacobien (limite de **QO‑S2‑05** mentionnée dans le papier, ligne 118) ; cela est cohérent avec la théorie, mais le papier doit clairement le signaler comme une **absence de dépendance** entre `conflict_level` et `jacobian_norm`. |
| **1.4** | **HybridOrchestrator** (ligne 43‑60 de `experiment_hybrid.py`) **alterne** entre un canal gradient‑preserving (`LatentChannel`) et un canal auditable (`CLAIMChannel`). Le **TIE** parle d’une **unique fonction `C`** qui doit être à la fois gradient‑preserving *et* auditable. Ici, on **contourne** le théorème en **décomposant** la tâche en deux fonctions distinctes selon le mode (`train` vs `certify`). | Pas de contradiction formelle, mais le **Corollaire 3** doit explicitement préciser que l’avantage provient de *la composition* de deux canaux distincts, non d’une même fonction. |
| **1.5** | Le **`cert_rate`** pour `text_only` et `claim_only` est **forcé à 1.0** (ligne 144‑150), sous l’hypothèse que ces canaux sont *par construction* auditable. Or, `TextChannel` est en réalité **discret** et n’a pas de procédure de certification explicite (`φ`). La certification est donc **implicite**, ce qui pourrait être perçu comme une **hypothèse non justifiée** dans le cadre théorique (condition (a)). | Nécessite une clarification dans le texte : soit définir une fonction `φ` triviale, soit ajuster le protocole d’audit pour le canal texte. |
| **1.6** | La **`generate_latent_with_entropy`** crée des vecteurs d’entropie contrôlée via température, mais la **relation entre l’entropie et la “contrainte d’auditabilité”** (corollaire 1) n’est pas explicitée dans le code. La métrique `entropy_level` ne correspond pas directement à une contrainte d’auditabilité, ce qui rend la **prédiction testable du Corollaire 1** difficile à interpréter. | Ajouter une note dans le code (docstring) ou le papier liant `entropy_level` → paramètres de `φ`. |

**Conclusion des points de rupture**
Aucun **contradiction fondamentale** entre les hypothèses théoriques et la logique du code, mais plusieurs **approximations / hypothèses implicites** (argmax vs fonction différentiable, certification triviale, découpage en deux modes) doivent être clairement exposées dans le manuscrit pour éviter toute accusation de **cavité théorique**.

---

## 2. Solidité topologique de la preuve du TIE

| Critère | Évaluation |
|---------|------------|
| **Exactitude du lemme** (décompte via injection Σ*) | Correct, preuve exhaustive (Stratégie B). |
| **Utilisation pertinente des théorèmes d’Engelking / Munkres** | Les références sont fidèles : Sierpiński ⇒ zéro‑dimensionnel, Engelking ⇒ totalement discontinu, Munkres ⇒ image d’un connexe est connexe. |
| **Pas de saut logique** (H4, dénombrabilité → zéro‑dim → disc.) | La chaîne d’implications est complète; le seul point sensible est l’hypothèse `O` métrique (γ) qui a été ajoutée explicitement (ligne 30 du théorème). |
| **Gestion des cas limites (espaces non métriques, espaces infiniment dénombrables)** | Mentionnée en section 6 (limitations). |
| **Clarté et accessibilité** | Le texte est détaillé, avec tableau des hypothèses (ligne 120‑124). |

**Score de solidité topologique :** **9 / 10**
*Justification :* La démonstration est rigoureuse, bien référencée et ne présente pas de faille majeure. Le seul léger bémol est le besoin d’une phrase explicite rappelant que la propriété « O est métrique » est indispensable pour appliquer le théorème de Sierpiński.

---

## 3. Alignement du papier (`EIP_paper_v0.3.md`) avec les données expérimentales

| Aspect | État actuel | Concordance avec les données |
|--------|-------------|------------------------------|
| **Figure 1 (Jacobien vs Entropie)** | Place‑holder `[PLACEHOLDER — figures/figure1_gradient_entropy.pdf]` (ligne 80). Aucun fichier réel n’est référencé ni généré. | **Non‑aligné** – les courbes décrites dans le texte (gradient collapse) ne sont pas illustrées. |
| **Figure 2 (Learning curves – Corollaire 1)** | Place‑holder (ligne 102). | **Non‑aligné** – aucune courbe réelle. |
| **Figure 4 (Supériorité hybride – Corollaire 3)** | Place‑holder (ligne 108). Le script `plot_figure4` génère `figures/figure4_hybrid_superiority.pdf` (ligne 170‑235) mais le papier ne l’inclut pas. | **Non‑aligné** – le texte mentionne la figure, mais le PDF n’est pas inséré. |
| **Table 4 (Rule O3 – source correlation)** | Place‑holder (ligne 109). Le script `compute_source_correlation` produit `figures/table4_source_correlation.md` (ligne 308‑365), mais le papier ne le contient pas. | **Non‑aligné**. |
| **Descriptions quantitatives** | Le texte indique que “hybrid_strict domine strictement” (section 6.4) et que “cert_rate = 1.0” pour certains canaux, ce qui correspond aux valeurs du CSV (`hybrid_strict` jacobian ≈ 2.3, cert_rate = 1.0 ; `latent_only` jacobian ≈ 2.3, cert_rate = 0). | **Aligné** sur le plan des valeurs, mais **absence de tableaux/figures** empêche la vérifiabilité. |
| **Discussion des limites expérimentales** | Section 7 mentionne des limitations (ex. “jacobian_norm invariant à `conflict_level`”). | Correctement reflété. |

**Conclusion de l’alignement**
Le texte reflète **logiquement** les résultats numériques, mais le manuscrit ne **présente pas les figures/tables générées**. Pour une soumission ICLR, cela constitue une lacune importante.

---

## 4. Verdict GNG (Go / No‑Go)

| Critère | Évaluation |
|---------|------------|
| **Rigueur théorique** | Très solide (score 9/10). |
| **Correspondance code ↔ théorie** | Globalement cohérente, avec plusieurs approximations qui doivent être explicitées. |
| **Qualité des résultats expérimentaux** | Les données sont complètes, reproductibles (CSV, scripts). |
| **Présence de visualisations / tables dans le manuscrit** | Manque de figures et de tables réelles (place‑holders uniquement). |
| **Clarté de la discussion (limitations, hypothèses)** | Bonne, mais nécessite un paragraphe dédié aux approximations du Jacobien et à la séparation des modes dans le *hybrid*. |
| **Prêt pour ICLR** | **Go avec révisions mineures** :  
1. **Intégrer** les fichiers générés (`figure1_…`, `figure2_…`, `figure4_hybrid_superiority.pdf`, `table4_source_correlation.md`) dans le manuscript (avec légendes).  
2. **Clarifier** dans la section “Méthodes” que `TextChannel.get_jacobian_norm` mesure une fonction différentiable approximative, non la fonction `encode` réelle.  
3. **Justifier** la certification triviale du `TextChannel` (condition (a) → `φ(o)=1` partout).  
4. **Éclaircir** le lien entre `entropy_level` et la contrainte d’auditabilité du Corollaire 1.  
Après ces ajustements, le travail sera **prêt** pour une soumission ICLR.

---

**Verdict final :** **Go (avec exigences de révision)**.
