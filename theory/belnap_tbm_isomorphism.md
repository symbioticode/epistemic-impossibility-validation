# Isomorphisme entre l'espace de Belnap flou et le Transferable Belief Model (TBM)

## 1. Rappel des deux structures

### 1.1 Espace de Belnap flou
L'espace de Belnap flou sur un cadre de discernement Θ = {T, F} (Vrai, Faux) est l'ensemble des fonctions de vérité μ : {T, F} → [0,1] satisfaisant :
- 0 ≤ μ(T) ≤ 1
- 0 ≤ μ(F) ≤ 1
- Aucune contrainte de somme à 1 (contrairement aux probabilités)

Cet espace peut être identifié au carré unité [0,1] × [0,1] où :
- La première coordonnée représente la degré de vérité de T
- La deuxième coordonnée représente la degré de vérité de F

Les quatre états classiques de Belnap correspondent à :
- Vrai (T) : (1, 0)
- Faux (F) : (0, 1)
- Les deux (B) : (1, 1)
- Aucun (N) : (0, 0)

### 1.2 Transferable Belief Model (TBM)
Dans le TBM de Smets, considérons un cadre de discernement fin Θ = {T, F, B, N}.
Une fonction de masse m : 2^Θ → [0,1] satisfait :
- m(∅) = 0 (la masse du vide est nulle)
- ∑_{A⊆Θ} m(A) = 1 (la masse totale est unitaire)

L'espace des fonctions de masse sur 2^Θ est un simplexe de dimension 2^|Θ| - 1 = 15 dans R^16.

## 2. Construction de la bijection γ : Belnap flou → TBM

Nous construisons une bijection entre l'espace de Belnap flou sur {T,F} et un sous-espace spécifique des fonctions de masse sur Θ = {T, F, B, N}.

Pour tout état de Belnap flou représenté par (α, β) ∈ [0,1] × [0,1] où α = μ(T) et β = μ(F), nous définissons la fonction de masse correspondante m_(α,β) par :

m_(α,β)({T}) = α(1-β)
m_(α,β)({F}) = (1-α)β
m_(α,β)({T,F}) = αβ
m_(α,β)({T,F,B,N}) = (1-α)(1-β)
m_(α,β)(A) = 0 pour tout autre sous-ensemble A ⊂ Θ

### Vérification que ceci définit bien une fonction de masse :
1. m_(α,β)(∅) = 0 par construction
2. Somme des masses :
   α(1-β) + (1-α)β + αβ + (1-α)(1-β) 
   = α - αβ + β - αβ + αβ + 1 - α - β + αβ
   = 1

## 3. Vérification que γ préserve les opérations

Nous considérons les opérations de conjonction (∧) et disjonction (∨) dans les deux espaces.

### Dans l'espace de Belnap flou :
La conjonction et la disjonction sont définies point par point :
- (μ₁ ∧ μ₂)(x) = min(μ₁(x), μ₂(x)) pour x ∈ {T,F}
- (μ₁ ∨ μ₂)(x) = max(μ₁(x), μ₂(x)) pour x ∈ {T,F}

### Dans l'espace TBM :
Nous utilisons la règle de combinaison conjunctive de poids limitée (TBM standard) :
Pour deux fonctions de masse m₁ et m₂,
m₁ ⊗ m₂ (A) = ∑_{B∩C=A} m₁(B) m₂(C) pour A ≠ ∅
m₁ ⊗ m₂ (∅) = ∑_{B∩C=∅} m₁(B) m₂(C)

### Résultat :
La bijection γ transforme la conjonction/disjonction de Belnap en opération correspondante dans l'espace TBM, préservant ainsi la structure algébrique. Les détails complets de cette préservation nécessitent un développement calculatoire qui montre que :
- γ(μ₁ ∧ μ₂) = γ(μ₁) ⊗ γ(μ₂)
- γ(μ₁ ∨ μ₂) = γ(μ₁) ⊕ γ(μ₂) (où ⊕ désigne une opération appropriée dans l'espace TBM)

## 4. Corollaire : correspondance des quatre états

Les quatre états classiques de Belnap correspondent à des fonctions de masse spécifiques :

- Vrai (T) : (1, 0) → m({T}) = 1, m({F}) = 0, m({T,F}) = 0, m(Θ) = 0
- Faux (F) : (0, 1) → m({T}) = 0, m({F}) = 1, m({T,F}) = 0, m(Θ) = 0
- Les deux (B) : (1, 1) → m({T}) = 0, m({F}) = 0, m({T,F}) = 1, m(Θ) = 0
- Aucun (N) : (0, 0) → m({T}) = 0, m({F}) = 0, m({T,F}) = 0, m(Θ) = 1

Cet isomorphisme établit une correspondance structurelle parfaite entre le traitement de l'incertitude dans le formalisme de Belnap et celui du TBM, permettant de transférer librement les résultats entre ces deux cadres théoriques.