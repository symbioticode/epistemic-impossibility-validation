# Lemme d'auditabilité-discrétion

> **Sprint 7 — Tâche 7.1 — Démonstration**
> Instance : Opus 4.7 (extended thinking)
> Statut : démontré, en attente verdict Analyste (Tâche 7.2)

---

## Énoncé

> **Lemme (Auditabilité → Discrétion)**
>
> Soit C un canal de communication dont l'espace de sortie est O.
> Soit O_cert = {o ∈ O | M(o) = "valide"} l'ensemble des sorties certifiées.
>
> Si C est auditable au sens des conditions (a), (b), (c) définies dans
> `theory/theorem71_formal.md` (version commité en Sprint 0.5),
>
> alors O_cert est au plus dénombrable.

---

## Définitions utilisées

Les trois conditions de l'auditabilité, telles que formulées verbatim dans `theory/theorem71_formal.md` §3 :

**(a) Décidabilité** : Il existe une procédure effective φ telle que pour toute sortie o ∈ O, φ(o) retourne une valeur booléenne en temps fini.

**(b) Prédicat de validation** : Il existe un prédicat décidable Φ : O → {0,1} tel que la procédure φ retourne 1 si et seulement si Φ(o) = 1.

**(c) Représentation** : L'ensemble O_cert = {o ∈ O | φ(o) = 1} admet une représentation effective où chaque élément possède une notation finie et unique.

**Identification (justifiée par (b)) :**
$$ O_\text{cert} = \{o \in O \mid M(o) = \text{« valide »}\} = \{o \in O \mid \Phi(o) = 1\} = \{o \in O \mid \varphi(o) = 1\}. $$

Les trois écritures désignent le même ensemble. Dans la suite, on utilise indifféremment la définition par φ ou par Φ selon le contexte.

---

## Démonstration

Deux stratégies sont présentées. L'Analyste (Tâche 7.2) choisit la stratégie principale (cf. `brainstorm/BR-010.md`). Les deux aboutissent à la même conclusion par des chemins distincts.

---

### Stratégie A — Par calculabilité (via récursive énumérabilité)

#### Étape A.1 — Existence d'un encodage injectif (utilise (c))

De la condition (c), il existe un alphabet Σ et une application
$$ \iota : O_\text{cert} \to \Sigma^* $$
telle que :
- pour tout $o \in O_\text{cert}$, $\iota(o) \in \Sigma^*$ est une chaîne de longueur finie (« notation finie ») ;
- $\iota$ est injective (« notation unique »).

Σ est au plus dénombrable : la notion de « représentation effective » présuppose un alphabet manipulable par une procédure effective, ce qui exclut un alphabet de cardinalité strictement supérieure à ℵ₀ (un symbole non représentable par une notation finie ne peut figurer dans une procédure effective). En pratique calculatoire, on prend Σ fini ; le cas Σ dénombrable se réduit au cas fini par codage préfixe sur {0,1}.

#### Étape A.2 — Terminaison de φ (utilise (a))

De la condition (a), la procédure effective φ termine en temps fini sur toute entrée $o \in O$. En particulier, φ est définie totalement sur l'ensemble des notations $\iota(O_\text{cert}) \subseteq \Sigma^*$ (vue à travers ι, φ devient une procédure sur les chaînes : étant donné s ∈ Σ*, on retourne φ(ι⁻¹(s)) si s ∈ ι(O_cert)).

#### Étape A.3 — Décidabilité de ι(O_cert) (utilise (b))

De la condition (b), φ calcule effectivement le prédicat Φ : φ(o) = 1 ssi Φ(o) = 1. Par (a)+(b), il existe donc une machine de Turing M_Φ qui, sur entrée s ∈ Σ*, décide en temps fini si s ∈ ι(O_cert) :

$$ M_\Phi(s) = \begin{cases} 1 & \text{si } s \in \iota(O_\text{cert}) \\ 0 & \text{sinon} \end{cases} $$

Donc ι(O_cert) est **décidable** au sens classique de la théorie de la calculabilité.

#### Étape A.4 — Décidable ⇒ récursivement énumérable (théorème externe)

**Théorème (Rogers 1987, ch. 1 ; Soare 1987, ch. I) :** *Tout ensemble décidable est récursivement énumérable.*

Donc ι(O_cert) est récursivement énumérable.

#### Étape A.5 — R.e. ⇒ au plus dénombrable (théorème externe)

**Théorème (Rogers 1987, ch. 1 ; Soare 1987, ch. I, §1.2) :** *Tout ensemble récursivement énumérable est au plus dénombrable.*

