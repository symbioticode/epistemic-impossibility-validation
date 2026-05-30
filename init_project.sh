#!/bin/bash
# init_project.sh — Script de création de l'arborescence du projet epistemic-impossibility-validation
# Ce script crée l'arborescence complète telle que décrite dans SPRINT-0-context.md

set -euo pipefail

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }
log_ok()   { echo -e "${GREEN}[OK]${NC}   $1"; }

log_info "Création de l'arborescence du projet epistemic-impossibility-validation..."

# Création des dossiers principaux
mkdir -p theory src results figures tests paper brainstorm reviews

# Création des fichiers racine
touch README.md CHANGELOG.md QUICK_START.md REPO_STRUCTURE.md STATUS.md VARIABLES.md CLAUDE.md requirements.txt

# Création des fichiers theory/
touch theory/theorem71_formal.md theory/belnap_tbm_isomorphism.md theory/corollary_framework.md theory/lemme_auditabilite.md

# Création des fichiers src/
touch src/channels.py src/calibration.py src/experiment.py src/analysis.py src/experiment_corollaries.py src/experiment_hybrid.py

# Création des fichiers results/ avec en-têtes CSV
echo "run_id,seed,canal,entropie,gradient_norm,n_tokens,timestamp" > results/raw_results.csv
echo "run_id,seed,canal,niveau_conflit,theta_conflit,masse_vide,resolution,timestamp" > results/conflict_results.csv
echo "run_id,seed,canal,round,accuracy,loss,timestamp" > results/learning_curves.csv
echo "run_id,seed,agent_id,confiance_kappa,signal_rlhf,gradient_norm,round,timestamp" > results/rlhf_propagation.csv
echo "run_id,seed,architecture,accuracy,auditabilite_score,gradient_norm,timestamp" > results/hybrid_comparison.csv
echo "run_id,seed,source_A_chain_id,source_B_chain_id,correlation_detectee,masse_combinee,rule_appliquee,timestamp" > results/source_correlation.csv

# Création du dossier figures/ (vide)
# Création du dossier tests/ (vide)
# Création du dossier paper/
touch paper/EIP_paper_v0.1.md

# Création des fichiers brainstorm/ avec template BR
for i in {001..010}; do
    cat > brainstorm/BR-${i}.md << EOF
# BR-${i} — [Titre de la décision]
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
EOF
done

# Personnalisation spécifique de certains BR (selon SPRINT-0-context.md)
# BR-001
cat > brainstorm/BR-001.md << EOF
# BR-001 — Stratégie anti-biais de substrat (personas vs IA externes)
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 0

## Question
quand invoquer des IA externes (DeepSeek, Gemini, Mistral) vs personas internes ?

## Options
A. Invoquer des IA externes uniquement pour validation indépendante
B. Utiliser principalement des personas internes avec validation externe ponctuelle

## Critères de décision
Équilibre entre indépendance de validation et cohérence expérimentale

## Statut
PROPOSÉ — à résoudre en Sprint 0
EOF

# BR-002
cat > brainstorm/BR-002.md << EOF
# BR-002 — Calibration γ_i : k-NN vs Deep EK-NN
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 1

## Question
quelle méthode de calibration pour la fonction γ_i ?

## Options
A. k-NN classique
B. Deep EK-NN (Extended Kalman Neural Network)

## Critères de décision
Précision de calibration vs complexité computationnelle

## Statut
PROPOSÉ — à résoudre en Sprint 1 (LLM Council requis — lancer en Sprint 0)
EOF

# BR-003
cat > brainstorm/BR-003.md << EOF
# BR-003 — Modèle de base : GPT-2 small (117M)
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 0

## Question
GPT-2 small est-il suffisamment représentatif ?

## Options
A. Oui, GPT-2 small suffit pour les expériences initiales
B. Non, il faut un modèle plus grand dès le début

## Critères de décision
Représentativité vs faisabilité expérimentale

## Statut
PROPOSÉ — à résoudre en Sprint 0 (décision adoptée sauf objection)
EOF

# BR-004
cat > brainstorm/BR-004.md << EOF
# BR-004 — Règle de combinaison TBM : O1 (Smets) vs O3 (Denœux)
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 0

## Question
quelle règle de combinaison pour les fonctions de masse ?

## Options
A. O1 (règle de Smets standard)
B. O3 (règle de Denœux généralisée)

