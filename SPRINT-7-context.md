# Session Sprint 7 — Lemme de non-circularité
**Chantier :** epistemic-impossibility-validation
**Durée estimée :** 2 jours
**Instance :** Opus 4.7 + extended thinking (Tâches 7.1 et 7.3)
**Instance séparée :** Opus isolé pour Tâche 7.2 (Analyste)

> **Règle de session :** ce fichier et les fichiers commités listés ci-dessous
> sont le seul contexte de cette session.
> Commence par : `git pull` + lecture de `STATUS.md` + lecture des 4 fichiers
> listés ci-dessous.
> La source de vérité est le repo — pas cette conversation.

> **Principe de cette session :** tu démontres le Lemme.
> Tu pars des définitions formelles telles qu'elles ont été commités en Sprint 0.5.
> Tu ne reçois pas de stratégie de preuve. Tu trouves la démonstration
> à partir des définitions et de l'énoncé ci-dessous.
> Si plusieurs stratégies sont possibles, produis-les toutes — l'Analyste choisit.

---

## Fichiers à lire avant de commencer (dans cet ordre)

```
1. theory/tie_formal.md       ← définitions + énoncé-cible (Sprint 0.5)
2. theory/belnap_tbm_isomorphism.md ← isomorphisme Belnap/TBM (Sprint 0.5)
3. reviews/REV-S0.5.md              ← rapport Analyste Sprint 0.5
4. brainstorm/BR-010.md             ← décision de preuve (statut PROPOSÉ)
```

**Ne pas lire :** les autres fichiers `brainstorm/`, les fichiers `src/`,
les fichiers `results/`, les fichiers `figures/`,
ni aucun fichier de session précédent.

---

## Ce que tu dois savoir sur ce sprint

Le Théorème 7.1 (énoncé dans `theory/tie_formal.md`) affirme qu'un canal
de communication ne peut pas être simultanément gradient-preserving et auditable.

La preuve de ce théorème comporte une étape qui suppose que l'espace de sortie
d'un canal auditable est dénombrable. Cette propriété n'est pas dans la définition
de l'auditabilité telle que tu vas la lire dans `theory/tie_formal.md` —
elle doit en être dérivée.

**Ce sprint produit cette dérivation : le Lemme d'auditabilité-discrétion.**

Sans ce Lemme, la preuve du Théorème 7.1 suppose ce qu'elle cherche à démontrer.
Avec ce Lemme, elle démontre une contrainte réelle sur l'architecture des canaux.

---

## Tâche 7.1 — Démonstration du Lemme (1 jour)

### Énoncé à démontrer

> **Lemme (Auditabilité → Discrétion)**
>
> Soit C un canal de communication dont l'espace de sortie est O.
> Soit O_cert = {o ∈ O | M(o) = "valide"} l'ensemble des sorties certifiées.
>
> Si C est auditable au sens des conditions (a), (b), (c) définies dans
> `theory/tie_formal.md` (version commité en Sprint 0.5),
>
> alors O_cert est au plus dénombrable.

### Instructions

**Étape préalable obligatoire :** lire les conditions (a), (b), (c) dans
`theory/tie_formal.md`. La preuve doit partir uniquement de ces
conditions telles qu'elles sont formulées dans ce fichier — pas d'une
reformulation, pas d'une hypothèse supplémentaire non déclarée.

**Ce que la preuve doit satisfaire :**

1. **Non-circularité :** aucune étape de la preuve ne peut supposer que O
   est discret, que O_cert est dénombrable, ou que M produit un résultat dans
   un espace fini. Ces propriétés doivent être *dérivées* des conditions
   (a), (b), (c), pas *supposées*.

2. **Primitives utilisées :** la preuve ne peut utiliser que des résultats
   standards de théorie des ensembles, théorie de la calculabilité, ou
   topologie — correctement référencés. Si tu utilises un théorème, nomme-le.

3. **Conditions nécessaires :** si la preuve n'utilise pas l'une des trois
   conditions (a), (b), (c), déclare-le explicitement. Une condition non
   utilisée est soit superflue (affaiblir la définition), soit indispensable
   à une autre étape non encore écrite.

**Format de la démonstration dans `theory/lemme_auditabilite.md` :**