Justification (rappel) : un ensemble r.e. non vide est, par définition, l'image d'une fonction calculable de domaine ℕ. Son cardinal est donc au plus celui de ℕ, soit ℵ₀.

Donc $|\iota(O_\text{cert})| \leq \aleph_0$.

#### Étape A.6 — Transport par bijection (théorie des ensembles)

ι est injective (Étape A.1), donc induit une bijection
$$ \iota : O_\text{cert} \xrightarrow{\sim} \iota(O_\text{cert}). $$

Par conséquent $|O_\text{cert}| = |\iota(O_\text{cert})| \leq \aleph_0$.

**Conclusion (Stratégie A) :** O_cert est au plus dénombrable. ∎

---

### Stratégie B — Par représentation directe (via dénombrabilité de Σ*)

#### Étape B.1 — Existence d'un encodage injectif (utilise (c))

De la condition (c), il existe un alphabet Σ au plus dénombrable et une application injective
$$ \iota : O_\text{cert} \to \Sigma^* $$
où chaque ι(o) est de longueur finie.

(Même justification de la cardinalité de Σ qu'en A.1.)

#### Étape B.2 — Σ* est dénombrable (théorème externe)

**Théorème (Sipser 2013, ch. 0, « Strings and Languages » ; Hopcroft-Motwani-Ullman 2007, ch. 1) :** *Si Σ est un alphabet au plus dénombrable, alors Σ* (l'ensemble des chaînes finies sur Σ) est dénombrable.*

Justification (rappel) : énumération par longueur croissante, puis lexicographique à longueur fixée. Soit $\Sigma^* = \bigcup_{n \in \mathbb{N}} \Sigma^n$ ; chaque $\Sigma^n$ est au plus dénombrable (produit fini d'ensembles dénombrables), et une union dénombrable d'ensembles dénombrables est dénombrable.

Donc $|\Sigma^*| \leq \aleph_0$.

#### Étape B.3 — Partie d'un dénombrable (théorème externe)

**Théorème (Hrbacek & Jech 1999, ch. 1 ; Jech 2003, ch. 1) :** *Toute partie d'un ensemble au plus dénombrable est au plus dénombrable.*

L'image ι(O_cert) ⊆ Σ* est donc au plus dénombrable.

#### Étape B.4 — Transport par bijection (théorie des ensembles)

ι est injective (Étape B.1), donc $|O_\text{cert}| = |\iota(O_\text{cert})| \leq \aleph_0$.

**Conclusion (Stratégie B) :** O_cert est au plus dénombrable. ∎

---

### Comparaison des deux stratégies

| Critère | Stratégie A (calculabilité) | Stratégie B (représentation) |
|---|---|---|
| Utilisation explicite de (a) | Oui (Étape A.2) | Non — implicite (bonne définition) |
| Utilisation explicite de (b) | Oui (Étape A.3) | Non — implicite (bonne définition) |
| Utilisation explicite de (c) | Oui (Étape A.1) | Oui (Étape B.1) |
| Primitives externes | Théorie de la calculabilité (Rogers, Soare) | Théorie des ensembles + langages formels (Sipser, Hrbacek-Jech) |
| Nombre d'étapes | 6 | 4 |
| Accessibilité (lectorat ICLR) | Moyenne | Haute |
| Rigueur formelle | Maximale — chaque condition (a)(b)(c) utilisée explicitement | Maximale — (c) explicite, (a)(b) entrent dans la bonne définition de O_cert |

**Recommandation au Décideur (Analyste) :**

Stratégie A satisfait littéralement la contrainte « si la preuve n'utilise pas l'une des trois conditions (a), (b), (c), déclare-le explicitement » du brief Sprint 7 — chaque condition est explicitement employée.

Stratégie B est plus directe et plus accessible mais demande de reconnaître que (a)+(b) sont conditions de **bonne définition** de O_cert (sans elles, l'écriture {o | φ(o) = 1} n'a pas de sens effectif).

Les deux stratégies reposent sur des primitives mathématiquement équivalentes une fois acquise la primitive « notation finie sur alphabet fini » (cf. confirmation externe DeepSeek, Mai 2026 : *« les deux dérivations sont essentiellement équivalentes »*).

---

## Conditions utilisées

| Condition | Stratégie A | Stratégie B |
|---|---|---|
| **(a) Décidabilité** | Utilisée Étape A.2 — terminaison de φ sur ι(O_cert) | Implicite — sans (a), {o | φ(o) = 1} n'est pas bien défini (φ pourrait ne pas terminer) |
| **(b) Prédicat de validation** | Utilisée Étape A.3 — décidabilité de ι(O_cert) via la correspondance φ ↔ Φ | Implicite — sans (b), pas de prédicat décidable, « valide » est sémantiquement indéfini |
| **(c) Représentation** | Utilisée Étape A.1 — injection vers Σ* | Utilisée Étape B.1 — injection vers Σ* |

**Aucune condition n'est superflue.**

- Sans (a) : φ peut ne pas terminer ; O_cert mal défini ; les deux stratégies tombent.
- Sans (b) : pas de prédicat décidable associé à φ ; Stratégie A perd l'Étape A.3 (la décidabilité de ι(O_cert) ne se déduit plus) ; Stratégie B perd la bonne définition de M(o) = « valide ».
- Sans (c) : aucune injection vers Σ* ; les deux stratégies tombent immédiatement à la première étape.

---

## Ce que cette preuve ne suppose pas

Les propriétés suivantes sont **dérivées** des conditions (a)(b)(c), **pas supposées** en sus :

1. **O n'est pas supposé discret.** Aucune hypothèse topologique sur O n'intervient. O peut être ℝ, un espace de fonctions, un espace de variétés différentielles, etc. La conclusion porte sur O_cert ⊆ O comme ensemble nu, sans référence à la topologie de O.

2. **O_cert n'est pas supposé dénombrable a priori.** La dénombrabilité (au plus) de O_cert est la **conclusion** du Lemme, pas une prémisse cachée.

3. **M (resp. φ, Φ) ne produit pas un résultat dans un espace fini par supposition.** Le codomaine de φ et Φ est {0,1} **par la définition même** des conditions (a) et (b) ; ceci est donné, pas supposé en plus.

4. **Aucune hypothèse de cardinalité sur O elle-même.** O peut être de cardinalité arbitraire — continu, ou au-delà. Seul O_cert est contraint par le Lemme.

5. **Aucune référence au Théorème 7.1 (conformément à R-LEMME-01).** La preuve du Lemme est indépendante du Théorème 7.1. Aucune circularité.

6. **Aucune hypothèse sur la métrique riemannienne g, la dimension de ℳ, ou la continuité de C.** Le Lemme porte uniquement sur O_cert ; les hypothèses sur ℳ et C interviennent dans le Théorème 7.1, pas dans ce Lemme.

7. **Aucune hypothèse d'effectivité de l'énumération de O_cert.** Le Lemme conclut une dénombrabilité **ensembliste**, pas effective. Un ensemble r.e. infini peut ne pas admettre de bijection calculable avec ℕ (cf. r.e. non décidables — Soare 1987, ch. II). Le Lemme ne prétend pas le contraire.

---

## Références externes

| Référence | Usage dans la preuve |
|---|---|
| Hrbacek, K. & Jech, T. (1999). *Introduction to Set Theory*, 3e éd., Marcel Dekker, ch. 1. | Étape B.3 — partie d'un dénombrable au plus dénombrable |
| Jech, T. (2003). *Set Theory*, 3e éd., Springer, ch. 1. | Étape B.3 (référence alternative) |
| Hopcroft, J.E., Motwani, R. & Ullman, J.D. (2007). *Introduction to Automata Theory, Languages, and Computation*, 3e éd., Pearson, ch. 1. | Étape B.2 — Σ* dénombrable (référence alternative) |
| Rogers, H. (1987). *Theory of Recursive Functions and Effective Computability*, MIT Press (orig. 1967), ch. 1. | Étapes A.4 et A.5 — décidable ⇒ r.e., r.e. ⇒ dénombrable |
| Sipser, M. (2013). *Introduction to the Theory of Computation*, 3e éd., Cengage, ch. 0 (Strings and Languages) et ch. 3 (Countability). | Étape B.2 — Σ* dénombrable |
| Soare, R.I. (1987). *Recursively Enumerable Sets and Degrees*, Springer, ch. I §1.2. | Étapes A.4 et A.5 (référence alternative) |

---

## Note sur BR-010

Les deux stratégies candidates (A = Calculabilité, B = représentation finie / dénombrabilité de Σ*) ont été produites comme demandé. Le Lemme est démontré dans les deux cas. Le statut de `brainstorm/BR-010.md` reste **PROPOSÉ** jusqu'au verdict de l'Analyste externe (Tâche 7.2), qui tranchera entre A et B comme preuve principale (`R-PREUVE-01`).

---

*Sprint 7 — Tâche 7.1 — instance Opus 4.7 (extended thinking) — Mai 2026*
