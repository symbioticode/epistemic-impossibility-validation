# Session Sprint 4 — Rédaction du papier
**Chantier :** epistemic-impossibility-validation
**Durée estimée :** 2 jours
**Instance :** Claude Sonnet (rédaction) + Opus isolé (révision REV-FINAL)

> **Règle de session :** ce fichier et les fichiers commités listés ci-dessous
> sont le seul contexte de cette session.
> Commence par : `git pull` + lecture de `STATUS.md` + lecture des fichiers
> listés ci-dessous dans l'ordre indiqué.
> La source de vérité est le repo — pas cette conversation.

> **Principe de cette session :** tu rédiges le papier complet en intégrant
> tous les résultats produits dans les sprints précédents. Tu ne produis pas
> de nouveaux résultats, tu ne relances pas d'expériences, tu ne modifies pas
> les fichiers `theory/`. Ton seul objectif est `paper/EIP_paper_v0.3.md` —
> un papier soumettable à ICLR 2027.

---

## ⚠️ ADDENDUM — État Sprint 5 post-exécution (Mai 2026)
*À lire avant toute chose. Modifie les instructions des Tâches 4.2 et 4.3.*

### Ce qui a changé depuis la rédaction initiale de ce fichier

**Sprint 5 a été exécuté. Deux livrables sont disponibles :**
- `brainstorm/BR-007.md` — statut RÉSOLU, valeurs observées documentées
- `reviews/REV-S5.md` — rapport Analyste avec diagnostic de circularité

**Corollaire 1 (learning curves) — CONFIRMÉ, avec réserves de protocole :**
- Figure 2 disponible. Canal texte plafonne vs canal latent. p < 1e-40.
- Déviations de protocole à déclarer en Section 7 :
  - N=10 runs au lieu de 50 → QO-S5-03
  - 50 rounds au lieu de 200 → QO-S5-04
- La p-value absorbe ces déviations — Corollaire 1 reste présentable en Section 6.

**Corollaire 2 (propagation RLHF) — CIRCULAIRE PARTIELLE, résultat jacobien exploitable :**

Lecture directe de `rlhf_propagation.csv` (branche sprint-5) :

| κ | Signal round 0 | Signal round 1+ | jacobian_norm |
|---|---|---|---|
| 0.3 | ~1.3 (60% des runs) | 0.0 | ~0.073 constant |
| 0.6 | ~1.3 (50% des runs) | 0.0 | ~0.042 constant |
| 0.9 | 0.0 | 0.0 | **0.0** — graphe détaché dès l'init |

- Pour κ=0.9 : `jacobian_norm = 0.0` dès round 0 — détachement total du graphe
  confirmé. C'est le mécanisme encodé par détachement explicite (REV-S5 Q2).
- Pour κ=0.3 et κ=0.6 : le signal s'effondre à 0 dès round 1 malgré un jacobien
  non nul (~0.073 / ~0.042). Cause non résolue — bug de minimum local ou
  effondrement de la tâche. Non interprétable comme validation de H11.
- **Résultat exploitable** : la décroissance monotone du `jacobian_norm` avec κ
  (0.073 → 0.042 → 0.0) est indépendante du signal RLHF et cohérente avec le TIE.
  Ce résultat partiel est présentable en Section 7 comme observation préliminaire,
  pas comme validation du Corollaire 2. Voir instruction Section 7 point 6.
- `figures/figure3_rlhf_bound.pdf` — **NE PAS INTÉGRER** comme résultat principal.

**Condition D (conflit injecté, `conflict_results.csv`) — VALIDE AVEC ANOMALIE :**

Lecture directe de `conflict_results.csv` (branche main) :
- Structure correcte, 1200+ lignes, toutes conditions présentes.
- **Anomalie structurelle** : les valeurs de `jacobian_norm` sont identiques pour
  un même `(entropy_level, run_idx)` quel que soit le `conflict_level`. Le conflit
  injecté ne modifie pas le jacobien du canal C.
- Deux lectures possibles : (a) comportement attendu — `inject_conflict()` modifie
  la structure des masses m(∅) sans affecter le graphe de calcul du jacobien, ou
  (b) bug — le conflit est appliqué après le calcul du jacobien.
- La colonne `m_vide` confirme bien que m_vide = conflict_level à chaque ligne —
  la manipulation des masses est fonctionnelle.
