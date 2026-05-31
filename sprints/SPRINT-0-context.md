# Session Sprint 0 — Préparation infrastructure
**Chantier :** epistemic-impossibility-validation
**Durée estimée :** 2 heures
**Instance :** manuelle (chercheur) + Claude Code Web pour init_project.sh

> **Règle de session :** ce fichier est le seul contexte de cette session.
> Ne pas injecter la méthodologie complète, le BR complet, ni les sprints suivants.
> La source de vérité après cette session est le repo GitHub, pas cette conversation.

---

## Ce que tu dois savoir sur ce chantier

Tu initialises le repo d'un projet de recherche en ML/théorie de l'information.
Le projet vise à valider expérimentalement un théorème mathématique sur les systèmes
multi-agents et à produire un papier soumettable à ICLR 2027.

Le chantier comporte plusieurs sprints. **Tu n'as besoin d'en connaître aucun autre
que Sprint 0 pour cette session.** Ton seul objectif est de produire une infrastructure
de repo fonctionnelle, vide, et reproductible.

---

## Identité du projet

```
NOM_CHANTIER      : epistemic-impossibility-validation
TARGET_CONF       : ICLR 2027
DEADLINE_SOUM     : Octobre 2026
PI                : Andrei
CO_AUTEURS        : [à compléter]
```

---

## Arborescence cible à créer

```
epistemic-impossibility-validation/
├── README.md                        ← squelette (titre + sections vides)
├── CHANGELOG.md                     ← vide avec en-tête
├── QUICK_START.md                   ← vide avec en-tête
├── REPO_STRUCTURE.md                ← vide avec en-tête
├── STATUS.md                        ← voir contenu ci-dessous
├── VARIABLES.md                     ← voir contenu ci-dessous (8 blocs)
├── CLAUDE.md                        ← voir contenu ci-dessous
├── requirements.txt                 ← voir contenu ci-dessous
├── init_project.sh                  ← script qui crée l'arborescence
│
├── theory/
│   ├── tie_formal.md          ← squelette vide (sera rempli Sprint 0.5)
│   ├── belnap_tbm_isomorphism.md    ← squelette vide (sera rempli Sprint 0.5)
│   ├── corollary_framework.md       ← squelette vide (sera rempli Sprint 0.5)
│   └── lemme_auditabilite.md        ← squelette vide (sera rempli Sprint 7)
│
├── src/
│   ├── channels.py                  ← squelette vide
│   ├── calibration.py               ← squelette vide
│   ├── experiment.py                ← squelette vide
│   ├── analysis.py                  ← squelette vide
│   ├── experiment_corollaries.py    ← squelette vide
│   └── experiment_hybrid.py         ← squelette vide
│
├── results/
│   ├── raw_results.csv              ← en-têtes seuls
│   ├── conflict_results.csv         ← en-têtes seuls
│   ├── learning_curves.csv          ← en-têtes seuls
│   ├── rlhf_propagation.csv         ← en-têtes seuls
│   ├── hybrid_comparison.csv        ← en-têtes seuls
│   └── source_correlation.csv       ← en-têtes seuls
│
├── figures/                         ← répertoire vide
│
├── tests/                           ← répertoire vide (tests unitaires Sprint 1+)
│
├── paper/
│   └── EIP_paper_v0.1.md            ← squelette vide (sera rempli Sprint 0.5)
│
├── brainstorm/
│   ├── BR-001.md  … BR-010.md       ← voir contenu ci-dessous
│   └── [council-reports à venir]
│
└── reviews/                         ← répertoire vide
```

---

## Contenu des fichiers à créer

### STATUS.md

```markdown
# STATUS — epistemic-impossibility-validation

**Sprint courant :** 0
**Statut :** PRÊT
**Version chantier :** v4 (5 questions, 7 sprints)
**Dernière mise à jour :** [DATE]

## Sprint courant
Sprint 0 — Préparation infrastructure — EN COURS

## Sprints complétés
(aucun)

## Prochaine action
Valider critère de passage Sprint 0 :
  git clone + pip install -r requirements.txt fonctionne sans erreur
  sur machine tierce, et les 10 fichiers BR existent avec statut PROPOSÉ.
```

### VARIABLES.md

