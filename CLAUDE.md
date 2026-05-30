# CLAUDE.md — Instructions pour Claude Code Web

## Identité du projet
Chantier de validation expérimentale d'un théorème mathématique.
Repo : epistemic-impossibility-validation
Branche principale : main

## Convention de nommage

Le théorème central du projet s'appelle :
  **TIE — Théorème de l'Impossibilité Épistémique**
  (alias provisoire dans le repo : "Théorème 7.1" / fichier : theorem71_formal.md)

Règle : dans tous les fichiers produits par les instances de travail,
utiliser "TIE" comme désignation courte et "Théorème de l'Impossibilité
Épistémique" comme désignation longue.
Le fichier theorem71_formal.md sera renommé tie_formal.md en Sprint 4
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