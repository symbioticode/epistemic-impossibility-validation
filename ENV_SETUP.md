# ENV_SETUP — Environnement de développement EIP

**Dernière mise à jour :** 30 mai 2026
**Validé sur :** NixOS 25.05 (Andrei)
**Statut Windows/venv :** À valider (Sprint 1)

---

## Contexte et décisions d'architecture

Ce projet tourne sur **NixOS** avec `nix-shell` comme gestionnaire d'environnement
reproductible. Le choix de Nix plutôt que `venv` ou `conda` est délibéré :
reproductibilité bit-for-bit entre sessions, pas de pollution système, rollback
trivial. La contrepartie : les binaires Nix sont volumineux et ne doivent **jamais**
être commités dans git.

Le fichier `shell.nix` à la racine définit l'environnement complet. Une session
s'ouvre avec `nix-shell` depuis le dossier du projet.

---

## 1. Prérequis système

### NixOS / nix-shell (environnement principal)

```bash
# Vérifier que nix est disponible
nix --version   # attendu : nix 2.x

# Entrer dans l'environnement du projet
cd ~/Projects/54_EIP/epistemic-impossibility-validation
nix-shell       # charge shell.nix automatiquement
```

Le `shell.nix` installe : Python 3.12, PyTorch (CPU), Transformers, matplotlib,
seaborn, scipy, pandas, numpy, pytest.

> **Attention NixOS :** Ne jamais faire `pip install` en dehors d'un venv ou de
> nix-shell. Les paquets système Nix sont en read-only.

### Outils Git additionnels (nettoyage historique)

```bash
# git-filter-repo — purger les artefacts de l'historique git
nix-shell -p git-filter-repo

# Utilisation via eip_deploy.sh
./eip_deploy.sh --clean-history
```

`git-filter-repo` est préféré à `BFG Repo Cleaner` car il est maintenu activement,
disponible dans nixpkgs, et ne nécessite pas Java.

---

## 2. Structure des outils projet

Tous les scripts opérationnels sont dans `tools/` et versionnés dans git.

```
tools/
├── eip_deploy.sh       # script principal : commit + backup + push
├── eip_status.sh       # tableau de bord progression
├── verify_sprint0.sh   # validation checklist Sprint 0
├── shell.nix           # environnement Nix reproductible
└── legacy/
    ├── deploy.sh       # ancien script (remplacé par eip_deploy.sh)
    └── cleanup_repo.sh # ancien script de nettoyage (intégré dans eip_deploy.sh)
```

> **Convention :** les scripts à la racine (`verify_sprint0.sh`) sont des raccourcis
> temporaires. Ils migrent dans `tools/` au début du sprint suivant.

---

## 3. Workflow quotidien

### Ouvrir une session de travail

```bash
cd ~/Projects/54_EIP/epistemic-impossibility-validation
nix-shell                    # charge l'environnement
./eip_status.sh              # vérifier l'état avant de commencer
```

### Sauvegarder en cours de sprint

```bash
# Commit + backup local + push GitHub (commande normale)
./eip_deploy.sh

# Message personnalisé
./eip_deploy.sh -m "theory: compléter lemme_auditabilite"

# Backup local uniquement (offline, ou avant opération risquée)
./eip_deploy.sh --local-only
```

### Démarrer un nouveau sprint

```bash
# Crée la branche sprint/NOM, backup local automatique, fichier de contexte
./eip_deploy.sh --new-sprint 1

# Vérifier
./eip_status.sh
```

### Récupérer un backup local

Les backups sont dans `~/.eip_backups/`, un dossier par sauvegarde avec
`.backup_meta` (timestamp, branche, dernier commit).

```bash
ls ~/.eip_backups/
cp -r ~/.eip_backups/<nom_backup>/ /chemin/de/restauration/
```

---

## 4. Règles de branche et accès