```markdown
# VARIABLES — epistemic-impossibility-validation
# 8 blocs — remplir avant Sprint 0.5

## BLOC 1 — Identité du projet
NOM_CHANTIER     : epistemic-impossibility-validation
TARGET_CONF      : ICLR 2027
DEADLINE_SOUM    : Octobre 2026
VERSION_CHANTIER : v4

## BLOC 2 — Équipe
PI               : Andrei
CO_AUTEURS       : [à compléter]
CONTACT_PI       : [email]

## BLOC 3 — Architecture technique
MODELE_BASE      : GPT-2 small (117M paramètres, HuggingFace)
N_CANAUX         : 3 (A=texte, B=latent, C=CLAIM)
N_AGENTS         : 3 (émetteur, récepteur, orchestrateur)
N_RUNS           : 50 par condition (extensible à 100 si variance élevée)
SEED_GLOBAL      : 42
NIVEAUX_ENTROPIE : {0.05, 0.1, 0.2, 0.5, 1.0, 2.0}
NIVEAUX_CONFLIT  : {0.0, 0.2, 0.5, 0.8}
N_ROUNDS_COROL   : 200
N_ROUNDS_RLHF    : 100
NIVEAUX_CONFIANCE: {0.3, 0.6, 0.9}
ARCHITECTURES    : {texte_seul, latent_seul, CLAIM_seul, hybride}
N_CLASSES_TACHE  : 4

## BLOC 4 — Budget tokens
SESSIONS_OPUS    : ~8
SESSIONS_SONNET  : ~8
SESSIONS_JULES   : ~6
SESSIONS_HAIKU   : ~5

## BLOC 5 — Repo GitHub
GITHUB_USER      : [à compléter]
GITHUB_REPO      : epistemic-impossibility-validation
BRANCH_PRINCIPALE: main

## BLOC 6 — Modèles IA
MODEL_THEORIQUE  : claude-opus-4-7 (extended thinking)
MODEL_ANALYSTE   : claude-opus-4-7 (instance isolée, extended thinking)
MODEL_COUNCIL    : claude-sonnet-4-6 (5 sub-agents)
MODEL_REDACTION  : claude-sonnet-4-x
MODEL_CODE       : Jules (Google) ou claude-sonnet-4-x
MODEL_VERIFICATION: claude-haiku-3-x

## BLOC 7 — Domaine de recherche
PROBLEME_EIP     : Impossibilité d'un canal simultanément
                   gradient-preserving et auditable
LEMME_CIBLE      : Auditabilité → Discrétion (dénombrabilité de O_cert)
STRATEGIE_PREUVE : À décider (BR-010) — ne pas anticiper ici
HYPOTHESE_NULL_1 : Les trois canaux ont le même profil de gradient
HYPOTHESE_ALT_1  : Canal texte s'effondre quand entropie → 0
CONCURRENTS      : RecursiveMAS (Yang et al. 2026), DIAL (Lazaridou 2020)

## BLOC 8 — Structure papier
# À compléter en Sprint 0.5 après formalisation des définitions
SECTION_1 : Introduction
SECTION_2 : Background
SECTION_3 : Théorème — [structure à préciser en Sprint 0.5]
SECTION_4 : Epistemic Interface Problem
SECTION_5 : CLAIM comme solution
SECTION_6 : Validation expérimentale
SECTION_7 : Limitations
SECTION_8 : Discussion et travaux futurs
```

### CLAUDE.md

```markdown
# CLAUDE.md — Instructions pour Claude Code Web

## Identité du projet
Chantier de validation expérimentale d'un théorème mathématique.
Repo : epistemic-impossibility-validation
Branche principale : main

## Convention de nommage

Le théorème central du projet s'appelle :
  **TIE — Théorème de l'Impossibilité Épistémique**
  (alias provisoire dans le repo : "Théorème 7.1" / fichier : tie_formal.md)

Règle : dans tous les fichiers produits par les instances de travail,
utiliser "TIE" comme désignation courte et "Théorème de l'Impossibilité
Épistémique" comme désignation longue.
Le fichier tie_formal.md sera renommé tie_formal.md en Sprint 4
(git mv + mise à jour des renvois). Pas avant.

## Règles opérationnelles

R-DOC-01   : Maximum 4 fichiers documentation core dans le repo.
R-DEC-01   : Toute décision d'architecture est tracée dans brainstorm/BR-XXX.md.
R-QO-01    : Toute question non résolue est tracée avec identifiant QO-Sn-XX.
R-PREUVE-01: Aucune preuve n'est complète sans validation Analyste externe.
R-REPRO-01 : Toute expérience est reproductible : seed fixé, dépendances versionnées.
R-REPRO-02 : Le canal C (CLAIM) doit être bit-à-bit identique entre deux runs,
             même seed.
R-STAT-01  : Toute comparaison inclut un test statistique et des barres d'erreur
             (IQR sur 50 runs).
R-STAT-02  : N = 50 runs minimum. Si IQR > 30% de la médiane → N = 100.

## Source de vérité
Le repo GitHub est la source de vérité. La conversation est éphémère.
Toute session commence par : git pull
Toute session se termine par : commit de STATUS.md à jour.

## Format des commits
[SPRINT-N] action courte : fichier(s) modifié(s)
Exemple : [SPRINT-1] add channel A implementation : src/channels.py
```

### requirements.txt

```
# epistemic-impossibility-validation
# Python 3.11+
torch>=2.0.0
transformers>=4.35.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.11.0
pandas>=2.0.0
numpy>=1.24.0
pytest>=7.0.0
```

### BR-001.md à BR-010.md — Format commun

Chaque fichier BR suit ce template :

```markdown
# BR-XXX — [Titre de la décision]
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint N

## Question
[La décision à prendre]

## Options
A. [Option A]
B. [Option B]

## Critères de décision
[Ce qui permettra de trancher]

## Statut
PROPOSÉ — à résoudre en Sprint N
```

