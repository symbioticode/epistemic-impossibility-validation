#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# eip_deploy.sh — EIP Unified Save/Deploy/Verify Workflow
# ═══════════════════════════════════════════════════════════════════════════
#
# USAGE:
#   ./eip_deploy.sh                        # commit + backup local + push GitHub
#   ./eip_deploy.sh -m "feat: message"    # message personnalisé
#   ./eip_deploy.sh --local-only           # backup local uniquement (pas de push)
#   ./eip_deploy.sh --push-only            # push seulement (pas de backup local)
#   ./eip_deploy.sh --clean-history        # purger les gros fichiers de l'historique git
#   ./eip_deploy.sh --new-sprint <nom>     # créer une nouvelle branche de sprint
#   ./eip_deploy.sh --status               # état du repo + progression
#   ./eip_deploy.sh --pull                 # pull depuis origin
#
# RÈGLES DE BRANCHE (inchangées depuis deploy.sh) :
#   main / governance/*  → Andrei seulement (IDEES_OWNER=1 requis)
#   collab/*             → Thierry seulement
#   sprint/* feature/* research/* → tout le monde
#
# SÉCURITÉ :
#   - Vérifie la taille des fichiers AVANT tout commit (bloque > SIZE_LIMIT_MB)
#   - Vérifie le pack git AVANT push (bloque si > GIT_PACK_LIMIT_MB)
#   - Sauvegarde locale automatique dans BACKUP_DIR avant chaque push
#   - Jamais de force-push sur main (sauf IDEES_OWNER + FORCE_PUSH=1)
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

BACKUP_BASE="${HOME}/.eip_backups"          # Dossier des sauvegardes locales
SIZE_LIMIT_MB=50                             # Taille max d'un fichier individuel
GIT_PACK_LIMIT_MB=95                         # Taille max du pack Git avant push
MAX_BACKUPS=10                               # Nombre de backups locaux à conserver

# ── Couleurs ─────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
info()  { echo -e "${CYAN}[INFO]${NC}  $1"; }
err()   { echo -e "${RED}[ERR]${NC}   $1"; exit 1; }
title() { echo -e "\n${BOLD}${CYAN}$1${NC}"; echo "$(printf '─%.0s' {1..60})"; }

GIT_USER=$(git config user.email 2>/dev/null || echo "unknown")
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# ── Parse arguments ───────────────────────────────────────────────────────
CUSTOM_MSG=""
MODE="deploy"
NEW_SPRINT_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message)    CUSTOM_MSG="$2"; shift 2 ;;
    --local-only)    MODE="local_only"; shift ;;
    --push-only)     MODE="push_only"; shift ;;
    --clean-history) MODE="clean_history"; shift ;;
    --new-sprint)    MODE="new_sprint"; NEW_SPRINT_NAME="$2"; shift 2 ;;
    --status)        MODE="status"; shift ;;
    --pull)          MODE="pull"; shift ;;
    *) shift ;;
  esac
done

# ═══════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════

# ── Vérification accès branche ────────────────────────────────────────────
check_branch_access() {
  local branch="$1"
  if [[ "$branch" == "main" ]] || [[ "$branch" =~ ^governance/ ]]; then
    [[ -n "${IDEES_OWNER:-}" ]] || err "Branche '$branch' protégée.
  → Andrei : ajouter 'export IDEES_OWNER=1' dans ~/.bashrc
  → Thierry : utiliser une branche collab/NOM ou sprint/NOM"
    ok "Accès propriétaire confirmé"
  fi
  if [[ "$branch" =~ ^collab/ ]]; then
    warn "Branche collaborative — tag [EXTERNE] automatique"
  fi
}