- **Instruction pour Section 6.3** : présenter l'effet du conflit sur `m_vide` et
  `output_entropy`, pas sur `jacobian_norm`. Déclarer explicitement l'absence d'effet
  sur le jacobien et sa lecture (QO-S2-05 si non déjà ouvert).

---

## Fichiers à lire avant de commencer (dans cet ordre)

```
1. theory/tie_formal.md       ← TIE démontré, H1–H4, Étapes 0–6 (Sprint 7)
2. theory/lemme_auditabilite.md     ← Lemme démontré, Stratégies A+B (Sprint 7)
3. theory/belnap_tbm_isomorphism.md ← Isomorphisme Belnap/TBM (Sprint 0.5)
4. theory/corollary_framework.md    ← Chaîne déductive TIE → Corollaires 1-3 (Sprint 0.5)
5. paper/EIP_paper_v0.1.md          ← Squelette 8 sections (Sprint 0.5)
6. results/raw_results.csv          ← Données expérimentales principales (Sprint 2)
7. figures/figure1_gradient_entropy.pdf  ← Figure 1 validée (Sprint 3)
8. figures/table1_main_results.md   ← Table 1 (Sprint 3)
9. figures/table2_stats.md          ← Table 2 tests statistiques (Sprint 3)
10. figures/table3_calibration.md   ← Table 3 calibration γ_i (Sprint 3)
11. reviews/REV-S7.md               ← Rapport Analyste Sprint 7 + addendum clôture
12. brainstorm/BR-010.md            ← Décision PI : Stratégie B adoptée, ζ+γ adopté
13. brainstorm/BR-007.md            ← Sprint 5 résolu : Corollaire 1 confirmé, Corollaire 2 circulaire (QO-S5-02)
14. reviews/REV-S5.md               ← Diagnostic circularité RLHF + déviations protocole
```

**Ne pas lire :** les fichiers `src/`, les fichiers `brainstorm/` autres que BR-010
et BR-007, ni aucun fichier de session précédent.

**Lire au moment de la Section 6.3 uniquement :** `results/conflict_results.csv`
(branche main — 1200+ lignes). Voir instruction Section 6.3 ci-dessous.

---

## Ce que tu dois savoir sur ce sprint

### État du chantier à l'entrée de Sprint 4

**Théorie (Sprint 7 — CLOS) :**
- Le TIE est démontré en 6 étapes + Étape 0 (Lemme).
- Hypothèses : H1 (canal, O métrique, C continue, ℳ connexe dim > 0), H2 (gradient-preserving), H3 (auditable — conditions a/b/c), H4 (C(ℳ) ⊆ O_cert, hypothèse ζ).
- Le Lemme utilise la **Stratégie B** (représentation directe, dénombrabilité de Σ*) comme preuve principale. Stratégie A conservée en annexe.
- Renforcement γ+ζ adopté : O espace métrique (§1), H4 ajoutée (§5).
- REV-S7 : Q1 GO, Q2 GO, Q3 NO-GO levé par ζ+γ. Clôture PI sans re-soumission Analyste (justification dans addendum REV-S7.md).

**Expériences (Sprints 2–3) :**
- Figure 1 : jacobien canal A s'effondre quand entropie → 0, canal B stable.
- Tables 1, 2, 3 : valeurs vérifiées par Haiku (REV-S3 Q1 confirmé).

**Ce sprint ne modifie pas :**
- `theory/tie_formal.md` (sera renommé en `tie_formal.md` — voir Tâche 4.4)
- `theory/lemme_auditabilite.md`
- les données dans `results/`
- les figures dans `figures/`

### Décisions BR en vigueur

| Décision | Statut | Impact Sprint 4 |
|---|---|---|
| BR-010 : Stratégie B principale | RÉSOLU | Section 3.2 présente Stratégie B ; Stratégie A en annexe |
| BR-010 §QO-S7-01 : ζ+γ adopté | RÉSOLU | H4 déclarée dans Section 3.3 ; γ (O métrique) dans §3.1 |
| BR-002 : calibration γ_i | OUVERT (QO-V-06) | Table 3 et Section 7 déclarent la limite |

---

## Tâche 4.1 — Rédaction des sections théoriques (0.75 jour)

**Fichier :** `paper/EIP_paper_v0.3.md` — à créer depuis le squelette `EIP_paper_v0.1.md`

### Section 3.1 — Définitions

Rédiger à partir de `theory/tie_formal.md` §1–§4 :

