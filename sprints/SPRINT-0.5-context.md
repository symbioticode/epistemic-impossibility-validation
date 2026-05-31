# Session Sprint 0.5 — Formalisation théorique préalable
**Chantier :** epistemic-impossibility-validation
**Durée estimée :** 2.5 jours
**Instance :** Opus 4.7 + extended thinking

> **Règle de session :** ce fichier est le seul contexte de cette session.
> Commence par lire STATUS.md et theory/theorem71_formal.md (squelettes) dans le repo.
> La source de vérité est le repo — pas cette conversation.
> Ne pas injecter la méthodologie complète, les sprints expérimentaux, ni Sprint 7.

> **Principe de cette session :** tu formalises les définitions. Tu ne démontre
> rien ici. Ton seul objectif est que les définitions soient primitives, séparées,
> et non-circulaires — qu'elles ne supposent pas ce qu'elles prétendent définir.

---

## Contexte minimal nécessaire

Le projet valide un théorème sur les canaux de communication dans les systèmes
multi-agents. Ce théorème affirme qu'un canal ne peut pas être simultanément
**gradient-preserving** (expressif, continu) et **auditable** (certifiable,
formellement vérifiable).

La preuve de ce théorème repose sur une chaîne logique :
```
(1) auditabilité → propriété structurelle de l'espace de sortie
(2) propriété structurelle → incompatibilité avec le gradient
```

**Ce que tu dois produire en Sprint 0.5 :** le bloc (1) — les définitions
formelles, en particulier la définition d'auditabilité, qui sera le point
de départ d'une démonstration ultérieure (dans un sprint futur que tu n'as
pas besoin de connaître maintenant).

**Ce que tu ne dois pas produire ici :** la démonstration elle-même.
Les définitions d'abord. La démonstration ensuite, dans une session séparée,
par une instance qui ne verra que les définitions et l'énoncé à démontrer.

---

## Tâche 1 — Définitions formelles (1 jour)

Rédiger `theory/theorem71_formal.md` — version provisoire.

### Ce fichier doit contenir exactement :

**1. Définition : Canal de communication C**
- Un canal C prend en entrée un état latent h ∈ ℳ (espace latent)
  et produit une sortie o ∈ O (espace de sortie).
- Formaliser (ℳ, g) comme variété riemannienne lisse, connexe, dim(ℳ) > 0.

**2. Définition : Gradient-preserving**
- Propriété formelle : ∃ c > 0 tel que ‖J_C(h)‖₂ ≥ c pour tout h ∈ ℳ
  (où J_C est le jacobien de C en h).
- Intuition : le canal préserve les variations de l'espace latent —
  des entrées différentes produisent des sorties différentes.

**3. Définition : Auditable — à formaliser en trois conditions séparées**

La définition d'auditabilité doit être construite à partir de propriétés
primitives, sans référence au concept de "discrétion" ni à la "dénombrabilité"
de l'espace de sortie. Ces propriétés doivent être dérivables depuis
les conditions, pas supposées dans les conditions.

Les trois conditions à formaliser :

> **(a) Décidabilité :** il existe une machine de Turing M qui s'arrête sur
>     toute entrée o ∈ O — la vérification est un processus fini.

> **(b) Prédicat de validation :** M produit "valide" si et seulement si
>     o satisfait un prédicat décidable Φ — la certification est formelle
>     et reproductible.

> **(c) Représentation :** chaque sortie certifiée (o tel que M(o) = "valide")
>     a une représentation finie et unique — la certification est sans ambiguïté.

**Contrainte de rédaction :** chaque condition doit être formulable sans
utiliser les mots "discret", "dénombrable", "fini" dans la définition
de la condition elle-même. Ces propriétés doivent être *déductibles* des
conditions, pas *incluses* dans les conditions.

**4. Définition : Canal certifiable (exemples concrets)**
- Message appartenant à un schéma JSON validé
- Formule logique propositionnelle valide
- Fonction de masse sur un cadre de discernement fini

Ces exemples servent à ancrer la définition dans les systèmes réels.
Ils ne font pas partie de la définition formelle.

**5. Énoncé-cible (sans preuve)**

Rédiger l'énoncé du résultat visé, sous cette forme exacte, sans le démontrer :