## Critères de décision
Propagation correcte de l'incertitude vs complexité de calcul

## Statut
PROPOSÉ — à résoudre en Sprint 0 (LLM Council requis — lancer en Sprint 0)
EOF

# BR-005
cat > brainstorm/BR-005.md << EOF
# BR-005 — Valeur initiale θ_conflit : 0.3
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 0

## Question
valeur initiale du seuil de conflit avant calibration.

## Options
A. θ_conflit = 0.3 (valeur modérée)
B. θ_conflit = 0.5 (seuil neutre)

## Critères de décision
Sensibilité aux conflits faibles vs robustesse au bruit

## Statut
PROPOSÉ — à résoudre en Sprint 0 (prior avant calibration empirique Sprint 3)
EOF

# BR-006
cat > brainstorm/BR-006.md << EOF
# BR-006 — Disponibilité Jules pour tous les sprints code (1, 2, 3, 5, 6)
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 0

## Question
Jules disponible ? Si non, fallback GitHub Actions ou local.

## Options
A. Jules disponible pour tous les sprints code
B. Fallback nécessaire sur GitHub Actions ou exécution locale

## Critères de décision
Fiabilité de l'environnement d'exécution continue

## Statut
PROPOSÉ — à résoudre en Sprint 0
EOF

# BR-007
cat > brainstorm/BR-007.md << EOF
# BR-007 — Tâche collaborative synthétique Sprints 5–6 : classification 4 classes
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 5

## Question
la tâche de classification 4 classes (Θ = {ami, ennemi, neutre, inconnu}) est-elle représentative ?

## Options
A. Oui, cette tâche capture les défis de l'ambiguïté sémantique
B. Non, il faut une tâche plus complexe ou différente

## Critères de décision
Pertinence pour étudier l'impossibilité épistémique vs artificialité

## Statut
PROPOSÉ — à résoudre en Sprint 5
EOF

# BR-008
cat > brainstorm/BR-008.md << EOF
# BR-008 — Framing recherche v4 : 5 questions dans le bon ordre pour ICR 2027
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 0.5

## Question
les 5 questions de recherche sont-elles dans le bon ordre ?

## Options
A. Oui, l'ordre actuel est logique pour un papier ICLR
B. Non, il faut réorganiser pour un meilleur flow narratif

## Critères de décision
Clarté de l'argumentation scientifique vs ordre chronologique des découvertes

## Statut
PROPOSÉ — à résoudre en Sprint 0.5 (LLM Council requis)
EOF

# BR-009
cat > brainstorm/BR-009.md << EOF
# BR-009 — Critère de stricte supériorité hybride (gap minimum Figure 4)
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** Sprint 6

## Question
quel gap minimum acceptable pour déclarer la supériorité stricte ?

## Options
A. Gap absolu de 5 points de pourcentage sur l'accuracy
B. Gap relatif de 15% par rapport au meilleur canal unique

## Critères de décision
Significativité statistique vs pertinence pratique

## Statut
PROPOSÉ — à résoudre en Sprint 6
EOF

# BR-010
cat > brainstorm/BR-010.md << EOF
# BR-010 — Stratégie de preuve du Lemme d'auditabilité-discrétion
**Statut :** PROPOSÉ
**Date création :** [DATE Sprint 0]
**Décideur :** [PI / LLM Council / Analyste]
**Sprint de résolution cible :** après Sprint 7, Tâche 7.2

## Question
Stratégie A (calculabilité) ou B (Cantor) comme preuve principale ?

## Options
A. Preuve par calculabilité (réduction au problème d'arrêt)
B. Preuve par construction de type Cantor (diagonale)

## Critères de décision
Rigueur mathématique vs accessibilité pour le lectorat ICLR

## Statut
PROPOSÉ — à résoudre après Sprint 7, Tâche 7.2 (Analyste tranche)
EOF

# Création du fichier deploy.sh (existant dans l'environnement)
# Comme deploy.sh existe déjà dans l'environnement, on ne le recrée pas ici
# Mais on vérifie qu'il est présent
if [ ! -f deploy.sh ]; then
    log_warn "deploy.sh manquant - il devrait être présent dans l'environnement de base"
else
    log_ok "deploy.sh trouvé"
fi

log_ok "Arborescence créée avec succès !"
log_info "Prochaine étape : vérifier la structure et commiter les changements"