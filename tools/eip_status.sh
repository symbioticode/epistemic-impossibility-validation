#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# eip_status.sh — Tableau de bord progression projet EIP
# ═══════════════════════════════════════════════════════════════════════════
#
# USAGE:
#   ./eip_status.sh              # tableau de bord complet
#   ./eip_status.sh --sprint     # résumé sprint courant seulement
#   ./eip_status.sh --backups    # liste des sauvegardes locales
#   ./eip_status.sh --sync       # état synchronisation GitHub
#   ./eip_status.sh --report     # génère un rapport Markdown
#
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

BACKUP_BASE="${HOME}/.eip_backups"

# ── Couleurs ─────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
CYAN='\033[0;36m'; BOLD='\033[1m'; BLUE='\033[0;34m'
MAGENTA='\033[0;35m'; NC='\033[0m'

ok()    { echo -e "  ${GREEN}✅${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠️ ${NC} $1"; }
fail()  { echo -e "  ${RED}❌${NC} $1"; }
info()  { echo -e "  ${CYAN}ℹ️ ${NC} $1"; }
box()   { echo -e "${BOLD}${BLUE}$1${NC}"; echo "$(printf '═%.0s' {1..60})"; }
sec()   { echo ""; echo -e "${BOLD}${CYAN}▶ $1${NC}"; echo "$(printf '─%.0s' {1..50})"; }

MODE="${1:-dashboard}"
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
GIT_USER=$(git config user.email 2>/dev/null || echo "unknown")

# ═══════════════════════════════════════════════════════════════════════════
# FONCTIONS D'ANALYSE
# ═══════════════════════════════════════════════════════════════════════════

# Détecter le sprint courant depuis STATUS.md ou la branche
detect_sprint() {
  local sprint="unknown"
  if [[ -f "STATUS.md" ]]; then
    sprint=$(grep -oE "Sprint courant.*[0-9]+\.[0-9]+" STATUS.md 2>/dev/null \
      | grep -oE "[0-9]+\.[0-9]+" | head -1 || echo "")
  fi
  if [[ -z "$sprint" ]] && [[ "$CURRENT_BRANCH" =~ sprint/([^/]+) ]]; then
    sprint="${BASH_REMATCH[1]}"
  fi
  echo "${sprint:-0}"
}

# Compter les fichiers par dossier
count_files() {
  local dir="$1" ext="${2:-*}"
  find "$dir" -name "$ext" -type f 2>/dev/null | wc -l | tr -d ' '
}

# Taille humaine d'un dossier
dir_size() {
  du -sh "$1" 2>/dev/null | awk '{print $1}' || echo "?"
}

# Vérifier si un fichier est non-vide
nonempty() {
  [[ -f "$1" ]] && [[ -s "$1" ]] && echo "✅" || echo "❌"
}

# Taux de complétion d'un fichier (lignes non-vides / TODO restants)
file_progress() {
  local file="$1"
  [[ -f "$file" ]] || { echo "0%"; return; }
  local total todos
  total=$(grep -c "." "$file" 2>/dev/null || echo 0)
  todos=$(grep -c "\[ \]" "$file" 2>/dev/null || echo 0)
  if (( total == 0 )); then echo "vide"; return; fi
  local done_count=$(( total > todos ? total - todos : 0 ))
  echo "${done_count}/${total} lignes"
}