```markdown
# Lemme d'auditabilité-discrétion

## Énoncé
[reprendre l'énoncé ci-dessus verbatim]

## Définitions utilisées
[lister les conditions (a), (b), (c) avec leur numéro dans tie_formal.md]

## Démonstration

### [Nom de la stratégie — à choisir]
[numéroter les étapes]
[indiquer quelle condition est utilisée à chaque étape]
[référencer tout théorème externe utilisé]

## Conditions utilisées
- Condition (a) : [utilisée à l'étape N / non utilisée — raison]
- Condition (b) : [utilisée à l'étape N / non utilisée — raison]
- Condition (c) : [utilisée à l'étape N / non utilisée — raison]

## Ce que cette preuve ne suppose pas
[liste explicite des propriétés qui sont dérivées, pas supposées]
```

**Si plusieurs stratégies de preuve sont possibles :**
produis chacune dans une section séparée, avec le même format.
L'Analyste (Tâche 7.2) choisira la preuve principale. Ne choisit pas
à sa place — présente les options avec leurs forces et faiblesses.

**Si la démonstration révèle que l'énoncé est faux :**
documente la contre-démonstration, les conditions qui manquent, et
ouvre `QO-S7-01` dans `brainstorm/BR-010.md`. Ne pas masquer.
(`#7 Fail Fast, Explain Faster` — `#18 Debt Visibility`)

---

## Tâche 7.2 — Vérification par l'Analyste (0.5 jour)

Après avoir produit et commité `theory/lemme_auditabilite.md`,
invoquer une **instance Opus séparée** (extended thinking activé).

**Fournir à l'Analyste uniquement :**
- `theory/tie_formal.md` (commité)
- `theory/lemme_auditabilite.md` (commité)

**Ne pas fournir à l'Analyste :** la présente conversation, ce fichier de session,
ni aucun contexte sur la façon dont la démonstration a été produite.

**Soumettre ces trois questions :**

**Question 1 — Non-circularité**
> En lisant uniquement la démonstration du Lemme et les définitions de
> `theory/tie_formal.md` : la preuve suppose-t-elle à un moment quelconque
> une propriété de l'espace de sortie O ou de O_cert qui n'est pas
> explicitement dérivée des conditions (a), (b), (c) ?
> Si oui : identifier l'étape et la propriété supposée.

**Question 2 — Nécessité des conditions**
> Chacune des trois conditions (a), (b), (c) de la définition d'auditabilité
> est-elle réellement utilisée dans la preuve ?
> Pour chaque condition non utilisée : la preuve reste-t-elle valide sans elle ?
> Si oui : la définition est trop forte et doit être allégée.

**Question 3 — Suffisance pour le Théorème 7.1**
> La dénombrabilité de O_cert (résultat du Lemme) est-elle suffisante pour
> que l'étape suivante de la preuve du Théorème 7.1 — « une application
> continue d'un espace connexe non-dénombrable vers un espace dénombrable
> est constante » — soit correcte ?
> En particulier : si O_cert est dénombrable mais muni d'une topologie
> non-discrète (héritée de O), le raisonnement de connectivité tient-il ?
> Justifier.

**Critères de passage :**
- Q1 : pas de circularité détectée → **GO**
- Q1 : circularité identifiée → **RETOUR Tâche 7.1** avec diagnostic
- Q2 : toutes les conditions nécessaires → **GO**
- Q2 : condition superflue identifiée → **GO conditionnel** (allégement documenté dans BR-010)
- Q3 : dénombrabilité suffisante → **GO**
- Q3 : propriété plus forte requise → **RETOUR Tâche 7.1** pour renforcer l'énoncé

Commiter le rapport Analyste dans `reviews/REV-S7.md`.

---

## Tâche 7.3 — Intégration dans Théorème 7.1 (0.5 jour)

Après un verdict GO de l'Analyste sur les trois questions :

**Fichier à modifier :** `theory/tie_formal.md`

Ajouter le Lemme comme étape explicite dans la preuve du Théorème 7.1.
Le Lemme doit apparaître comme **Étape 0** ou **Lemme préliminaire**,
avec un renvoi vers `theory/lemme_auditabilite.md`.

