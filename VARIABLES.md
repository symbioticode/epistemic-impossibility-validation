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