```
Résultat visé (à démontrer dans un sprint ultérieur) :
  Si C est auditable au sens des conditions (a), (b), (c),
  alors l'ensemble O_cert = {o ∈ O | M(o) = "valide"}
  satisfait une propriété structurelle P.
  [Ne pas écrire quelle est la propriété P — la laisser à démontrer.]
```

> **Pourquoi ne pas écrire la propriété P ici ?** Parce que la formulation
> de P dans les définitions biaiserait la démonstration future. L'instance
> qui démontrera le résultat doit dériver P des conditions, pas la lire dans
> les définitions. C'est la garantie de non-circularité.

---

## Tâche 2 — Isomorphisme Belnap / TBM (0.5 jour)

Rédiger `theory/belnap_tbm_isomorphism.md`.

### Contexte

Le projet utilise deux formalismes pour représenter l'incertitude et le conflit
dans les systèmes multi-agents :
- **L'espace de Belnap flou** (Perry & Tsoukias 1998) : quatre états {T, F, B, N}
  (True, False, Both, Neither) avec des valeurs de vérité graduées.
- **Le Transferable Belief Model (TBM)** de Smets (1994) : fonctions de masse
  sur des sous-ensembles d'un cadre de discernement Θ.

### Ce que tu dois produire

Démontrer l'isomorphisme entre ces deux espaces — c'est-à-dire montrer qu'il
existe une bijection préservant la structure algébrique entre :
- l'espace des valeurs de vérité de Belnap flou sur Θ = {T, F}
- l'espace des fonctions de masse m : 2^{T,F,B,N} → [0,1]

**Structure du fichier :**
1. Rappel des deux structures (définitions)
2. Construction de la bijection γ : Belnap flou → TBM
3. Vérification que γ préserve les opérations (conjonction, disjonction)
4. Corollaire : les quatre états Belnap correspondent à quatre types de masses

---

## Tâche 3 — Vérification de cohérence par l'Analyste (0.5 jour)

Après avoir produit `theory/theorem71_formal.md` et l'avoir commité,
invoquer une **instance Opus séparée** (extended thinking activé) sans
lui donner accès à la conversation de travail.

Soumettre uniquement :
- Le fichier `theory/theorem71_formal.md` commité
- Les deux questions suivantes, exactement telles qu'elles sont formulées :

**Question 1 :**
> Les trois conditions (a), (b), (c) de la définition d'auditabilité
> supposent-elles implicitement la propriété qu'elles sont censées permettre
> de dériver, ou en sont-elles indépendantes ?
> Identifier toute hypothèse cachée dans la formulation des conditions.

**Question 2 :**
> La définition d'auditabilité en trois conditions est-elle plus forte que
> nécessaire — c'est-à-dire : existe-t-il une définition strictement plus
> faible (moins de conditions, ou conditions plus permissives) qui permettrait
> encore de dériver la même propriété structurelle sur O_cert ?
> Si oui, proposer la définition allégée.

**Livrable Tâche 3 :** le rapport de l'Analyste est commité dans `reviews/REV-S0.5.md`.

**Critère de passage Tâche 3 :**
- Réponse à Q1 : les conditions sont indépendantes de la propriété cible (aucune
  hypothèse cachée détectée)
- Réponse à Q2 : soit confirmation que les trois conditions sont toutes nécessaires,
  soit proposition d'allégement documentée et tracée dans BR-010

Si l'Analyste identifie une hypothèse cachée en Q1 : revenir à Tâche 1 et
reformuler les conditions incriminées avant de passer à Tâche 4.

---

## Tâche 4 — Cadrage théorique des corollaires (0.5 jour)

Rédiger `theory/corollary_framework.md`.

### Ce que tu dois produire

Un document qui établit la **chaîne déductive** depuis le résultat principal
(à démontrer plus tard) vers trois corollaires empiriquement testables.

La chaîne est de la forme :
```
Résultat principal
  → Corollaire 1 : implication pour les benchmarks textuels MAS
  → Corollaire 2 : implication pour les systèmes RLHF multi-agent
  → Corollaire 3 : implication pour les architectures hybrides
```

**Format de chaque corollaire dans le fichier :**
```
Corollaire N : [énoncé formel]
Hypothèses supplémentaires : [ce qui s'ajoute au résultat principal]
Prédiction testable : [ce qu'on doit observer expérimentalement]
Figure cible : Figure N
```

**Contrainte :** chaque corollaire doit déclarer explicitement ses hypothèses
supplémentaires au-delà du résultat principal. Aucune hypothèse cachée.