# ═══════════════════════════════════════════════════════════════════════════
# TABLEAU DE BORD PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════
dashboard() {
  clear
  echo ""
  box "  EIP — Tableau de Bord Projet  $(date '+%Y-%m-%d %H:%M')"
  echo ""

  local sprint
  sprint=$(detect_sprint)

  echo -e "  ${BOLD}Sprint courant :${NC} $sprint    ${BOLD}Branche :${NC} $CURRENT_BRANCH"
  echo -e "  ${BOLD}Utilisateur    :${NC} $GIT_USER"
  echo ""

  # ── STRUCTURE DU REPO ──────────────────────────────────────────────────
  sec "📁 Structure du dépôt"

  # Fichiers core
  local core_ok=0 core_total=9
  for f in STATUS.md VARIABLES.md CLAUDE.md requirements.txt init_project.sh \
            README.md CHANGELOG.md QUICK_START.md REPO_STRUCTURE.md; do
    [[ -f "$f" ]] && core_ok=$(( core_ok + 1 ))
  done
  local core_pct=$(( core_ok * 100 / core_total ))
  progress_bar "Fichiers core ($core_ok/$core_total)" $core_ok $core_total

  # Dossiers
  local dirs_ok=0 dirs_total=8
  for d in theory src results figures tests paper brainstorm reviews; do
    [[ -d "$d" ]] && dirs_ok=$(( dirs_ok + 1 ))
  done
  progress_bar "Dossiers requis ($dirs_ok/$dirs_total)" $dirs_ok $dirs_total

  # ── THEORY ──────────────────────────────────────────────────────────────
  sec "📐 Theory (formalisation)"
  local theory_files=("tie_formal.md" "belnap_tbm_isomorphism.md" "corollary_framework.md" "lemme_auditabilite.md")
  local theory_ok=0
  for f in "${theory_files[@]}"; do
    if [[ -s "theory/$f" ]]; then
      local lines
      lines=$(wc -l < "theory/$f" 2>/dev/null || echo 0)
      ok "$f ($lines lignes)"
      theory_ok=$(( theory_ok + 1 ))
    else
      fail "$f (vide ou absent)"
    fi
  done
  progress_bar "Theory ($theory_ok/${#theory_files[@]})" $theory_ok ${#theory_files[@]}

  # ── SOURCE CODE ─────────────────────────────────────────────────────────
  sec "🐍 Code source (src/)"
  local src_files=("channels.py" "calibration.py" "experiment.py" "analysis.py" \
                   "experiment_corollaries.py" "experiment_hybrid.py")
  local src_ok=0
  for f in "${src_files[@]}"; do
    if [[ -s "src/$f" ]]; then
      local lines
      lines=$(wc -l < "src/$f" 2>/dev/null || echo 0)
      ok "$f ($lines lignes)"
      src_ok=$(( src_ok + 1 ))
    else
      warn "$f (squelette vide)"
    fi
  done
  progress_bar "Code src ($src_ok/${#src_files[@]})" $src_ok ${#src_files[@]}

  # ── RÉSULTATS ────────────────────────────────────────────────────────────
  sec "📊 Résultats (results/)"
  local csv_files=("raw_results.csv" "conflict_results.csv" "learning_curves.csv" \
                   "rlhf_propagation.csv" "hybrid_comparison.csv" "source_correlation.csv")
  local csv_ok=0
  for f in "${csv_files[@]}"; do
    if [[ -f "results/$f" ]]; then
      local lines
      lines=$(wc -l < "results/$f" 2>/dev/null || echo 0)
      if (( lines > 1 )); then
        ok "$f ($lines lignes de données)"
        csv_ok=$(( csv_ok + 1 ))
      else
        warn "$f (en-tête seulement)"
      fi
    else
      fail "$f absent"
    fi
  done
  progress_bar "Résultats CSV ($csv_ok/${#csv_files[@]})" $csv_ok ${#csv_files[@]}

  # ── BRAINSTORM ───────────────────────────────────────────────────────────
  sec "💡 Brainstorm (BR-001 à BR-010)"
  local br_ok=0
  for i in $(seq -w 1 10); do
    local f="brainstorm/BR-0${i}.md"
    [[ -s "$f" ]] && br_ok=$(( br_ok + 1 ))
  done
  progress_bar "Brainstorm ($br_ok/10)" $br_ok 10

  # Fichiers additionnels brainstorm
  local extra_br
  extra_br=$(find brainstorm/ -name "*.md" -not -name "BR-0*.md" 2>/dev/null | wc -l | tr -d ' ')
  local extra_html
  extra_html=$(find brainstorm/ -name "*.html" 2>/dev/null | wc -l | tr -d ' ')
  (( extra_br > 0 )) && info "$extra_br fichier(s) Markdown additionnels"
  (( extra_html > 0 )) && info "$extra_html rapport(s) HTML (LLM Council, etc.)"

  # ── PAPER ────────────────────────────────────────────────────────────────
  sec "📄 Paper"
  local paper_count
  paper_count=$(find paper/ -name "*.md" -o -name "*.tex" -o -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
  if (( paper_count > 0 )); then
    ok "$paper_count fichier(s) présent(s)"
    find paper/ \( -name "*.md" -o -name "*.tex" \) 2>/dev/null | while read -r f; do
      local lines
      lines=$(wc -l < "$f" 2>/dev/null || echo 0)
      info "$(basename $f) — $lines lignes"
    done
  else
    warn "Aucun fichier paper/ (normal en Sprint 0)"
  fi

  # ── TAILLE ET SANTÉ GIT ──────────────────────────────────────────────────
  sec "🔍 Santé Git"
  local pack_size
  pack_size=$(git count-objects -vH 2>/dev/null | grep size-pack | awk '{print $2}')
  echo -n "  Pack Git : $pack_size  "

  # Extraire la valeur numérique pour comparaison
  local pack_num
  pack_num=$(echo "$pack_size" | sed 's/[^0-9.]//g')
  local pack_unit
  pack_unit=$(echo "$pack_size" | sed 's/[0-9. ]//g')
  local pack_mb=0
  [[ "$pack_unit" == "MiB" || "$pack_unit" == "MB" ]] && pack_mb=$(printf "%.0f" "$pack_num" 2>/dev/null || echo 0)
  [[ "$pack_unit" == "GiB" || "$pack_unit" == "GB" ]] && pack_mb=$(( $(printf "%.0f" "$pack_num" 2>/dev/null || echo 1) * 1024 ))

  if (( pack_mb > 95 )); then
    echo -e "${RED}❌ TROP VOLUMINEUX — ./eip_deploy.sh --clean-history${NC}"
  elif (( pack_mb > 50 )); then
    echo -e "${YELLOW}⚠️  Attention (> 50MB)${NC}"
  else
    echo -e "${GREEN}✅${NC}"
  fi

  # Commits non poussés
  local unpushed
  unpushed=$(git log main --not origin/main --oneline 2>/dev/null | wc -l | tr -d ' ')
  if (( unpushed > 0 )); then
    warn "$unpushed commit(s) non poussé(s) sur GitHub"
    git log main --not origin/main --oneline 2>/dev/null | head -3 | sed 's/^/    /'
  else
    ok "Synchronisé avec GitHub"
  fi

  # Fichiers non trackés potentiellement problématiques
  local big_untracked
  big_untracked=$(git ls-files --others --exclude-standard 2>/dev/null \
    | while read -r f; do
        [[ -f "$f" ]] || continue
        local s
        s=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
        (( s > 10485760 )) && echo "$f ($(( s / 1048576 ))MB)"
      done)
  if [[ -n "$big_untracked" ]]; then
    warn "Fichiers non trackés > 10MB (vérifier .gitignore) :"
    echo "$big_untracked" | sed 's/^/    /'
  fi

  # ── BACKUPS LOCAUX ───────────────────────────────────────────────────────
  sec "💾 Sauvegardes locales"
  if [[ -d "$BACKUP_BASE" ]]; then
    local backup_count
    backup_count=$(ls -1 "$BACKUP_BASE" 2>/dev/null | wc -l | tr -d ' ')
    if (( backup_count > 0 )); then
      ok "$backup_count backup(s) dans $BACKUP_BASE"
      ls -1t "$BACKUP_BASE" 2>/dev/null | head -3 | while read -r d; do
        local meta="${BACKUP_BASE}/${d}/.backup_meta"
        if [[ -f "$meta" ]]; then
          local ts br
          ts=$(grep "^timestamp:" "$meta" | cut -d' ' -f2)
          br=$(grep "^branch:" "$meta" | cut -d' ' -f2)
          echo "    $d  [$br]"
        else
          echo "    $d"
        fi
      done
    else
      warn "Aucun backup local"
    fi
  else
    warn "Répertoire de backup inexistant ($BACKUP_BASE)"
    info "Sera créé automatiquement au prochain ./eip_deploy.sh"
  fi

  # ── RÉSUMÉ GLOBAL ────────────────────────────────────────────────────────
  echo ""
  box "  📈 Progression globale"
  echo ""

  local total_checks=0 passed_checks=0

  # Calculer un score global
  (( core_ok == core_total )) && passed_checks=$(( passed_checks + 1 )); total_checks=$(( total_checks + 1 ))
  (( dirs_ok == dirs_total )) && passed_checks=$(( passed_checks + 1 )); total_checks=$(( total_checks + 1 ))
  (( theory_ok > 0 )) && passed_checks=$(( passed_checks + 1 )); total_checks=$(( total_checks + 1 ))
  (( src_ok > 0 )) && passed_checks=$(( passed_checks + 1 )); total_checks=$(( total_checks + 1 ))
  (( br_ok == 10 )) && passed_checks=$(( passed_checks + 1 )); total_checks=$(( total_checks + 1 ))
  (( pack_mb < 95 )) && passed_checks=$(( passed_checks + 1 )); total_checks=$(( total_checks + 1 ))
  (( unpushed == 0 )) && passed_checks=$(( passed_checks + 1 )); total_checks=$(( total_checks + 1 ))

  local global_pct=$(( passed_checks * 100 / total_checks ))
  progress_bar "Score global ($passed_checks/$total_checks)" $passed_checks $total_checks

  echo ""
  if (( global_pct == 100 )); then
    echo -e "  ${GREEN}${BOLD}🎉 Sprint $sprint — COMPLET ET STABLE${NC}"
  elif (( global_pct >= 70 )); then
    echo -e "  ${YELLOW}${BOLD}⚡ Sprint $sprint — En bonne voie (${global_pct}%)${NC}"
  else
    echo -e "  ${RED}${BOLD}🔧 Sprint $sprint — Travail en cours (${global_pct}%)${NC}"
  fi
  echo ""
}

# ── Barre de progression ASCII ────────────────────────────────────────────
progress_bar() {
  local label="$1" val="$2" total="$3"
  local pct width=30 filled empty

  (( total == 0 )) && pct=0 || pct=$(( val * 100 / total ))
  filled=$(( val * width / (total > 0 ? total : 1) ))
  empty=$(( width - filled ))

  local bar=""
  local i
  for (( i=0; i<filled; i++ )); do bar+="█"; done
  for (( i=0; i<empty; i++ )); do bar+="░"; done

  local color
  (( pct == 100 )) && color="$GREEN" || { (( pct >= 50 )) && color="$YELLOW" || color="$RED"; }

  printf "  %-35s ${color}[%s]${NC} %3d%%\n" "$label" "$bar" "$pct"
}

# ── Vue synchronisation ───────────────────────────────────────────────────
view_sync() {
  box "  📡 Synchronisation GitHub"
  echo ""
  echo -e "  ${BOLD}Branche locale  :${NC} $CURRENT_BRANCH"

  local remote_url
  remote_url=$(git remote get-url origin 2>/dev/null || echo "❌ Pas de remote configuré")
  echo -e "  ${BOLD}Remote origin   :${NC} $remote_url"
  echo ""

  info "Derniers commits distants :"
  git log origin/main --oneline -5 2>/dev/null | sed 's/^/    /' || echo "    (non accessible)"

  echo ""
  info "Commits locaux non poussés :"
  git log main --not origin/main --oneline 2>/dev/null | sed 's/^/    /' || echo "    Aucun"

  echo ""
  info "Taille du pack Git : $(git count-objects -vH | grep size-pack | awk '{print $2}')"
}

# ── Liste des backups ─────────────────────────────────────────────────────
view_backups() {
  box "  💾 Sauvegardes locales"
  echo ""

  if [[ ! -d "$BACKUP_BASE" ]]; then
    echo "  Aucun backup trouvé dans $BACKUP_BASE"
    return
  fi

  local backups=()
  while IFS= read -r -d '' d; do
    backups+=("$d")
  done < <(find "$BACKUP_BASE" -maxdepth 1 -mindepth 1 -type d -print0 | sort -rz)

  if (( ${#backups[@]} == 0 )); then
    echo "  Aucun backup trouvé"
    return
  fi

  printf "  %-45s %-20s %s\n" "NOM" "BRANCHE" "TAILLE"
  printf "  %-45s %-20s %s\n" "$(printf '─%.0s' {1..45})" "$(printf '─%.0s' {1..20})" "$(printf '─%.0s' {1..8})"

  for d in "${backups[@]}"; do
    local name branch size meta
    name=$(basename "$d")
    meta="${d}/.backup_meta"
    branch=$(grep "^branch:" "$meta" 2>/dev/null | cut -d' ' -f2 || echo "?")
    size=$(du -sh "$d" 2>/dev/null | awk '{print $1}' || echo "?")
    printf "  %-45s %-20s %s\n" "$name" "$branch" "$size"
  done

  echo ""
  info "Total : ${#backups[@]} backup(s) dans $BACKUP_BASE"
  echo ""
  echo "  Restaurer un backup :"
  echo "    cp -r ${BACKUP_BASE}/<nom_backup>/ /chemin/de/restauration/"
}

# ── Génération rapport Markdown ───────────────────────────────────────────
generate_report() {
  local report_file="STATUS_REPORT_$(date '+%Y%m%d_%H%M%S').md"
  local sprint
  sprint=$(detect_sprint)

  cat > "$report_file" << EOF
# Rapport de Progression EIP — $(date '+%Y-%m-%d %H:%M')

**Sprint courant :** $sprint
**Branche :** $CURRENT_BRANCH
**Utilisateur :** $GIT_USER
**Pack Git :** $(git count-objects -vH | grep size-pack | awk '{print $2}')

## Structure

| Composant | Statut |
|-----------|--------|
| Fichiers core (9) | $(for f in STATUS.md VARIABLES.md CLAUDE.md requirements.txt init_project.sh README.md CHANGELOG.md QUICK_START.md REPO_STRUCTURE.md; do [[ -f "$f" ]] || echo "❌ $f"; done | grep -c "❌" | xargs -I{} echo "{} manquant(s)" || echo "✅ complets") |
| Dossiers (8) | $(for d in theory src results figures tests paper brainstorm reviews; do [[ -d "$d" ]] || echo "❌"; done | grep -c "❌" | xargs -I{} echo "{} manquant(s)" || echo "✅ complets") |
| Theory/*.md | $(for f in tie_formal.md belnap_tbm_isomorphism.md corollary_framework.md lemme_auditabilite.md; do [[ -s "theory/$f" ]] && echo "✅" || echo "❌ $f"; done | grep -c "✅")/4 non vides |
| src/*.py | $(for f in channels.py calibration.py experiment.py analysis.py experiment_corollaries.py experiment_hybrid.py; do [[ -s "src/$f" ]] && echo "✅" || echo "❌"; done | grep -c "✅")/6 non vides |
| results/*.csv | $(for f in raw_results.csv conflict_results.csv learning_curves.csv rlhf_propagation.csv hybrid_comparison.csv source_correlation.csv; do [[ -f "results/$f" ]] && echo "✅" || echo "❌"; done | grep -c "✅")/6 présents |
| brainstorm/BR-00*.md | $(for i in $(seq -w 1 10); do [[ -s "brainstorm/BR-0${i}.md" ]] && echo "✅" || echo "❌"; done | grep -c "✅")/10 non vides |

## Git

\`\`\`
$(git log --oneline -5 2>/dev/null || echo "N/A")
\`\`\`

## Commits non poussés

\`\`\`
$(git log main --not origin/main --oneline 2>/dev/null || echo "Aucun")
\`\`\`

---
*Généré par eip_status.sh --report*
EOF

  ok "Rapport généré : $report_file"
}

# ═══════════════════════════════════════════════════════════════════════════
# DISPATCH
# ═══════════════════════════════════════════════════════════════════════════
case "$MODE" in
  --sprint)  dashboard ;;   # alias simplifié
  --sync)    view_sync ;;
  --backups) view_backups ;;
  --report)  generate_report ;;
  *)         dashboard ;;
esac