- **Canal C** : ℳ variété riemannienne lisse connexe dim > 0 ; **O espace métrique** (noter la modification γ et son rôle) ; C continue.
- **Gradient-preserving** : ∃ c > 0, ‖J_C(h)‖₂ ≥ c ∀h ∈ ℳ.
- **Auditable** : conditions (a) décidabilité, (b) prédicat de validation, (c) représentation. Formulées verbatim depuis §3 de `tie_formal.md` — ne pas reformuler.
- Exemples §4 (JSON, formules logiques, fonctions de masse) — intégrer comme illustration après la définition formelle.

> **Contrainte R-TRL-PAPER-01 :** ne pas écrire que les conditions (a)(b)(c) sont
> « naturelles » ou « minimales » sans le justifier — REV-S7 Q2 confirme qu'elles
> sont nécessaires ; c'est ce qu'on peut écrire.

### Section 3.2 — Lemme d'auditabilité-discrétion

Présenter le Lemme comme **résultat intermédiaire** (R-LEMME-03), pas comme contribution principale.

Structure recommandée :
```
Lemme 1 (Auditabilité → Discrétion). Si C est auditable au sens de (a)(b)(c),
alors O_cert est au plus dénombrable.

Preuve. [Stratégie B — 4 étapes, références Sipser 2013 et Hrbacek-Jech 1999]
          [Renvoyer à theory/lemme_auditabilite.md pour la Stratégie A alternative]
```

La nouveauté du Lemme est sa **fonction** (fermer le trou dans la preuve du TIE),
pas sa difficulté mathématique intrinsèque. Le formuler ainsi.

### Section 3.3 — Théorème 7.1 (TIE)

Présenter le TIE complet avec les 4 hypothèses H1–H4 et les 6 étapes + Étape 0.

**Point de vigilance sur H4 :**
H4 (C(ℳ) ⊆ O_cert) doit être présentée de façon transparente, pas minimisée.
Formuler : *« Un canal auditable dont on étudie les propriétés de certification
est naturellement supposé certifier toutes ses sorties effectives — H4 rend
cette exigence explicite. »*