**Contrainte de rédaction :** la version mise à jour de `tie_formal.md`
doit être auto-contenue — un lecteur qui lit uniquement ce fichier doit
pouvoir suivre la preuve complète, avec les renvois explicites vers le Lemme.

**Ce qui ne change pas :** les hypothèses H1, H2, H3 et les définitions
des conditions (a), (b), (c) restent identiques à la version Sprint 0.5.
Seule la structure de la preuve change pour intégrer l'Étape 0.

**Après modification :** relire `theory/tie_formal.md` entier et vérifier :
- La preuve est-elle complète de H1/H2/H3 à la conclusion, sans saut ?
- Chaque étape référence-t-elle son fondement (lemme, définition, théorème externe) ?
- Les hypothèses non utilisées sont-elles déclarées comme telles ?

(`#4 No Hidden State` — `#8 No Silent Assumptions`)

---

## Livrables Sprint 7

```
theory/lemme_auditabilite.md    ← NOUVEAU (démonstration du Lemme)
theory/tie_formal.md      ← MIS À JOUR (Étape 0 intégrée)
reviews/REV-S7.md               ← Rapport Analyste (Q1, Q2, Q3)
brainstorm/BR-010.md            ← MIS À JOUR (statut ADOPTÉ ou retour)
```

**Commit final :** `[SPRINT-7] prove lemme auditabilite-discretion : theory/lemme_auditabilite.md`
`STATUS.md` mis à jour : Sprint courant = 4 (si GO), statut = PRÊT.

---

## Critère de passage Sprint 7

> **REV-S7 : Q1 GO (pas de circularité), Q2 GO ou GO conditionnel,
> Q3 GO avec justification topologique.**
> **Score GNG-PAPER ≥ 70 sur Rigueur théorique.**

**No-Go absolu :** si Q1 revient avec circularité après deux itérations
de Tâche 7.1, ouvrir `QO-S7-02` et escalader vers le PI avant de continuer.
Un Lemme circulaire ne peut pas être corrigé par itération — il faut
revoir les définitions de Sprint 0.5 (`R-LEMME-02`).

**Note sur `R-SEQ-01` :** Sprint 4 (rédaction du papier) ne peut pas
démarrer sans un verdict GO sur les trois questions de REV-S7.
Cette contrainte est non-négociable.

---

## Règles applicables à cette session

| Règle | Application concrète |
|-------|----------------------|
| `R-LEMME-01` | La preuve du Lemme ne peut pas référencer le Théorème 7.1 |
| `R-LEMME-02` | Utiliser exactement les conditions (a)(b)(c) de Sprint 0.5 ; toute modification → BR-010 |
| `R-LEMME-03` | Le Lemme est un résultat intermédiaire, pas la contribution principale |
| `R-PREUVE-01` | La preuve n'est complète qu'après confirmation Analyste |
| `R-PREUVE-02` | Toutes les hypothèses sont explicitées |
| `#1 Ground Truth or Silence` | β=T uniquement si la preuve est complète ; β=B si deux stratégies contradictoires |
| `#4 No Hidden State` | Toute hypothèse implicite sur O ou O_cert est déclarée |
| `#7 Fail Fast` | Si l'énoncé est faux : documenter, pas masquer |
| `#18 Debt Visibility` | Toute étape non démontrée est tracée comme QO-S7-XX |
| `#20 Qualified Silence` | β=N si une condition n'a pas été examinée ; ne pas inférer |

---

## Ce que ce fichier ne contient pas intentionnellement

Ce fichier ne contient pas les stratégies de preuve candidates,
ni les théorèmes externes suggérés, ni la formulation cible de l'Étape 0
dans le Théorème 7.1. Ces éléments sont dans les documents de pilotage
(réservés au PI) pour éviter que l'instance de travail adapte sa démonstration
à une réponse attendue plutôt qu'à une vérité mathématique.

Si tu identifies naturellement une stratégie de preuve et qu'elle te semble
solide : l'utiliser. Si l'Analyste la confirme, elle sera adoptée.
C'est le processus correct.

---

*Fichier de session — ne pas modifier après la session*
*Sprint 7 — v4 — Mai 2026*
