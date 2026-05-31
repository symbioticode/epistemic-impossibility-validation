# REV-S3 — Rapport d'Analyse Sprint 3

**Date :** 2026-05-31
**Analyste :** Jules (Instance isolée)
**Sprint :** 3 — Figures et tables

## Q1 — Cohérence figure / données
**Question :** Les valeurs numériques dans Table 1 et les points visualisés dans Figure 1 sont-ils cohérents avec `raw_results.csv` ?

**Analyse :**
- Une vérification indépendante des médianes et IQRs a été effectuée sur `results/raw_results.csv`.
- Valeurs de référence (Table 1) :
    - Canal A (texte), ε=0.05 : 0.0042 ± 0.0021
    - Canal B (latent), ε=2.00 : 1.9400 ± 0.0584
- Ces valeurs correspondent exactement à l'agrégation directe des données brutes.
- Aucun filtrage caché ou transformation non déclarée n'a été détecté. La figure 1 utilise une échelle linéaire pour l'axe Y et logarithmique pour l'axe X (entropie), ce qui est cohérent avec la distribution des données.

**Verdict :** COHÉRENCE CONFIRMÉE.

## Q2 — Lisibilité ICLR
**Question :** La Figure 1 permet-elle à un lecteur de vérifier visuellement l'hypothèse centrale ?

**Analyse :**
- **Hypothèse centrale** : Effondrement du jacobien pour le canal texte à entropie basse.
- **Observation (QO-S3-01)** : Contrairement à l'attendu, le jacobien du canal texte (Canal A) augmente légèrement quand l'entropie diminue (de 0.0009 à 0.0042). Cependant, il reste à des ordres de grandeur extrêmement bas par rapport aux canaux B (~2.0) et C (~0.4).
- **Lisibilité** : Les barres d'erreur (IQR) sont bien visibles pour les canaux B et C, mais quasi-invisibles pour le canal A car ses valeurs sont proches de zéro à l'échelle linéaire.
- **Distinguabilité** : Les couleurs (bleu, vert, rouge) et les marqueurs (o, s, ^) assurent une bonne lisibilité en noir et blanc.

**Verdict :** LISIBILITÉ CONFIRMÉE pour la comparaison inter-canaux. Cependant, le pattern spécifique d'effondrement (décroissance quand entropy → 0) n'est pas observé pour le Canal A (résultat négatif QO-S3-01).

## Notes additionnelles (QO-S3-02)
- La calibration du Canal C (Table 3) montre une corrélation de 0.28, ce qui est sous le seuil d'alerte de 0.50 (**QO-S1-01**). Cela indique que le Canal C, bien que conservant mieux le gradient que le Canal A, a une fidélité sémantique limitée dans cette configuration.
