#!/usr/bin/env bash
# cleanup_repo.sh — Retire les artefacts indésirables du suivi Git (version récursive)
# Usage : ./cleanup_repo.sh --dry-run   # Voir ce qui serait supprimé
#         ./cleanup_repo.sh --execute   # Appliquer les suppressions
# Compatibilité : bash 4+, Git 2.23+, Linux/macOS/NixOS

set -euo pipefail

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}🔍 MODE DRY-RUN : aucune modification ne sera appliquée${NC}"
elif [[ "${1:-}" == "--execute" ]]; then
    echo -e "${RED}⚠️  MODE EXÉCUTION : les fichiers seront retirés de l'index Git${NC}"
else
    echo "Usage : $0 [--dry-run|--execute]"
    exit 1
fi

# Patterns à exclure — chaque entrée peut être :
# - un dossier (ex: ".venv") → matche .venv/ et tout son contenu récursif
# - un fichier exact (ex: ".gitignore") → matche uniquement ce fichier
# - un glob (ex: "*.pyc") → matche tous les fichiers avec cette extension
EXCLUDE_PATTERNS=(
    # Environnements Python / Nix
    ".venv" "venv" "env" ".env" ".direnv"
    # Cache Python
    "__pycache__" "*.pyc" "*.pyo" "*.pyd" "*.pyi"
    ".pytest_cache" ".mypy_cache" ".coverage" "htmlcov" ".ruff_cache"
    # Nix
    "result" "result-*"
    # ML / Hugging Face / Modèles
    "*.bin" "*.pt" "*.pth" "*.ckpt" "*.safetensors" "*.onnx" "*.h5" "*.pkl" "*.parquet" "*.dump" "*.mar"
    ".cache" "hf_cache" "hf_hub" "models" "datasets" "downloads" "checkpoints"
    # Logs / Temp / IDE
    "*.log" "*.tmp" "*.temp" "*.swp" "*.swo" "*.lock" "*.pid"
    ".DS_Store" ".vscode" ".idea" "*.sublime-*" "Thumbs.db"
    # Build Python
    "build" "dist" "*.egg-info" ".eggs" "*.whl"
    # Project-specific large outputs (si générés accidentellement)
    "*.zip" "*.tar.gz" "*.tgz" "*.7z"
)

echo -e "${GREEN}🔎 Analyse des fichiers trackés indésirables...${NC}"
FOUND=()

# Fonction pour vérifier si un fichier matche un pattern
matches_pattern() {
    local file="$1"
    local pattern="$2"
    
    # Pattern avec wildcard (ex: "*.pyc")
    if [[ "$pattern" == *"*"* || "$pattern" == *"?"* ]]; then
        # Convertir glob shell en regex extended
        local regex="^$(echo "$pattern" | sed 's/\./\\./g; s/\*/.*/g; s/?/./g')$"
        [[ "$file" =~ $regex ]] && return 0
    # Pattern de dossier (ex: ".venv") → matche le dossier et tout son contenu
    elif [[ -d "$pattern" ]] || [[ "$pattern" =~ ^[a-zA-Z0-9_.-]+$ ]]; then
        [[ "$file" == "$pattern" || "$file" == "$pattern/"* ]] && return 0
    # Fichier exact
    else
        [[ "$file" == "$pattern" ]] && return 0
    fi
    return 1
}

# Récupérer TOUS les fichiers trackés récursivement
# git ls-files liste déjà récursivement, mais on filtre avec des regex ancrées
ALL_TRACKED=$(git ls-files)

for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    if [[ "$pattern" == *"*"* ]]; then
        # Glob pattern : convertir en regex et grep
        regex="(^|/)$(echo "$pattern" | sed 's/\./\\./g; s/\*/[^\/]*/g; s/?/[^\/]/g')$"
        while IFS= read -r file; do
            [[ -n "$file" ]] && FOUND+=("$file")
        done < <(echo "$ALL_TRACKED" | grep -E "$regex" 2>/dev/null || true)
    else
        # Dossier ou fichier exact : match préfixe ou exact
        while IFS= read -r file; do
            if [[ "$file" == "$pattern" || "$file" == "$pattern/"* || "$file" =~ ^"$pattern"/ ]]; then
                [[ -n "$file" ]] && FOUND+=("$file")
            fi
        done < <(echo "$ALL_TRACKED")
    fi
done

# Dédupliquer et trier
if [[ ${#FOUND[@]} -gt 0 ]]; then
    FOUND=($(printf '%s\n' "${FOUND[@]}" | sort -u))
fi

if [[ ${#FOUND[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ Aucun fichier indésirable trouvé dans l'index Git.${NC}"
    exit 0
fi

# Affichage des résultats
echo -e "${YELLOW}📋 ${#FOUND[@]} fichier(s) à retirer du suivi Git :${NC}"
printf '  - %s\n' "${FOUND[@]}" | head -30
[[ ${#FOUND[@]} -gt 30 ]] && echo -e "  ${YELLOW}... et $(( ${#FOUND[@]} - 30 )) autres${NC}"

# Estimation de la taille (si fichiers existent localement)
TOTAL_SIZE=0
COUNT_EXISTING=0
for file in "${FOUND[@]}"; do
    if [[ -f "$file" ]]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        TOTAL_SIZE=$((TOTAL_SIZE + size))
        COUNT_EXISTING=$((COUNT_EXISTING + 1))
    fi
done

if [[ $TOTAL_SIZE -gt 0 ]]; then
    SIZE_MB=$((TOTAL_SIZE / 1024 / 1024))
    echo -e "${YELLOW}📦 Taille estimée à libérer : ~${SIZE_MB} MB (${COUNT_EXISTING}/${#FOUND[@]} fichiers existent localement)${NC}"
else
    echo -e "${YELLOW}📦 Fichiers déjà supprimés localement — seul l'index Git sera nettoyé${NC}"
fi

if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${GREEN}💡 Pour appliquer : $0 --execute${NC}"
    exit 0
fi

# Exécution : retirer de l'index Git sans supprimer les fichiers locaux
echo -e "${GREEN}🗑️  Retrait des fichiers de l'index Git (fichiers locaux conservés)...${NC}"
REMOVED=0

for file in "${FOUND[@]}"; do
    # git rm --cached retire du suivi sans supprimer le fichier local
    if git rm -r --cached "$file" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $file"
        REMOVED=$((REMOVED + 1))
    elif git rm --cached "$file" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $file"
        REMOVED=$((REMOVED + 1))
    else
        echo -e "  ${RED}✗${NC} $file (déjà absent ou erreur)"
    fi
done

# Commit automatique si des fichiers ont été retirés
if [[ $REMOVED -gt 0 ]]; then
    git add .gitignore 2>/dev/null || true
    
    # Message de commit détaillé
    COMMIT_MSG="[SPRINT-0] chore: remove build artifacts and caches from Git tracking

Removed $REMOVED file(s) from Git index:
"
    for file in "${FOUND[@]}"; do
        COMMIT_MSG+="  - $file
"
    done
    COMMIT_MSG+="
These files are now properly ignored via .gitignore.
Local copies preserved; regenerate via nix-shell or pip as needed.

Auto-generated by cleanup_repo.sh --execute"
    
    git commit -m "$
