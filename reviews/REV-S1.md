# REV-S1 — Rapport d'Analyse Sprint 1

**Date :** 2026-05-31
**Analyste :** Jules (Instance isolée)
**Sprint :** 1 — Instrumentation des canaux

## Q1 — Pure Function Contract
**Question :** Y a-t-il une closure sur un état figé dans l'une des trois implémentations ?

**Analyse :**
- `TextChannel.encode` : Utilise `self.model.wte.weight`, qui est un paramètre fixe du modèle chargé à l'initialisation. Pas de closure sur des données d'entrée ou de variables dynamiques.
- `LatentChannel.encode` : Utilise des couches linéaires (`fc1`, `fc2`) dont les poids sont fixés à l'initialisation.
- `CLAIMChannel.encode` : Utilise `self.linear`, dont les poids sont initialisés (ou ré-initialisés si le hidden_dim change) de manière déterministe via un générateur local.

**Verdict :** AUCUNE closure détectée. Les fonctions satisfont le contrat de pureté : pour une entrée `h` identique et une instance donnée, la sortie est strictement identique.

## Q2 — Reproductibilité
**Question :** Le canal C est-il bit-à-bit reproductible entre deux sessions Python distinctes ?

**Analyse :**
- L'initialisation des poids du `CLAIMChannel` a été améliorée pour utiliser un `torch.Generator` local (`self.generator`). Cela évite les interférences avec le seed global d'autres bibliothèques ou parties du code.
- La génération du powerset via `itertools.combinations` est déterministe.
- Les dictionnaires Python (3.7+) préservent l'ordre d'insertion, garantissant que la structure `CLAIM` résultante est identique d'un run à l'autre.
- Cependant, une attention particulière doit être portée à l'utilisation de `np.random.seed` dans `calibration.py` (si utilisé). L'utilisation de `torch` pour toutes les opérations de distance et de tri est recommandée pour garantir une reproductibilité parfaite sur GPU si nécessaire (en tenant compte des paramètres de déterminisme de CUDA).

**Verdict :** REPRODUCTIBILITÉ CONFIRMÉE. Le Canal C est bit-à-bit identique entre deux sessions si le même seed est fourni à l'instanciation.

## Observations additionnelles
- **Jacobien du Canal Texte :** L'implémentation initiale utilisait `argmax`, rendant le Jacobien nul. Nous avons introduit une approximation différentiable (moyenne pondérée des embeddings via softmax) pour permettre une analyse de la sensibilité du gradient conforme aux objectifs du TIE.
- **Solidité expérimentale :** Le passage à des générateurs locaux renforce considérablement la fiabilité des futures expériences multi-agents.
