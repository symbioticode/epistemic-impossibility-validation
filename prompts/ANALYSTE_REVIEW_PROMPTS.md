# Prompts pour la revue Analyste externe - Sprint 1

## Contexte
Cette revue concerne l'implémentation des trois canaux de communication pour le projet EIP (Epistemic Impossibility Validation) - Sprint 1 : Instrumentation des canaux.

## Livrables à examiner
1. `src/channels.py` - Implémentation des trois canaux et protocole commun
2. `src/calibration.py` - Fonctions de calibration et vérification
3. `tests/test_channels.py` - Tests unitaires minimaux obligatoires

## Questions spécifiques à adresser (Q1-Q2 du SPRINT-1-context.md)

### Q1 — Pure Function Contract
**Objectif** : Détecter toute closure sur un état figé qui ferait que `encode(h_A) == encode(h_B)` pour `h_A ≠ h_B`.

**Zones d'examen prioritaires** :
- Dans `TextChannel.encode()` : Vérifier que aucune variable d'état n'est utilisée en dehors du paramètre `h`
- Dans `LatentChannel.encode()` : Vérifier que les poids du MLP ne sont pas modifiés entre les appels
- Dans `CLAIMChannel.encode()` : Vérifier que aucune variable d'état n'influence le résultat
- Rechercher toute utilisation de variables membres non constantes dans les méthodes `encode`

**Points de contrôle spécifiques** :
- Ligne ~63 dans `TextChannel.encode()` : `h = h.clone()` - bon point de départ
- Ligne ~174 dans `LatentChannel.encode()` : `h = h.clone()` - bon point de départ
- Ligne ~341 dans `CLAIMChannel.encode()` : `h = h.clone()` - bon point de départ
- Vérifier que aucune modification d'attributs d'instance ne se produit dans `encode()`

### Q2 — Reproductibilité
**Objectif** : Vérifier que le canal C (CLAIMChannel) est bit-à-bit reproductible entre deux sessions Python distinctes (même seed).

**Zones d'examen prioritaires** :
- Toute opération non-déterministe dans `CLAIMChannel.encode()` :
  - Opérations CUDA (non applicable ici car nous utilisons CPU)
  - Hash Python aléatoire
  - Opérations dépendantes de l'ordre d'exécution
  - Appels à des fonctions non pures

**Points de contrôle spécifiques** :
- Dans `CLAIMChannel._determine_proposition()` : La logique dépend-elle de l'ordre d'itération du dictionnaire `belief_mass` ?
- Dans `CLAIMChannel._determine_belnap_state()` : Même question pour l'itération sur `belief_mass`
- Dans `calibrate_claim_channel()` : Le k-NN introduit-il du non-déterminisme ? (devrait être déterministe avec seed fixé)
- Vérifier l'utilisation de `torch.manual_seed()` et `np.random.seed()` dans les constructeurs

## Aspects supplémentaires à valider

### Conformité aux contrats API
Vérifier que chaque classe respecte exactement les contrats spécifiés dans SPRINT-1-context.md :

#### TextChannel
- `encode(h)` déterministe pour h fixé et seed fixé
- Aucune modification de h en place
- `get_jacobian_norm(h)` retourne ≥ 0
- `get_output_entropy(h)` retourne valeur dans [0, log(vocab_size)]

#### LatentChannel
- `encode(h)` déterministe pour h fixé et seed fixé
- `‖J_C(h)‖₂ ≥ 0.5` pour tout h (gradient-preserving par construction)
- `get_output_entropy(h)` retourne valeur dans [0, log(50)]

#### CLAIMChannel
- `encode(h)` déterministe pour h fixé et seed fixé
- `CLAIM.belief_mass` satisfait Σ_{A ⊆ Θ} m(A) = 1
- `CLAIM.belief_mass[frozenset()] = m(∅) explicite ≥ 0`
- `get_jacobian_norm(h)` retourne ≥ 0
- `get_output_entropy(h)` retourne valeur dans [0, log(2^|Θ|)]
- `inject_conflict(h, conflict_level)` respecte `CLAIM.belief_mass[frozenset()] = conflict_level ± 0.01`

### Qualité du code
- Respect des conventions PEP 8
- Commentaires utiles (mais pas excessifs)
- Gestion appropriée des erreurs
- Lisibilité et maintenabilité

## Instructions pour l'Analyste
1. Examiner les trois fichiers principaux listés ci-dessus
2. Répondre spécifiquement aux questions Q1 et Q2 avec des références aux lignes de code si des problèmes sont trouvés
3. Vérifier la conformité aux contrats API pour chaque canal
4. Confirmer que tous les tests unitaires passent (ils passent actuellement en local)
5. Fournir un rapport indiquant :
   - Aucune closure détectée pour Q1 (ou détails si trouvée)
   - Reproductibilité confirmée pour Q2 (ou détails si non confirmée)
   - Toute non-conformité aux contrats API
   - Recommandations d'amélioration le cas échéant

## Fichiers de référence
- SPRINT-1-context.md : Spécifications détaillées du Sprint 1
- theory/theorem71_formal.md : Définition formelle du théorème TIE (pour contexte)
- VARIABLES.md : Paramètres techniques de référence
- STATUS.md : État actuel du projet (Sprint 1 terminé)

## Note importante
Seul le fichier `theorem71_formal.md` pourra être renommé en `tie_formal.md` lors du Sprint 4. Ne pas modifier ce fichier pendant cette revue.