---

## Tâche 5 — LLM Council sur le framing de recherche (30 min)

Invoquer le **LLM Council** (5 sub-agents Claude Sonnet) sur la question suivante :

> « Le projet répond-il aux bonnes questions de recherche pour ICLR 2027,
> dans le bon ordre, avec la bonne portée ? Y a-t-il une question manquante
> ou mal positionnée qui affaiblirait la contribution aux yeux d'un reviewer ? »

**Contexte à fournir au Council :**
- Le fichier `theory/theorem71_formal.md` (définitions + énoncé visé)
- Le fichier `theory/corollary_framework.md` (corollaires)
- Cette phrase de contexte : *"Le papier cible ICLR 2027. Le résultat principal
  est un théorème d'impossibilité sur les canaux de communication dans les
  systèmes multi-agents. Les corollaires empiriques testent trois implications
  pratiques."*

**Ne pas donner au Council** : la structure du papier, les numéros de section,
le titre du projet, ni les expériences planifiées.

**Livrable :** `brainstorm/council-report-framing-S05.html` commité.

---

## Livrables Sprint 0.5

```
theory/theorem71_formal.md          ← version provisoire (définitions + énoncé visé)
theory/belnap_tbm_isomorphism.md    ← isomorphisme Belnap/TBM
theory/corollary_framework.md       ← chaîne déductive TIE → 3 corollaires
paper/EIP_paper_v0.1.md             ← squelette avec 8 sections vides + titres
brainstorm/council-report-framing-S05.html
reviews/REV-S0.5.md                 ← rapport Analyste Tâche 3
```

**`paper/EIP_paper_v0.1.md` — squelette attendu :**
```markdown
# [Titre — à déterminer]
## Abstract
[vide]
## 1. Introduction
[vide]
## 2. Background
[vide]
## 3. Résultat principal
### 3.1 Définitions
[pointer vers theory/theorem71_formal.md]
### 3.2 [section à nommer en Sprint ultérieur]
[vide]
### 3.3 [section à nommer en Sprint ultérieur]
[vide]
## 4. Epistemic Interface Problem
[vide]
## 5. CLAIM comme solution
[vide]
## 6. Validation expérimentale
[vide]
## 7. Limitations
[vide]
## 8. Discussion et travaux futurs
[vide]
```

> Note : les noms des sections 3.2 et 3.3 seront déterminés lors d'un sprint
> ultérieur, après que la démonstration aura précisé la structure du résultat.
> Ne pas les nommer ici pour ne pas anticiper la démonstration.

---

## Critère de passage Sprint 0.5

> **REV-S0.5 confirme que les trois conditions d'auditabilité sont indépendantes
> de la propriété cible (Q1 : pas d'hypothèse cachée). Score GNG-PAPER ≥ 65
> sur la section théorique. LLM Council ne soulève pas d'objection bloquante.**

Quand ce critère est atteint :
1. Mettre STATUS.md à jour : Sprint courant = 1, statut = PRÊT
2. Si le Council soulève une objection sur le framing : ouvrir QO-S05-01
   dans brainstorm/BR-008.md avant de passer à Sprint 1
3. Committer
4. Passer au fichier `SPRINT-1-context.md` (à créer)

---

## Score GNG-PAPER — application Sprint 0.5

Le score GNG-PAPER évalue uniquement la **rigueur théorique** pour ce sprint
(les autres dimensions seront évaluées dans les sprints expérimentaux).

**Grille pour Sprint 0.5 (25 points — rigueur théorique uniquement) :**

| Critère | Points | Question de vérification |
|---------|--------|--------------------------|
| Conditions (a)(b)(c) primitives et séparées | 8 | Chaque condition est-elle formulable sans référence aux autres ? |
| Absence d'hypothèse cachée (Q1 Analyste) | 8 | L'Analyste confirme : OUI, indépendantes |
| Énoncé-cible sans propriété P écrite | 5 | La propriété à dériver est-elle absente des définitions ? |
| Isomorphisme Belnap/TBM démontré | 4 | La bijection est-elle construite et la préservation vérifiée ? |

**Seuil :** ≥ 65% = 17/25 points → GO conditionnel pour Sprint 1

---

*Fichier de session — ne pas modifier après la session*
*Sprint 0.5 — v4 — Mai 2026*