# ── Vérification taille fichiers (AVANT staging) ──────────────────────────
check_file_sizes() {
  title "🔍 Vérification taille des fichiers"
  local big_files=()
  local limit_bytes=$((SIZE_LIMIT_MB * 1024 * 1024))

  # Fichiers modifiés/nouveaux non encore stagés
  while IFS= read -r -d '' file; do
    if [[ -f "$file" ]]; then
      local size
      size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
      if (( size > limit_bytes )); then
        local size_mb=$(( size / 1024 / 1024 ))
        big_files+=("${size_mb}MB  $file")
        warn "Fichier volumineux détecté : $file (${size_mb} MB)"
      fi
    fi
  done < <(git status --porcelain | awk '{print $2}' | tr '\n' '\0')

  if [[ ${#big_files[@]} -gt 0 ]]; then
    echo ""
    err "❌ ${#big_files[@]} fichier(s) dépassant ${SIZE_LIMIT_MB}MB détecté(s) :
$(printf '   - %s\n' "${big_files[@]}")

Solutions :
  1. Ajouter ces patterns à .gitignore
  2. Utiliser git-lfs pour les fichiers binaires volumineux
  3. FORCE_SIZE=1 ./eip_deploy.sh pour ignorer (non recommandé)"
  fi

  [[ "${FORCE_SIZE:-}" == "1" ]] && warn "FORCE_SIZE=1 — vérification taille ignorée" && return
  ok "Taille des fichiers OK (tous < ${SIZE_LIMIT_MB}MB)"
}

# ── Vérification taille pack Git (AVANT push) ─────────────────────────────
check_pack_size() {
  title "📦 Vérification taille pack Git"
  local size_raw
  size_raw=$(git count-objects -vH 2>/dev/null | grep size-pack | awk '{print $2}')
  local size_unit="${size_raw//[0-9. ]/}"
  local size_num="${size_raw//[^0-9.]/}"

  # Convertir en MB
  local size_mb=0
  if [[ "$size_unit" == "MiB" ]] || [[ "$size_unit" == "MB" ]]; then
    size_mb=$(printf "%.0f" "$size_num" 2>/dev/null || echo "$size_num")
  elif [[ "$size_unit" == "GiB" ]] || [[ "$size_unit" == "GB" ]]; then
    size_mb=$(( $(printf "%.0f" "$size_num" 2>/dev/null || echo 1) * 1024 ))
  elif [[ "$size_unit" == "KiB" ]] || [[ "$size_unit" == "KB" ]]; then
    size_mb=0
  fi

  if (( size_mb > GIT_PACK_LIMIT_MB )); then
    warn "Pack Git trop volumineux : ${size_raw} (limite : ${GIT_PACK_LIMIT_MB}MB)"
    echo ""
    echo "  → Pour nettoyer l'historique : ./eip_deploy.sh --clean-history"
    echo "  → Pour forcer (non recommandé) : FORCE_PUSH=1 ./eip_deploy.sh"
    [[ "${FORCE_PUSH:-}" == "1" ]] && warn "FORCE_PUSH=1 — vérification pack ignorée" && return
    err "Push bloqué — pack Git trop volumineux"
  fi
  ok "Pack Git OK : ${size_raw} (limite : ${GIT_PACK_LIMIT_MB}MB)"
}

# ── Sauvegarde locale ─────────────────────────────────────────────────────
local_backup() {
  title "💾 Sauvegarde locale"
  local timestamp
  timestamp=$(date '+%Y%m%d_%H%M%S')
  local sprint_label
  sprint_label=$(echo "$CURRENT_BRANCH" | tr '/' '_')
  local backup_dir="${BACKUP_BASE}/${sprint_label}_${timestamp}"

  mkdir -p "$backup_dir"

  # Copie rsync (exclut .git et .venv pour la rapidité)
  rsync -a --quiet \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.direnv/' \
    --exclude='result' \
    --exclude='result-*' \
    "$REPO_ROOT/" "$backup_dir/"

  # Métadonnées du backup
  cat > "${backup_dir}/.backup_meta" << EOF
timestamp: $timestamp
branch: $CURRENT_BRANCH
user: $GIT_USER
commit: $(git rev-parse HEAD 2>/dev/null || echo "uncommitted")
last_message: $(git log -1 --pretty=format:"%s" 2>/dev/null || echo "N/A")
EOF

  ok "Backup créé : $backup_dir"

  # Rotation : conserver seulement les MAX_BACKUPS derniers
  local backup_count
  backup_count=$(find "$BACKUP_BASE" -maxdepth 1 -type d | grep -c "${sprint_label}_" 2>/dev/null || echo 0)
  if (( backup_count > MAX_BACKUPS )); then
    local to_delete=$(( backup_count - MAX_BACKUPS ))
    find "$BACKUP_BASE" -maxdepth 1 -type d -name "${sprint_label}_*" \
      | sort | head -n "$to_delete" \
      | xargs rm -rf
    info "Rotation : $to_delete ancien(s) backup(s) supprimé(s)"
  fi
}

# ── Pre-checks qualité code ───────────────────────────────────────────────
run_prechecks() {
  title "🧪 Pre-checks qualité"
  local failed=0

  STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep '\.py$' || true)
  if [[ -n "$STAGED_PY" ]]; then
    if command -v uv &>/dev/null; then
      info "  ruff..."
      uv run ruff check $STAGED_PY --quiet 2>/dev/null && ok "  ruff: propre" || { warn "  ruff: problèmes — 'uv run ruff check --fix'"; failed=1; }
      info "  black..."
      uv run black --check $STAGED_PY --quiet 2>/dev/null && ok "  black: propre" || { warn "  black: format — 'uv run black .'"; failed=1; }
    else
      warn "  uv non trouvé — checks Python ignorés"
    fi
  fi

  # Protection fichiers gouvernance
  STAGED_GOV=$(git diff --cached --name-only 2>/dev/null | grep -E '^(CHARTER\.md|STATUS\.md|governance/)' || true)
  if [[ -n "$STAGED_GOV" ]] && [[ -z "${IDEES_OWNER:-}" ]]; then
    err "Fichiers gouvernance stagés : $STAGED_GOV
  Seul Andrei (IDEES_OWNER=1) peut commiter sur STATUS.md / CHARTER.md / governance/"
  fi

  [[ "$failed" -eq 1 ]] && [[ "${FORCE_PUSH:-}" != "1" ]] && \
    err "Pre-checks échoués. Corriger ou : FORCE_PUSH=1 ./eip_deploy.sh"

  ok "Pre-checks OK"
}

# ── Génération message de commit ──────────────────────────────────────────
generate_commit_msg() {
  if [[ -n "$CUSTOM_MSG" ]]; then
    echo "$CUSTOM_MSG"
    return
  fi

  local changed
  changed=$(git diff --cached --name-only 2>/dev/null || true)
  local scope=""

  echo "$changed" | grep -qE '^theory/'     && scope="${scope}theory,"
  echo "$changed" | grep -qE '^src/'        && scope="${scope}src,"
  echo "$changed" | grep -qE '^results/'    && scope="${scope}results,"
  echo "$changed" | grep -qE '^paper/'      && scope="${scope}paper,"
  echo "$changed" | grep -qE '^brainstorm/' && scope="${scope}brainstorm,"
  echo "$changed" | grep -qE '^reviews/'    && scope="${scope}reviews,"
  echo "$changed" | grep -qE '^governance/' && scope="${scope}governance,"
  echo "$changed" | grep -qE '^tests/'      && scope="${scope}tests,"
  scope="${scope%,}"
  [[ -z "$scope" ]] && scope="misc"

  local sprint_tag=""
  [[ "$CURRENT_BRANCH" =~ sprint/([^/]+) ]] && sprint_tag="[${BASH_REMATCH[1]}] "
  [[ "$CURRENT_BRANCH" =~ ^collab/ ]] && sprint_tag="[EXTERNE:collab] "

  local file_count
  file_count=$(echo "$changed" | grep -c . || echo 0)
  echo "${sprint_tag}${scope}: ${file_count} fichier(s) — $(date '+%Y-%m-%d %H:%M')"
}

# ═══════════════════════════════════════════════════════════════════════════
# NETTOYAGE HISTORIQUE GIT
# ═══════════════════════════════════════════════════════════════════════════
mode_clean_history() {
  title "🧹 Nettoyage historique Git"
  warn "Cette opération RÉÉCRIT l'historique. Un backup local sera créé d'abord."
  echo ""

  # Backup de sécurité AVANT tout
  local_backup

  # Identifier les gros objets dans l'historique
  info "Analyse des gros objets dans l'historique..."
  echo ""
  git rev-list --objects --all \
    | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
    | awk '/^blob/ {print $3, $4}' \
    | sort -rn \
    | head -20 \
    | awk '{printf "  %6.1f MB  %s\n", $1/1048576, $2}'

  echo ""
  warn "Patterns à purger depuis l'historique :"
  echo "  .venv/ __pycache__/ *.pt *.bin *.safetensors *.pth *.ckpt *.pkl *.h5"
  echo ""
  read -r -p "Confirmer le nettoyage ? [y/N] " confirm
  [[ "$confirm" != "y" ]] && info "Annulé." && exit 0

  # Méthode 1 : git filter-repo (recommandé)
  if command -v git-filter-repo &>/dev/null; then
    info "Utilisation de git-filter-repo..."
    git filter-repo --force \
      --path-glob '.venv' --invert-paths \
      --path-glob '__pycache__' --invert-paths \
      --path-glob '*.pt' --invert-paths \
      --path-glob '*.bin' --invert-paths \
      --path-glob '*.safetensors' --invert-paths \
      --path-glob '*.pth' --invert-paths \
      --path-glob '*.ckpt' --invert-paths \
      --path-glob '*.pkl' --invert-paths \
      --path-glob '*.h5' --invert-paths \
      --path-glob 'hf_cache' --invert-paths \
      --path-glob 'models' --invert-paths \
      --path-glob 'datasets' --invert-paths
    ok "Historique nettoyé avec git-filter-repo"

  # Méthode 2 : BFG Repo Cleaner
  elif command -v bfg &>/dev/null; then
    info "Utilisation de BFG..."
    bfg --delete-folders .venv
    bfg --delete-files "*.pt,*.bin,*.safetensors,*.pth,*.ckpt"
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
    ok "Historique nettoyé avec BFG"

  else
    err "Ni git-filter-repo ni bfg trouvés.
  Installation (NixOS) : nix-shell -p git-filter-repo
  Installation (pip)   : pip install git-filter-repo"
  fi

  # GC agressif
  info "Compression du pack Git..."
  git reflog expire --expire=now --all 2>/dev/null || true
  git gc --prune=now --aggressive 2>/dev/null || true

  local new_size
  new_size=$(git count-objects -vH | grep size-pack | awk '{print $2}')
  ok "Nouvelle taille du pack : $new_size"
  echo ""
  warn "⚠️  L'historique a été réécrit. Push forcé requis :"
  echo "   git remote add origin <URL> (si remote perdu)"
  echo "   IDEES_OWNER=1 FORCE_PUSH=1 ./eip_deploy.sh"
}

# ═══════════════════════════════════════════════════════════════════════════
# NOUVELLE BRANCHE DE SPRINT
# ═══════════════════════════════════════════════════════════════════════════
mode_new_sprint() {
  local sprint_name="$1"
  title "🚀 Nouveau sprint : $sprint_name"

  # Vérifier qu'on est propre avant de créer une branche
  local dirty
  dirty=$(git status --porcelain 2>/dev/null || echo "")
  if [[ -n "$dirty" ]]; then
    warn "Changements non commités détectés. Commit automatique avant création de branche."
    git add --all
    CUSTOM_MSG="misc: sauvegarde avant sprint $sprint_name"
    local msg
    msg=$(generate_commit_msg)
    git commit -m "$msg" 2>/dev/null || true
  fi

  # Backup local du sprint actuel
  local_backup

  # Créer la branche
  local branch_name="sprint/${sprint_name}"
  if git show-ref --verify --quiet "refs/heads/$branch_name" 2>/dev/null; then
    warn "Branche '$branch_name' existe déjà. Basculement..."
    git checkout "$branch_name"
  else
    git checkout -b "$branch_name"
    ok "Branche '$branch_name' créée depuis $CURRENT_BRANCH"
  fi

  # Créer le fichier de contexte du sprint
  local sprint_file="brainstorm/SPRINT-${sprint_name}-context.md"
  if [[ ! -f "$sprint_file" ]]; then
    cat > "$sprint_file" << EOF
# Sprint ${sprint_name} — Contexte et Objectifs

**Date de début :** $(date '+%Y-%m-%d')
**Branche :** sprint/${sprint_name}
**Statut :** EN_COURS

## Objectifs

- [ ] TODO

## Livrables attendus

- [ ] TODO

## Notes

EOF
    ok "Fichier de contexte créé : $sprint_file"
  fi

  echo ""
  ok "Sprint '$sprint_name' initialisé sur la branche '$branch_name'"
  info "Prochaine étape : ./eip_deploy.sh pour sauvegarder"
}

# ═══════════════════════════════════════════════════════════════════════════
# STATUS / PROGRESSION
# ═══════════════════════════════════════════════════════════════════════════
mode_status() {
  title "📊 État du dépôt EIP"

  echo -e "${BOLD}Branche courante :${NC} $CURRENT_BRANCH"
  echo -e "${BOLD}Utilisateur      :${NC} $GIT_USER"
  echo ""

  # Taille pack
  local pack_size
  pack_size=$(git count-objects -vH | grep size-pack | awk '{print $2}')
  echo -e "${BOLD}Pack Git         :${NC} $pack_size"

  # État des fichiers
  local unstaged staged untracked
  unstaged=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
  staged=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
  untracked=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
  echo -e "${BOLD}Modifiés (non stagés) :${NC} $unstaged"
  echo -e "${BOLD}Stagés               :${NC} $staged"
  echo -e "${BOLD}Non suivis           :${NC} $untracked"
  echo ""

  # Commits non poussés
  local unpushed
  unpushed=$(git log main --not origin/main --oneline 2>/dev/null || echo "")
  if [[ -n "$unpushed" ]]; then
    warn "Commits non poussés sur main :"
    echo "$unpushed" | head -5 | sed 's/^/  /'
  fi

  # Historique récent
  title "🕐 Historique récent"
  git log --oneline --graph --all -10 2>/dev/null || true

  # Branches
  title "🌿 Branches"
  git branch -a 2>/dev/null | head -15 || true

  # Backups locaux
  title "💾 Backups locaux"
  if [[ -d "$BACKUP_BASE" ]]; then
    ls -1t "$BACKUP_BASE" 2>/dev/null | head -5 | while read -r d; do
      local meta="${BACKUP_BASE}/${d}/.backup_meta"
      if [[ -f "$meta" ]]; then
        local ts branch
        ts=$(grep "^timestamp:" "$meta" | cut -d' ' -f2)
        branch=$(grep "^branch:" "$meta" | cut -d' ' -f2)
        echo "  $d  [$branch]"
      else
        echo "  $d"
      fi
    done
  else
    echo "  Aucun backup trouvé dans $BACKUP_BASE"
  fi

  # STATUS.md résumé
  if [[ -f "STATUS.md" ]]; then
    title "📋 STATUS.md (extrait)"
    head -20 STATUS.md
  fi
}

# ═══════════════════════════════════════════════════════════════════════════
# MODE PRINCIPAL : DEPLOY
# ═══════════════════════════════════════════════════════════════════════════
mode_deploy() {
  local do_push=true
  local do_local=true

  [[ "$MODE" == "local_only" ]] && do_push=false
  [[ "$MODE" == "push_only" ]]  && do_local=false

  title "🚀 EIP Deploy — $(date '+%Y-%m-%d %H:%M:%S')"
  info "Utilisateur : $GIT_USER"
  info "Branche     : $CURRENT_BRANCH"
  echo ""

  check_branch_access "$CURRENT_BRANCH"

  # Y a-t-il des changements ?
  local dirty
  dirty=$(git status --porcelain 2>/dev/null || echo "")
  if [[ -z "$dirty" ]]; then
    info "Aucun changement local."
    if $do_push; then
      info "Pull depuis origin/$CURRENT_BRANCH..."
      git fetch origin 2>/dev/null || warn "fetch échoué (offline ?)"
      git pull --ff-only origin "$CURRENT_BRANCH" 2>/dev/null || \
        git pull --rebase origin "$CURRENT_BRANCH" 2>/dev/null || \
        warn "Pull échoué — peut-être déjà à jour"
      ok "Synchronisé"
    fi
    git log --oneline -3
    exit 0
  fi

  # 1. Vérifier taille fichiers AVANT staging
  check_file_sizes

  # 2. Stager
  title "📁 Staging"
  git add --all
  info "Fichiers stagés :"
  git status --short | head -20
  echo ""

  # 3. Pre-checks qualité
  run_prechecks

  # 4. Backup local
  if $do_local; then
    local_backup
  fi

  # 5. Commit
  title "📝 Commit"
  local msg
  msg=$(generate_commit_msg)
  info "Message : $msg"
  git commit -m "$msg"
  ok "Commit créé"

  # 6. Push GitHub
  if $do_push; then
    title "☁️  Push GitHub"
    git fetch origin 2>/dev/null || warn "fetch échoué"

    # Vérifier taille pack AVANT push
    check_pack_size

    info "Rebase sur origin/$CURRENT_BRANCH..."
    if git pull --rebase origin "$CURRENT_BRANCH" 2>/dev/null; then
      ok "Rebase propre"
    else
      local conflicts
      conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
      if [[ -n "$conflicts" ]]; then
        err "Conflits de merge :
$conflicts
Résoudre puis : git add --all && git rebase --continue && ./eip_deploy.sh --push-only"
      fi
    fi

    if [[ "${FORCE_PUSH:-}" == "1" ]] && [[ "$CURRENT_BRANCH" == "main" ]]; then
      warn "Force-push sur main — opération irréversible !"
      git push --force-with-lease origin "$CURRENT_BRANCH"
    else
      git push origin "$CURRENT_BRANCH"
    fi
    ok "Push réussi sur origin/$CURRENT_BRANCH"
  fi

  # ── Résumé final ──────────────────────────────────────────────────────
  echo ""
  echo -e "${BOLD}${GREEN}═══════════════════════════════════════════${NC}"
  echo -e "${BOLD}${GREEN}  ✅ DEPLOY COMPLET${NC}"
  echo -e "${BOLD}${GREEN}═══════════════════════════════════════════${NC}"
  git log --oneline -3
  echo ""
  $do_local  && echo -e "  💾 Backup local  : ${BACKUP_BASE}/"
  $do_push   && echo -e "  ☁️  GitHub        : origin/$CURRENT_BRANCH"
  echo ""
}

# ═══════════════════════════════════════════════════════════════════════════
# DISPATCH
# ═══════════════════════════════════════════════════════════════════════════
case "$MODE" in
  clean_history)  mode_clean_history ;;
  new_sprint)     mode_new_sprint "$NEW_SPRINT_NAME" ;;
  status)         mode_status ;;
  pull)
    info "Pull depuis origin/$CURRENT_BRANCH..."
    git fetch origin
    git pull --ff-only origin "$CURRENT_BRANCH" || git pull --rebase origin "$CURRENT_BRANCH"
    ok "À jour"
    ;;
  deploy|local_only|push_only) mode_deploy ;;
  *) err "Mode inconnu : $MODE" ;;
esac
