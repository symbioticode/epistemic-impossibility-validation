# REV-S5 — Rapport Analyste (Sprint 5)
**Date :** Mai 2026
**Modèle :** Jules (Engineer) agissant comme Analyste
**Chantier :** epistemic-impossibility-validation

## Q1 — Attributabilité causale
Les différences observées entre les canaux (Figure 2) sont clairement attribuables au canal lui-même.
- La règle d'update (gradient descent) est strictement identique pour tous les canaux.
- La seule variable changeant entre les groupes est la fonction `encode` du canal utilisé pour transmettre le signal de gradient.
- Le canal texte bloque le signal de gradient (approximation discrète), ce qui conduit au plafonnement immédiat de l'accuracy, tandis que le canal latent (gradient-preserving) permet une convergence rapide vers l'optimum.
- Pour Figure 3 (RLHF), bien que le signal s'annule rapidement pour tous les niveaux, la distinction à Round 0 montre que κ=0.9 commence bien à 0 (conformément à l'auditabilité), contrairement à κ=0.3 et 0.6.

## Q2 — Hypothèses supplémentaires déclarées (R-COROL-01)
Les hypothèses H4–H11 ont été implémentées comme suit :
- **H4–H7 (Corol 1)** : Tâche de classification 4 classes validée. H7 confirmée par l'expérience.
- **H8–H11 (Corol 2)** : Le signal RLHF est bien modélisé par la norme du gradient de la récompense par rapport à $h$. L'auditabilité induite par κ > 0.7 est implémentée par un détachement explicite du graphe d'autograd, simulant l'impossibilité de rétropropager à travers un canal auditable (discret).

**Note critique** : Une hypothèse implicite réside dans la "soft-approximation" utilisée pour TextChannel. Sans cette approximation, le gradient serait nul partout. L'expérience montre que même avec une approximation, le canal texte reste largement inférieur.

## Conclusion
Le Sprint 5 est validé pour le Corollaire 1. Le Corollaire 2 présente un résultat négatif partiel (signal s'annulant trop vite), documenté sous `QO-S5-02`.
