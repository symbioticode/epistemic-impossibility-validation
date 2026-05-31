# Session Sprint 2 — Post‑review coherence fixes 
**Chantier :** epistemic-impossibility-validation
**Durée estimée :** 0.5 jours
**Instance :** Antigravity (Google) ou Claude Code Web

## Prompt pour la correction et l’amélioration de la cohérence globale du projet

Vous êtes le responsable de l’intégration des révisions issues de deux audits indépendants (REV‑G01 et REV‑G02). Le projet `epistemic-impossibility-validation` a reçu un verdict **« Go with minor revisions »** . Les corrections sont classées en trois catégories : **éditoriales / documentation**, **modifications légères du code / expériences**, et **révisions conceptuelles / théoriques** (qui peuvent nécessiter des recalculs ou des ajustements architecturaux).  

Ci‑dessous, la liste exhaustive des actions à mener, avec priorisation. À l’issue de ces corrections, le projet sera prêt pour une soumission ICLR 2027.

---

## 1. Corrections éditoriales et documentation (aucun impact sur les résultats)

| # | Action | Fichier(s) concerné(s) | Priorité |
|---|--------|------------------------|----------|
| 1.1 | Remplacer tous les `[PLACEHOLDER — …]` par les liens réels vers les figures et tables générées (figures 1 à 4, tables 1 à 4). | `paper/EIP_paper_v0.3.md` | Haute |
| 1.2 | Convertir les tables Markdown (`*.md` dans `figures/`) en tables LaTeX (ou les laisser en Markdown si la conférence l’accepte, mais harmoniser). | `paper/EIP_paper_v0.3.md` | Haute |
| 1.3 | Vérifier et corriger les fautes d’orthographe, la mixité français/anglais (ex. "La dichotomie manquante" → titre en anglais cohérent). | `paper/EIP_paper_v0.3.md` | Haute |
| 1.4 | Ajouter un paragraphe **« Broader Impact »** comme requis par ICLR. | `paper/EIP_paper_v0.3.md` | Moyenne |
| 1.5 | S’assurer que toutes les références bibliographiques citées apparaissent dans la bibliographie (ex. Yang et al., 2026). | `paper/EIP_paper_v0.3.md` | Haute |
| 1.6 | Ajouter un **checklist de reproductibilité** (`README-reproducibility.md`) avec la ligne de commande exacte, les seeds utilisées (42‑52), et l’environnement (`environment.yml`). | `README-reproducibility.md`, `environment.yml` | Moyenne |
| 1.7 | Ajouter une légende explicative pour chaque figure (pas seulement un placeholder). | `paper/EIP_paper_v0.3.md` | Moyenne |
| 1.8 | Ajouter une note sur les seeds aléatoires dans le papier (ex. “All experiments run with seeds 42‑52”). | `paper/EIP_paper_v0.3.md` (Section 6) | Basse |

---

## 2. Modifications légères du code / expériences (pas de révision théorique)

| # | Action | Fichier(s) concerné(s) | Priorité |
|---|--------|------------------------|----------|
| 2.1 | Ajouter des **docstrings** à la méthode `inject_conflict` dans `CLAIMChannel` (expliquer qu’elle modifie `m_vide` sans affecter le jacobien). | `src/channels.py` | Haute |
| 2.2 | Ajouter un **test unitaire** pour `CLAIMChannel.encode` vérifiant que la somme des masses = 1. | `tests/test_channels.py` (à créer) | Basse |
| 2.3 | Dans `TextChannel`, commenter explicitement que `get_jacobian_norm` utilise une approximation différentiable (`soft_encode_fn`) alors que `encode` est discret. | `src/channels.py` (lignes 90‑92 et 109‑116) | Moyenne |
| 2.4 | Ajouter une vérification que `cert_rate` pour `TextChannel` et `CLAIMChannel` est bien forcé à 1.0, et justifier pourquoi (certification implicite). | `src/experiment_hybrid.py` (lignes 144‑150) | Basse (déjà mentionné dans REV‑G01) |

---

## 3. Révisions conceptuelles / théoriques (peuvent nécessiter des recalculs ou des clarifications majeures)