| Branche | Qui | Commande push |
|---------|-----|---------------|
| `main` | Andrei seulement | `IDEES_OWNER=1 ./eip_deploy.sh` |
| `governance/*` | Andrei seulement | `IDEES_OWNER=1 ./eip_deploy.sh` |
| `collab/*` | Thierry | `./eip_deploy.sh` (tag `[EXTERNE]` auto) |
| `sprint/*` | Tout le monde | `./eip_deploy.sh` |
| `feature/*` `research/*` | Tout le monde | `./eip_deploy.sh` |

La variable d'environnement `IDEES_OWNER=1` est à ajouter dans `~/.bashrc` ou
`~/.zshrc` sur la machine d'Andrei uniquement.

---

## 5. Limites git et sécurité

`eip_deploy.sh` applique deux garde-fous automatiques avant chaque push :

- **Fichier individuel > 50 MB** → push bloqué avec indication du fichier
- **Pack git > 95 MB** → push bloqué avec indication de `--clean-history`

Ces limites protègent contre la répétition de l'incident Sprint 0 (282 MB de pack
git causé par `.venv` commité accidentellement dans l'historique).

### Nettoyer l'historique si nécessaire

```bash
# Purge .venv, __pycache__, *.pt, *.bin, *.safetensors de l'historique
./eip_deploy.sh --clean-history

# Puis reconnecter le remote (filter-repo le déconnecte par sécurité)
git remote add origin https://github.com/symbioticode/epistemic-impossibility-validation.git

# Push forcé (réécriture d'historique requiert --force)
IDEES_OWNER=1 FORCE_PUSH=1 ./eip_deploy.sh
```

---

## 6. Patterns .gitignore critiques

Les patterns suivants doivent **toujours** être présents dans `.gitignore` :

```
.venv/          # environnement Python virtuel
__pycache__/    # cache Python compilé
*.pt *.bin      # poids de modèles PyTorch / binaires ML
*.safetensors *.pth *.ckpt   # autres formats de modèles
.cache/ hf_cache/ models/ datasets/   # caches Hugging Face
result result-*  # liens symboliques Nix
```

> **Leçon apprise (Sprint 0) :** Le `.venv` a été commité avant que `.gitignore`
> soit en place, gonflant le pack git à 282 MB. Toujours vérifier `.gitignore`
> avant le premier `git add`.

---

## 7. Validation de l'environnement

```bash
# Vérification complète Sprint 0
./verify_sprint0.sh

# Tableau de bord progression
./eip_status.sh

# Rapport Markdown horodaté
./eip_status.sh --report

# État synchronisation GitHub
./eip_status.sh --sync
```

---

## 8. Environnement alternatif : Python venv (Windows / sans Nix)

> **Statut :** À valider — prévu en fin de Sprint 1

L'objectif est de vérifier que les scripts Python (`src/*.py`) produisent les
mêmes résultats numériques avec `venv` sur Windows que sous NixOS avec nix-shell.

### Procédure prévue

```powershell
# Windows — PowerShell
cd C:\Projects\epistemic-impossibility-validation
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Lancer les tests de reproductibilité
python -m pytest tests/
```

### Points de validation

- [ ] Imports identiques (`torch`, `transformers`, `scipy`)
- [ ] Résultats numériques stables (seed fixe à 42 dans `src/experiment.py`)
- [ ] Fichiers CSV générés identiques (à ±1e-6 près)
- [ ] Scripts `eip_deploy.sh` / `eip_status.sh` fonctionnels sous Git Bash ou WSL2

> **Note :** Les scripts bash supposent `bash 4+`. Sur Windows natif, utiliser
> Git Bash ou WSL2. PowerShell n'est pas supporté.

---

## 9. Incident log

| Date | Incident | Cause | Résolution |
|------|----------|-------|------------|
| 2026-05-30 | Pack git 282 MB | `.venv` commité avant `.gitignore` | `git-filter-repo --clean-history` → 29 MB |
| 2026-05-30 | Sprint 0.5 perdu | `git reset --hard` avant push | Reconstruction depuis contexte session |

---

*Fichier maintenu dans `tools/` — mettre à jour après chaque incident ou changement d'environnement.*