Contenu spécifique de chaque BR :

**BR-001** — Stratégie anti-biais de substrat (personas vs IA externes)
- Résolution : Sprint 0
- Question : quand invoquer des IA externes (DeepSeek, Gemini, Mistral) vs personas internes ?

**BR-002** — Calibration γ_i : k-NN vs Deep EK-NN
- Résolution : Sprint 1 (LLM Council requis — lancer en Sprint 0)
- Question : quelle méthode de calibration pour la fonction γ_i ?

**BR-003** — Modèle de base : GPT-2 small (117M)
- Résolution : Sprint 0 (décision adoptée sauf objection)
- Question : GPT-2 small est-il suffisamment représentatif ?

**BR-004** — Règle de combinaison TBM : O1 (Smets) vs O3 (Denœux)
- Résolution : Sprint 0 (LLM Council requis — lancer en Sprint 0)
- Question : quelle règle de combinaison pour les fonctions de masse ?

**BR-005** — Valeur initiale θ_conflit : 0.3
- Résolution : Sprint 0 (prior avant calibration empirique Sprint 3)
- Question : valeur initiale du seuil de conflit avant calibration.

**BR-006** — Disponibilité Jules pour tous les sprints code (1, 2, 3, 5, 6)
- Résolution : Sprint 0
- Question : Jules disponible ? Si non, fallback GitHub Actions ou local.

**BR-007** — Tâche collaborative synthétique Sprints 5–6 : classification 4 classes
- Résolution : Sprint 5
- Question : la tâche de classification 4 classes (Θ = {ami, ennemi, neutre, inconnu})
  est-elle représentative ?

**BR-008** — Framing recherche v4 : 5 questions dans le bon ordre pour ICLR 2027
- Résolution : Sprint 0.5 (LLM Council requis)
- Question : les 5 questions de recherche sont-elles dans le bon ordre ?

**BR-009** — Critère de stricte supériorité hybride (gap minimum Figure 4)
- Résolution : Sprint 6
- Question : quel gap minimum acceptable pour déclarer la supériorité stricte ?

**BR-010** — Stratégie de preuve du Lemme d'auditabilité-discrétion
- Résolution : après Sprint 7, Tâche 7.2 (Analyste tranche)
- Question : Stratégie A (calculabilité) ou B (Cantor) comme preuve principale ?

---

### CSV — en-têtes seuls

**raw_results.csv**
```
run_id,seed,canal,entropie,gradient_norm,n_tokens,timestamp
```

**conflict_results.csv**
```
run_id,seed,canal,niveau_conflit,theta_conflit,masse_vide,resolution,timestamp
```

**learning_curves.csv**
```
run_id,seed,canal,round,accuracy,loss,timestamp
```

**rlhf_propagation.csv**
```
run_id,seed,agent_id,confiance_kappa,signal_rlhf,gradient_norm,round,timestamp
```

**hybrid_comparison.csv**
```
run_id,seed,architecture,accuracy,auditabilite_score,gradient_norm,timestamp
```

**source_correlation.csv**
```
run_id,seed,source_A_chain_id,source_B_chain_id,correlation_detectee,
masse_combinee,rule_appliquee,timestamp
```

---

## Checklist de passage Sprint 0

Valider chaque item avant de committer et de passer à Sprint 0.5.

```
  — Fondations repo —
□ VARIABLES.md complété et commité (8 blocs)
□ Repo GitHub créé avec branch main
□ CLAUDE.md au format Claude Code Web commité
□ STATUS.md initialisé (Sprint=0, statut=PRÊT, VERSION=v4) et commité
□ Arborescence créée via init_project.sh
□ README.md squelette commité
□ requirements.txt commité

  — Vérifications techniques —
□ git clone + pip install -r requirements.txt fonctionne sans erreur
□ from transformers import GPT2Model → sans erreur
□ torch.manual_seed(42) → sans erreur
□ Connectivity Claude Code Web / Jules ↔ GitHub (lecture + commit)

  — Décisions architecturales —
□ BR-001 à BR-010 créés avec statut PROPOSÉ et commités
□ LLM Council lancé sur BR-002 (γ_i) → council-report-BR002.html commité
□ LLM Council lancé sur BR-004 (règle O1 vs O3) → council-report-BR004.html commité
□ Quota tokens Opus 4.7 connu (~8 sessions)
□ Décision Jules disponibilité tous sprints code (1,2,3,5,6) documentée dans BR-006
□ R-PI-01 : régime de propriété intellectuelle documenté si applicable
```

---

## Critère de passage Sprint 0

> **`git clone` + `pip install -r requirements.txt` fonctionne sans erreur
> sur une machine tierce. Les 10 fichiers BR existent avec statut PROPOSÉ.**

Quand ce critère est atteint :
1. Mettre STATUS.md à jour : Sprint courant = 0.5, statut = PRÊT
2. Committer
3. Passer au fichier `SPRINT-0.5-context.md`

---

*Fichier de session — ne pas modifier après la session*
*Sprint 0 — v4 — Mai 2026*
