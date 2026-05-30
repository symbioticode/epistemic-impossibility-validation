# Cadre théorique des corollaires du TIE

## Chaîne déductive : Résultat principal → 3 corollaires empiriquement testables

```
Résultat principal du TIE
   → Corollaire 1 : implication pour les benchmarks textuels MAS
   → Corollaire 2 : implication pour les systèmes RLHF multi-agent
   → Corollaire 3 : implication pour les architectures hybrides
```

## Corollaire 1 : Implication pour les benchmarks textuels MAS
**Énoncé formel :** Dans un système multi-agent où les agents communiquent via des canaux de texte naturel, si le canal est auditable (au sens des conditions TIE), alors sa capacité à préserver les gradients d'information nécessaire pour l'apprentissage collaboratif est bornée supérieurement par une fonction de la taille du vocabulaire et de la profondeur de l'arbre de dérivation syntaxique.

**Hypothèses supplémentaires :** 
- Les agents utilisent des architectures de type Transformer pour le traitement du langage
- La tâche est un benchmark de coopération textuelle standard (comme ceux utilisés dans les travaux sur le langage émergent)
- La mesure de préservation du gradient est la norme du jacobien moyen sur l'espace des états latents

**Prédiction testable :** 
Lorsque l'on augmente les contraintes d'auditabilité (par exemple, en nécessitant que les messages soient des programmes valides dans un langage de programmation simple), on observera une décroissance en loi de puissance de la performance collaborative, avec un exposant lié à la complexité de la langue cible.

**Figure cible :** Figure 1 - Performance collaborative vs. contraintes d'auditabilité dans les benchmarks textuels MAS

## Corollaire 2 : Implication pour les systèmes RLHF multi-agent
**Énoncé formel :** Dans un système de aprendizaje par renforcement avec retour humain (RLHF) multi-agent, si le canal de retour humain est auditable, alors il existe un compromis fondamental entre la précision du signal de récompense et la capacité du système à apprendre des comportements complexes nécessitant une exploration fine de l'espace des politiques.

**Hypothèses supplémentaires :**
- Le retour humain est canalisé à travers un dispositif nécessitant une validation formelle (ex. : choix parmi un ensemble fini d'options prédéfinies)
- La tâche RLHF implique l'apprentissage de comportements hiérarchiques ou de stratégies nécessitant une coordination temporelle fine
- La mesure de qualité du signal de récompense est la corrélation entre le signal récompensé et la vraie fonction de récompense sous-jacente

**Prédiction testable :**
Dans les systèmes RLHF où le retour humain passe par un canal auditable, on observera que l'apprentissage de comportements nécessitant une exploration fine (comme ceux avec de nombreux états intermédiaires récompensants) est significativement plus lent que dans les systèmes avec retour continu, même lorsque le nombre total de interactions humain-agent est identique.

**Figure cible :** Figure 2 - Vitesse d'apprentissage RLHF vs. type de canal de retour humain

## Corollaire 3 : Implication pour les architectures hybrides
**Énoncé formel :** Dans une architecture de communication hybride utilisant simultanément plusieurs canaux (texte, latent, CLAIM), si au moins un canal est auditable, alors l'avantage de performance de l'architecture hybride par rapport à l'utilisation exclusive du meilleur canal unique est borné supérieurement par une fonction décroissante de la contrainte d'auditabilité appliquée au canal auditable.

**Hypothèses supplémentaires :**
- L'architecture hybride utilise une mécanisme d'attention ou de gating pour combiner les sorties des différents canaux
- Les canaux non-auditables sont présumés gradient-preserving (comme les espaces latents standards)
- La mesure de performance est la précision sur une tâche de décision nécessitant à la fois expressivité et interprétabilité

**Prédiction testable :**
Lorsque l'on augmente progressivement les contraintes d'auditabilité sur le canal CLAIM dans une architecture hybride, l'amélioration de performance apportée par l'ajout du canal CLAIM suivra une courbe de rendements décroissants, convergant vers zéro lorsque le canal CLAIM devient totalement discret (comme un canal de symboles finis).

**Figure cible :** Figure 3 - Avantage performance hybride vs. contrainte d'auditabilité sur le canal CLAIM