**Renommage dans le corps du texte :**
À partir de cette section, utiliser **TIE** (Théorème d'Impossibilité Épistémique)
au lieu de « Théorème 7.1 ». Toutes les occurrences de « Théorème 7.1 » dans
le papier deviennent « TIE ». (Voir aussi Tâche 4.4.)

### Section 3.4 — Généralisation Information Bottleneck + Figure 1

Rattacher Figure 1 (résultat expérimental) à la Section 3 :
- Canal A (texte) = implémentation approchée d'un canal auditable → jacobien → 0
- Canal B (latent) = canal gradient-preserving → jacobien stable
- Le pattern observé est cohérent avec le TIE (ne pas écrire « confirme » —
  l'expérience illustre, la preuve démontre)

Insérer Figure 1 et Table 1 ici.

---

## Tâche 4.2 — Rédaction des sections empiriques (0.5 jour)

### Section 4 — Epistemic Interface Problem

Définir formellement l'EIP comme la conséquence pratique du TIE :
tout système multi-agents qui requiert simultanément expressivité (gradient)
et auditabilité (certification) se heurte à une incompatibilité structurelle.

Intégrer Table 2 (tests statistiques) et Table 3 (calibration).

### Section 5 — CLAIM comme solution

Présenter les 5 invariants de la structure CLAIM (depuis `theory/belnap_tbm_isomorphism.md`)
et le rôle de l'orchestrateur comme traversée γ_i de la frontière latent/symbolique.

> **Contrainte §5.5 :** harmoniser la terminologie Belnap flou avec
> `theory/belnap_tbm_isomorphism.md` — utiliser les notations exactes de ce fichier
> (états {T, F, B, N}, isomorphisme γ, fonctions de masse sur {T,F,B,N}).

### Section 6 — Validation expérimentale

- **6.1** : Figure 1 déjà intégrée en Section 3.4 — renvoi.

- **6.2** : Figure 2 (courbes d'apprentissage) — **disponible, intégrer**.
  Lire `figures/figure2_learning_curves.pdf`.
  Déclarer en note : N=10 runs (déviation R-STAT-02, QO-S5-03) et 50 rounds
  (QO-S5-04). La p < 1e-40 maintient la conclusion malgré les déviations.

- **6.3** : Résultats condition D — lire `results/conflict_results.csv`.
  L'effet du conflit porte sur `m_vide` (= conflict_level, confirmé) et
  `output_entropy`, **pas sur `jacobian_norm`** (invariant quel que soit
  conflict_level — voir anomalie documentée dans l'addendum).
  Décrire : (a) l'augmentation de m(∅) avec conflict_level, (b) l'effet
  sur output_entropy, (c) déclarer explicitement l'absence d'effet sur
  jacobian_norm avec la lecture retenue (comportement attendu ou QO-S2-05).

- **6.4** : Figure 4 (hybride — Sprint 6) — `[PLACEHOLDER — Sprint 6 en cours]`

- **6.5** : Table corrélation cachée (Rule O3 — Sprint 6) — `[PLACEHOLDER — Sprint 6 en cours]`

> ⚠️ **Figure 3 (RLHF) — NE PAS INTÉGRER.** La simulation du Corollaire 2
> est circulaire (H11 encodée par détachement autograd, non testée empiriquement —
> voir BR-007 QO-S5-02 et REV-S5 Q2). `figures/figure3_rlhf_bound.pdf` est
> invalide. La sous-section RLHF est supprimée de Section 6.

> **Règle des placeholders :** tout placeholder est marqué explicitement
> `[PLACEHOLDER — Sprint N en cours]` avec le livrable attendu.
> Ne pas laisser de section vide sans marquage. (#18 Debt Visibility)

### Section 7 — Limitations

Déclarer **explicitement** (R-TRL-PAPER-01) :

1. **Généralité du modèle** : expériences sur GPT-2 small (117M). Validité du TIE
   sur d'autres architectures = travaux futurs (QO-V-01 fermée pour GPT-2 ;
   généralisation = travaux futurs Section 8).

2. **Calibration γ_i** : QO-V-06 reste ouverte (k-NN suffisance non confirmée).
   Si Table 3 montre corrélation < 0.50 : déclarer comme limite du claim
   sur le canal C, pas masquer.

3. **Portée du Lemme — condition (c) et finitude de l'alphabet** :
   La Stratégie B repose sur la dénombrabilité de Σ*. Si l'alphabet de
   certification est infini (précision arbitraire), Σ* reste dénombrable
   (Σ dénombrable ⇒ Σ* dénombrable). La Stratégie A reste valide dans
   tous les cas. Déclarer la limite pratique : les systèmes CLAIM avec
   cadre de discernement infini ne sont pas couverts par les exemples §4.

4. **Hypothèse H4 (ζ)** : déclarer que H4 est une hypothèse explicite,
   non dérivée de (a)(b)(c) — transparence sur le renforcement adopté.

5. **Hypothèse γ (O métrique)** : déclarer les espaces de sortie non-métrisables
   comme hors du scope de la version actuelle du TIE.

6. **Corollaire 2 (borne RLHF) — validation partielle uniquement** :
   La simulation Sprint 5 a encodé la prédiction H11 via détachement explicite
   du graphe autograd pour κ=0.9 (REV-S5 Q2, BR-007 QO-S5-02) — le test
   multi-round est circulaire et non présentable.
   **Résultat partiel exploitable** : la décroissance monotone du jacobien du
   canal CLAIM avec κ (‖J‖ ≈ 0.073 pour κ=0.3, 0.042 pour κ=0.6, 0.0 pour
   κ=0.9, N=10 runs) est cohérente avec le TIE et indépendante du mécanisme
   de détachement. Présenter comme observation préliminaire, pas comme
   validation du Corollaire 2. La validation complète requiert une architecture
   où l'auditabilité est une propriété externe du canal — renvoi Section 8.

7. **Déviations de protocole Sprint 5** : les courbes d'apprentissage (Figure 2)
   ont été produites avec N=10 runs (QO-S5-03) et 50 rounds au lieu de 200
   (QO-S5-04). La p < 1e-40 maintient la conclusion du Corollaire 1 malgré
   ces déviations. La réplication à pleine échelle (N=50, 200 rounds) est
   laissée aux travaux futurs.

8. **Condition D — absence d'effet du conflit sur le jacobien** : dans
   `conflict_results.csv`, `jacobian_norm` est invariant par rapport à
   `conflict_level` pour un même `(entropy_level, run_idx)`. L'effet du
   conflit injecté se manifeste uniquement sur m(∅) et `output_entropy`.
   Déclarer cette limite de portée de la Condition D : l'injection de conflit
   éistémique n'affecte pas le gradient du canal dans cette implémentation.

---

## Tâche 4.3 — REV-FINAL par l'Analyste (0.5 jour)

Après avoir commité `paper/EIP_paper_v0.3.md`, invoquer une **instance Opus
séparée** (extended thinking activé) sans accès à la conversation de travail.

**Fournir à l'Analyste uniquement :**
- `paper/EIP_paper_v0.3.md`
- `theory/tie_formal.md`
- `theory/lemme_auditabilite.md`
- `figures/figure1_gradient_entropy.pdf`

**Soumettre ces 7 questions exactement :**

**Q1 — Présentation du Lemme**
> Le Lemme est-il présenté de façon à ce que sa nouveauté soit claire sans
> survente ? En particulier : le papier distingue-t-il correctement la nouveauté
> du Lemme (sa fonction dans la chaîne de preuve) de sa difficulté mathématique
> intrinsèque (faible) ?

**Q2 — Cohérence empirique / théorique**
> Les résultats empiriques (Figure 1, Tables 1–2) supportent-ils le TIE sans
> survente ? Le papier distingue-t-il clairement ce que la preuve démontre
> et ce que les expériences illustrent ?

**Q3 — Explications alternatives**
> Y a-t-il des explications alternatives aux résultats observés que les auteurs
> n'ont pas considérées ? En particulier : l'effondrement du jacobien du canal
> texte à faible entropie pourrait-il s'expliquer par un artefact de
> l'implémentation GPT-2 small plutôt que par le TIE ?

**Q4 — Reproductibilité**
> Le protocole décrit dans le papier est-il reproductible par une équipe tierce
> sans contact avec les auteurs ? Identifier tout paramètre non déclaré ou
> toute étape ambiguë dans la description expérimentale.

**Q5 — Soumettabilité ICLR 2027**
> Le papier, dans son état actuel, est-il soumettable à ICLR 2027 ?
> Identifier les points bloquants (format, scope, claim) s'il y en a.

**Q6 — Rigueur théorique**
> La définition d'auditabilité en trois conditions (a)(b)(c) + H4 est-elle
> suffisamment rigoureuse pour une communauté de théoriciens de l'information ?
> H4 sera-t-elle perçue comme ad hoc ou comme une clarification transparente ?

**Q7 — Positionnement concurrents**
> Le positionnement par rapport à RecursiveMAS (Yang et al. 2026) est-il équitable ?
> Le papier reconnaît-il honnêtement ce que RecursiveMAS fait et ne fait pas ?

**Critères de passage REV-FINAL :**
- Q1–Q7 : réponses GO ou GO conditionnel avec corrections mineures documentées
- Score GNG-PAPER ≥ 75 global (seuil PROGRESSION.md Sprint 4)
- Si une réponse est NO-GO : corrections ciblées et re-soumission Q concernée

Commiter le rapport dans `reviews/REV-FINAL.md`.

---

## Tâche 4.4 — Renommage et nettoyage final (0.25 jour)

**Action 1 — Renommage (commité séparément) :**
```bash
git mv theory/tie_formal.md theory/tie_formal.md
```
Mettre à jour tous les renvois internes :
- `paper/EIP_paper_v0.3.md` : tous les renvois vers `tie_formal.md` → `tie_formal.md`
- `theory/lemme_auditabilite.md` : renvoi dans l'Énoncé et les Définitions utilisées
- `CLAUDE.md` §Convention de nommage (si elle existe)

**Action 2 — Remplacement terminologique dans `paper/` :**
Toutes les occurrences de « Théorème 7.1 » → « TIE » dans le corps du texte.
Conserver « Théorème 7.1 » uniquement dans les références formelles
(e.g. « Theorem 1 (TIE) » en en-tête, une fois).

**Action 3 — Vérification finale :**
```bash
grep -r "Théorème 7.1" paper/   # doit retourner 0 ou 1 occurrence (label formel)
grep -r "tie_formal" .    # doit retourner 0 (tous renvois mis à jour)
```

---

## Livrables Sprint 4

```
paper/EIP_paper_v0.3.md     ← Papier complet (sections 1–8, placeholders marqués)
theory/tie_formal.md        ← tie_formal.md renommé (git mv)
reviews/REV-FINAL.md        ← Rapport Analyste — 7 questions
```

**Commit Tâche 4.1–4.2 :** `[SPRINT-4] draft EIP_paper_v0.3 : sections 1-7`
**Commit Tâche 4.3 :** `[SPRINT-4] add REV-FINAL : reviews/REV-FINAL.md`
**Commit Tâche 4.4 :** `[SPRINT-4] rename tie_formal → tie_formal : R-DOC-01`

`STATUS.md` mis à jour : Sprint courant = 5, statut = PRÊT.

---

## Critère de passage Sprint 4

> **`paper/EIP_paper_v0.3.md` : sections 1–7 rédigées, placeholders marqués.**
> **`reviews/REV-FINAL.md` : 7 questions GO ou GO conditionnel.**
> **Score GNG-PAPER ≥ 75 global.**
> **`git mv` tie_formal → tie_formal commité.**
> **0 occurrence de "Théorème 7.1" non labelisée dans `paper/`.**

**No-Go partiel :** si REV-FINAL Q3 (explications alternatives) retourne NO-GO,
ajouter un paragraphe §7 « Menaces à la validité » avant de re-soumettre Q3.
Ne pas relancer l'expérience pour répondre à une objection rédactionnelle.

---

## Structure attendue de `paper/EIP_paper_v0.3.md`

```markdown
# [Titre — à confirmer par le PI]
## Abstract
[Claim en 1 phrase + méthode + résultat principal chiffré]

## 1. Introduction — La dichotomie manquante
## 2. Background — Latent MAS, protocoles, belief functions
## 3. Résultat principal
### 3.1 Définitions (canal, gradient-preserving, auditable H1–H4)
### 3.2 Lemme d'auditabilité-discrétion
### 3.3 Théorème d'Impossibilité Épistémique (TIE) — preuve complète
### 3.4 Généralisation IB + Figure 1
## 4. Epistemic Interface Problem — Définition formelle
## 5. CLAIM comme solution — 5 invariants + orchestrateur
### 5.5 Terminologie Belnap flou [harmonisée avec belnap_tbm_isomorphism.md]
## 6. Validation expérimentale
### 6.1 Figure 1 — renvoi Section 3.4
### 6.2 Figure 2 — Courbes d'apprentissage (Corollaire 1, Sprint 5 ✅)
### 6.3 Condition D — conflit injecté (conflict_results.csv ✅)
### 6.4 Figure 4 — [PLACEHOLDER Sprint 6]
### 6.5 Table Rule O3 — [PLACEHOLDER Sprint 6]
## 7. Limitations
## 8. Discussion et travaux futurs
   [inclure §Corollaire 2 — prédiction théorique non testée empiriquement]
## Références
## Annexe A — Stratégie A (calculabilité) du Lemme
```

---

## Paramètres ICLR 2027 de référence (R-ICLR-01)

| Contrainte | Valeur |
|---|---|
| Pages maximum | 9 (corps) + références illimitées |
| Format | Double colonne, LaTeX ICLR template |
| Anonymisation | Double-blind — pas de noms d'auteurs dans `v0.3` |
| Figures | Lisibles en noir et blanc |
| Code | Lien repo anonymisé si applicable |

> **Note :** `EIP_paper_v0.3.md` est en Markdown — conversion LaTeX en Sprint 4 final
> ou Sprint suivant. Pour ce sprint : Markdown avec structure complète et contenu réel.
> La mise en forme LaTeX n'est pas un critère de passage Sprint 4.

---

## Règles applicables à cette session

| Règle | Application concrète |
|---|---|
| `R-SEQ-01` | Sprint 4 débloqué — REV-S7 clos (Q1 GO, Q2 GO, Q3 levé par ζ+γ, addendum PI) |
| `R-LEMME-03` | Lemme présenté comme résultat intermédiaire, pas contribution principale |
| `R-TRL-PAPER-01` | Ne pas écrire de claim plus fort que ce que démontrent la preuve et les expériences |
| `R-DOC-01` | Renommage tie_formal → tie_formal dans Tâche 4.4 |
| `R-ICLR-01` | 9 pages max, double-blind, figures noir-et-blanc lisibles |
| `R-PREUVE-02` | H1–H4 explicitement déclarées dans §3.3 — aucune hypothèse cachée |
| `#1 Ground Truth or Silence` | Placeholders marqués explicitement — figure3 invalide NON intégrée |
| `#4 No Hidden State` | H4 (ζ) et modification γ (O métrique) déclarées et justifiées dans le papier |
| `#18 Debt Visibility` | QO-V-06, QO-S5-02, QO-S5-03, QO-S5-04, QO-S2-05 toutes déclarées en Section 7 |

---

*Fichier de session — ne pas modifier après la session*
*Sprint 4 — v4 — Mai 2026*
