#!/usr/bin/env bash
# verify_sprint0.sh — Validation complétion Sprint 0
set -euo pipefail

echo "🔍 Vérification Sprint 0 — Infrastructure"
echo "=========================================="

PASS=0
FAIL=0

# 1. Structure de base
echo -n "□ Arborescence core (9 fichiers) ... "
CORE_FILES=("STATUS.md" "VARIABLES.md" "CLAUDE.md" "requirements.txt" "init_project.sh" "README.md" "CHANGELOG.md" "QUICK_START.md" "REPO_STRUCTURE.md")
for f in "${CORE_FILES[@]}"; do
    [[ -f "$f" ]] || { echo "❌ $f manquant"; FAIL=$((FAIL+1)); continue; }
done
echo "✅" && PASS=$((PASS+1))

# 2. Dossiers theory/src/results/paper/brainstorm/reviews
echo -n "□ Dossiers requis (6) ... "
for d in theory src results figures tests paper brainstorm reviews; do
    [[ -d "$d" ]] || { echo "❌ $d manquant"; FAIL=$((FAIL+1)); continue; }
done
echo "✅" && PASS=$((PASS+1))

# 3. Fichiers theory/ (4 squelettes)
echo -n "□ theory/*.md (4 fichiers) ... "
THEORY_FILES=("theorem71_formal.md" "belnap_tbm_isomorphism.md" "corollary_framework.md" "lemme_auditabilite.md")
for f in "${THEORY_FILES[@]}"; do
    [[ -f "theory/$f" ]] || { echo "❌ theory/$f manquant"; FAIL=$((FAIL+1)); continue; }
done
echo "✅" && PASS=$((PASS+1))

# 4. src/*.py (6 squelettes)
echo -n "□ src/*.py (6 fichiers) ... "
SRC_FILES=("channels.py" "calibration.py" "experiment.py" "analysis.py" "experiment_corollaries.py" "experiment_hybrid.py")
for f in "${SRC_FILES[@]}"; do
    [[ -f "src/$f" ]] || { echo "❌ src/$f manquant"; FAIL=$((FAIL+1)); continue; }
done
echo "✅" && PASS=$((PASS+1))

# 5. results/*.csv (6 fichiers avec en-têtes)
echo -n "□ results/*.csv (6 fichiers avec en-têtes) ... "
CSV_FILES=("raw_results.csv" "conflict_results.csv" "learning_curves.csv" "rlhf_propagation.csv" "hybrid_comparison.csv" "source_correlation.csv")
for f in "${CSV_FILES[@]}"; do
    [[ -f "results/$f" ]] || { echo "❌ results/$f manquant"; FAIL=$((FAIL+1)); continue; }
    [[ $(head -1 "results/$f" | wc -c) -gt 10 ]] || { echo "❌ results/$f vide ou sans en-tête"; FAIL=$((FAIL+1)); continue; }
done
echo "✅" && PASS=$((PASS+1))

# 6. brainstorm/BR-001.md à BR-010.md (10 fichiers, statut PROPOSÉ)
echo -n "□ brainstorm/BR-001.md à BR-010.md (10 fichiers PROPOSÉ) ... "
for i in $(seq -w 1 10); do
    f="brainstorm/BR-0${i}.md"
    [[ -f "$f" ]] || { echo "❌ $f manquant"; FAIL=$((FAIL+1)); continue; }
    grep -q "Statut.*PROPOSÉ" "$f" || { echo "❌ $f sans statut PROPOSÉ"; FAIL=$((FAIL+1)); continue; }
done
echo "✅" && PASS=$((PASS+1))

# 7. VARIABLES.md — 8 blocs présents
echo -n "□ VARIABLES.md — 8 blocs ... "
BLOCKS=("BLOC 1" "BLOC 2" "BLOC 3" "BLOC 4" "BLOC 5" "BLOC 6" "BLOC 7" "BLOC 8")
for b in "${BLOCKS[@]}"; do
    grep -q "$b" VARIABLES.md || { echo "❌ $b manquant dans VARIABLES.md"; FAIL=$((FAIL+1)); continue; }
done
echo "✅" && PASS=$((PASS+1))

# 8. STATUS.md — Sprint 0 complété
echo -n "□ STATUS.md — Sprint 0 marqué complété ... "
if grep -q "Sprint courant.*0.5\|Sprint 0.*[Cc]omplété\|Sprint 0.*[Tt]erminé" STATUS.md; then
    echo "✅" && PASS=$((PASS+1))
else
    echo "⚠️  STATUS.md ne mentionne pas la progression vers Sprint 0.5"
    FAIL=$((FAIL+1))
fi

# 9. .gitignore — patterns critiques présents
echo -n "□ .gitignore — patterns critiques ... "
PATTERNS=(".venv/" "__pycache__/" "*.pt" "*.bin")
for p in "${PATTERNS[@]}"; do
    grep -q "$p" .gitignore || { echo "❌ Pattern '$p' absent de .gitignore"; FAIL=$((FAIL+1)); continue; }
done
echo "✅" && PASS=$((PASS+1))

# 10. Repo size < 100 MB
echo -n "□ Taille du pack Git < 100 MB ... "
SIZE=$(git count-objects -vH | grep size-pack | awk '{print $2}' | sed 's/Mio//')
if (( $(echo "$SIZE < 100" | bc -l 2>/dev/null || echo 0) )); then
    echo "✅ (${SIZE} MB)" && PASS=$((PASS+1))
else
    echo "❌ (${SIZE} MB > 100 MB)" && FAIL=$((FAIL+1))
fi

echo ""
echo "📊 Résultat : $PASS/$((PASS+FAIL)) tests passés"
if [[ $FAIL -eq 0 ]]; then
    echo "✅ Sprint 0 — VALIDÉ"
    exit 0
else
    echo "❌ Sprint 0 — $FAIL échec(s) à corriger"
    exit 1
fi
