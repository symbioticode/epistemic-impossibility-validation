# Prompt: Optimisation du calcul du Jacobian pour accélérer l'expérience Sprint 2

## Contexte
L'expérience Sprint 2 nécessite de calculer le Jacobian de chaque canal pour 900 combinaisons (3 canaux × 6 niveaux d'entropie × 50 runs). Le calcul actuel utilise une décomposition en valeurs singulières (SVD) complète pour chaque échantillon, ce qui est extrêmement lent (plusieurs heures pour l'expérience complète).

## Problème
- Chaque appel à `get_jacobian_norm` implique un appel à `torch.autograd.functional.jacobian` suivi d'une SVD.
- Cette opération est le goulot d'étranglement principal de l'expérience.
- Nous devons maintenir la précision nécessaire pour les tests scientifiques tout en réduisant considérablement le temps de calcul.

## Solutions envisagées
1. **Approximation du Jacobian** : Utiliser la méthode de la puissance pour estimer la plus grande valeur singulière (norme spectrale) au lieu de la SVD complète.
2. **Réduction de la dimensionnalité** : Projeter dans un sous-espace avant de calculer le Jacobian.
3. **Mise en cache** : Certains calculs pourraient être réutilisés (à vérifier si applicable).
4. **Vectorisation améliorée** : Optimiser l'utilisation de `torch.autograd.functional.jacobian`.

## Questions spécifiques
1. Quelle précision est acceptable pour l'approximation de la norme spectrale du Jacobian dans le contexte de la validation de l'Hypothèse alt. 1 ?
2. Pourrions-nous utiliser une méthode itérative comme la méthode de la puissance avec un nombre fixe d'itérations (ex: 5-10) pour obtenir une estimation suffisante ?
3. Y a-t-il des parties du calcul du Jacobian qui pourraient être précomputées ou simplifiées compte tenu de la structure spécifique de nos canaux ?
4. Serait-il acceptable de réduire temporairement la précision pendant le développement pour accélérer les tests, puis revenir à la pleine précision pour la course finale ?

## Critères de succès
- Réduire le temps total de l'expérience de plusieurs heures à moins de 30 minutes.
- Maintenir suffisamment de précision pour que les tests statistiques (Mann-Whitney U) et les critères de variance (IQR ≤ 30% de la médiane) restent valides.
- S'assurer que l'approximation n'introduit pas de biais systématique qui pourrait fausser les conclusions concernant l'effondrement du Jacobian du canal texte.

## Références dans le code
- `src/channels.py` : Méthodes `get_jacobian_norm` pour TextChannel, LatentChannel et CLAIMChannel (lignes ~71, ~196, ~302, ~459)
- `src/experiment.py` : Fonction `run_experiment` qui appelle ces méthodes

Merci de fournir des conseils sur l'optimisation la plus appropriée ou de proposer une implémentation spécifique.