# REV-S7 — Rapport d'Analyste externe (Sprint 7, Tâche 7.2)
**Analyste :** Instance Opus 4.7 externe (extended thinking)
**Date :** Mai 2026
**Documents examinés :**
- `theory/theorem71_formal.md` (Sprint 0.5)
- `theory/lemme_auditabilite.md` (Sprint 7, Tâche 7.1 — commit `14926d0`)

---

## Question 1 — Non-circularité

> En lisant uniquement la démonstration du Lemme et les définitions de
> `theory/theorem71_formal.md` : la preuve suppose-t-elle à un moment quelconque
> une propriété de l'espace de sortie O ou de O_cert qui n'est pas explicitement
> dérivée des conditions (a), (b), (c) ?

**Réponse Analyste :** Non. La preuve du Lemme n'introduit aucune hypothèse
supplémentaire sur O ou O_cert. Toutes les propriétés utilisées sont dérivées
directement des conditions (a), (b), (c) :

- L'existence de l'injection ι : O_cert → Σ* découle de **(c)**.
- Le bon comportement de φ (procédure qui termine en temps fini) vient de **(a)**.
- Le lien avec le prédicat décidable Φ est donné par **(b)**.

La preuve ne fait jamais référence à la topologie de O, à une continuité, à une
métrique, ni à la dimension de ℳ. Aucune circularité.

**Verdict : GO**

---

## Question 2 — Nécessité des conditions

> Chacune des trois conditions (a), (b), (c) de la définition d'auditabilité
> est-elle réellement utilisée dans la preuve ?

**Réponse Analyste :** Les trois conditions sont nécessaires et explicitement
utilisées. Aucune ne peut être supprimée sans invalider la preuve.

| Condition | Utilisation | Conséquence si omise |
|---|---|---|
| (a) Décidabilité | Stratégie A étape A.2 ; Stratégie B (implicite pour bonne déf.) | O_cert n'est pas correctement caractérisé |
| (b) Prédicat | Stratégie A étape A.3 ; Stratégie B (implicite) | L'étape de décidabilité de ι(O_cert) tombe |
| (c) Représentation | Première étape des deux stratégies (A.1, B.1) | Cardinalité incontrôlable — le Lemme tombe immédiatement |

**Verdict : GO**

*Note : l'Analyste n'a pas tranché entre Stratégie A et Stratégie B. BR-010
reste en statut PROPOSÉ — décision reportée à l'itération 2 ou au-delà.*

---

## Question 3 — Suffisance pour le Théorème 7.1

> La dénombrabilité de O_cert (résultat du Lemme) est-elle suffisante pour que
> l'étape suivante de la preuve du Théorème 7.1 — « une application continue
> d'un espace connexe non-dénombrable vers un espace dénombrable est constante »
> — soit correcte ? Si O_cert est dénombrable mais muni d'une topologie
> non-discrète (héritée de O), le raisonnement de connectivité tient-il ?

**Réponse Analyste :** **Non.** Le Lemme ne suffit pas. Deux problèmes structurels :

### Problème G1 — L'image du canal n'est pas contrainte

La définition d'auditabilité ne dit pas que C(ℳ) ⊆ O_cert. Elle ne garantit que
l'existence d'un ensemble de sorties certifiables O_cert ⊆ O, mais le canal
pourrait très bien produire des sorties qui ne sont pas dans O_cert. Rien dans
(a), (b), (c) n'interdit que C(ℳ) contienne des éléments non certifiables. Or,
le Lemme ne porte que sur O_cert.

### Problème G2 — La topologie de O_cert n'est pas garantie discrète

Même si C(ℳ) ⊆ O_cert, O_cert hérite de la topologie de O (non spécifiée).
Un ensemble dénombrable peut être muni d'une topologie non-discrète
(par exemple ℚ dans ℝ avec la topologie usuelle). Une application continue
d'un espace connexe vers un espace dénombrable **n'est pas nécessairement
constante** — seul un espace totalement discontinu (ou discret) force la
constance via la connexité de l'image.

### Suggestions de l'Analyste

Pour rendre le Lemme suffisant dans le cadre du T7.1 :

1. Renforcer la définition d'auditabilité en exigeant explicitement C(ℳ) ⊆ O_cert.
2. Démontrer C(ℳ) ⊆ O_cert à partir de (a)(b)(c) + continuité de C (non évident).
3. Supposer que O est muni de la topologie discrète (ou que ses points sont isolés).

Aucune de ces précisions n'apparaît dans les fichiers fournis.

**Verdict : NO-GO → RETOUR Tâche 7.1 — renforcer l'énoncé du Lemme**

---

## Synthèse

| Question | Verdict | Conséquence |
|---|---|---|
| Q1 — Non-circularité | **GO** | Pas de re-démonstration nécessaire à l'itération 2 |
| Q2 — Nécessité (a)(b)(c) | **GO** | (a), (b), (c) restent dans la définition |
| Q3 — Suffisance pour T7.1 | **NO-GO** | RETOUR Tâche 7.1 — ouvrir QO-S7-01 |

**Décision Sprint 7 :** RETOUR Tâche 7.1, itération 2.
Ouvrir `QO-S7-01` dans `brainstorm/BR-010.md` pour tracer le gap topologique
et arbitrer entre les options de renforcement (décision PI — R-DEC-01).

**Score GNG-PAPER (Rigueur théorique) :** non finalisé. Q3 NO-GO suspend
l'évaluation finale jusqu'à correction. La preuve produite est correcte dans
ses bornes (GO sur Q1+Q2) mais insuffisante.

**Critère de passage Sprint 7 :** non atteint (Q3 NO-GO).
Sprint 4 (rédaction du papier) reste bloqué par `R-SEQ-01`.

---

## Conséquences pour les itérations suivantes

- **Q1 GO + Q2 GO** sont **acquis** : ne pas re-faire la preuve depuis zéro.
  La preuve actuelle (Stratégies A et B) reste valide comme **première étape**
  d'un Lemme renforcé.
- **Q3 NO-GO** nécessite soit un Lemme renforcé (conclusion topologique en plus
  de la dénombrabilité), soit un renforcement des hypothèses (définition
  d'auditabilité ou de canal, ou hypothèse supplémentaire dans T7.1).
- Le choix entre ces options est une **décision d'architecture** (R-DEC-01)
  qui revient au PI. Les options sont énumérées dans BR-010 §QO-S7-01.

---

*Sprint 7 — Tâche 7.2 — instance Opus 4.7 externe (extended thinking) — Mai 2026*