| # | Action | Justification / Impact | Priorité |
|---|--------|------------------------|----------|
| 3.1 | **Clarifier le lien entre `entropy_level` et la contrainte d’auditabilité** dans le Corollaire 1. Actuellement, l’entropie est une température softmax, non un paramètre d’auditabilité. Il faut ajouter une explication dans le papier (Section 6) : *“We vary the output entropy of the text channel by scaling the softmax temperature; lower entropy simulates a more deterministic (thus more auditable) channel.”* | Évite l’accusation de non‑correspondance entre théorie et expérience. | Haute |
| 3.2 | **Justifier l’approximation du Jacobien pour `TextChannel`** – la fonction `encode` réelle (argmax) n’est pas différentiable. Expliquer pourquoi la mesure via `soft_encode_fn` est un proxy acceptable, et mentionner cette limite en Section 7 (Limitations). | Nécessaire pour la rigueur. | Haute |
| 3.3 | **Résoudre la certification implicite du `TextChannel`** – le papier suppose que le canal texte est auditable, mais aucune fonction `φ` explicite n’est implémentée. Proposition : ajouter une fonction `is_certified` dans `TextChannel` qui retourne toujours `True` (car tout message texte est considéré comme certifiable). Inclure cette justification dans la Section 6. | Corrige le point soulevé dans REV‑G01 (1.5). | Moyenne |
| 3.4 | **Vérifier l’hypothèse γ (métrisabilité de O)** dans le contexte expérimental : l’espace de sortie du CLAIM (masses sur Θ) est métrique (par ex. distance de Jousselme). Ajouter une phrase dans la Section 3.1 pour le justifier. | Aucun recalcul nécessaire, simple clarification. | Basse |
| 3.5 | **Re‑examiner le Corollaire 2 (RLHF)** – les données montrent une décroissance monotone du jacobien avec κ, mais le signal multi‑round est nul. Le papier doit **séparer** les deux sous‑résultats : (a) décroissance du jacobien (confirmée), (b) propagation du signal sur plusieurs rounds (non validée, à déplacer en travaux futurs). | Nécessite une réécriture de la Section 6.3 et un ajustement des claims. | Haute |
| 3.6 | **Ajouter une note sur l’absence d’effet du conflit injecté sur le jacobien** – c’est attendu (le conflit est sémantique, non différentiable). Mentionner explicitement dans la Section 6.3 (Condition D) pour éviter toute suspicion de bug. | Clarification nécessaire. | Moyenne |
| 3.7 | **Vérifier que l’architecture hybride (Corollaire 3) ne viole pas le TIE** – le papier doit explicitement dire que le théorème s’applique à un **canal unique**, et que l’avantage hybride vient de la composition de deux canaux distincts. | Déjà mentionné dans REV‑G01, mais à renforcer dans le texte. | Basse |

---

## 4. Tâches nécessitant des recalculs ou de nouvelles expériences (si le temps le permet)

| # | Action | Justification |
|---|--------|----------------|
| 4.1 | **Augmenter le nombre de runs (N=30 ou 50)** pour le Corollaire 1 et 3, afin d’améliorer la puissance statistique (actuellement N=10). Recalculer p‑values. | Optionnel, mais renforcerait la crédibilité. |
| 4.2 | **Tester le Corollaire 2 sur une tâche plus complexe** (ex. classification sur CIFAR‑10 via un encodeur) pour observer si le signal RLHF persiste sur plusieurs rounds. | Non bloquant pour ICLR, mais utile pour travaux futurs. |
| 4.3 | **Implémenter une certification explicite pour `TextChannel`** avec une fonction `φ` qui vérifie que la sortie est un token valide (toujours vrai). | Peut être fait en 30 minutes, sans recalcul. |

---

## Instructions de priorisation

- **Haute priorité** : à traiter avant toute nouvelle soumission (corrections éditoriales + clarifications conceptuelles 3.1, 3.2, 3.5).  
- **Priorité moyenne** : à traiter si possible avant la re‑soumission, mais peut être repoussé à une version révisée après revue par les pairs.  
- **Priorité basse** : peut être intégré dans une mise à jour mineure.

Après avoir appliqué ces corrections, relancez une vérification rapide (un `REV‑G03` léger) pour confirmer que tous les placeholders sont remplacés et que les clarifications sont cohérentes.

**Rendu attendu :** un commit sur la branche principale contenant les modifications décrites, avec un message de commit clair : `“Post‑review coherence fixes (editorial + minor code + conceptual clarifications)”`.  

---  

Ce prompt peut être directement confié à un assistant ou à un membre de l’équipe. Il évite de demander des recalculs massifs tout en assurant la rigueur nécessaire.