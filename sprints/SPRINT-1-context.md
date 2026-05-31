# Session Sprint 1 — Instrumentation des canaux
**Chantier :** epistemic-impossibility-validation
**Durée estimée :** 1.5 jour
**Instance :** Jules (Google) ou Claude Code Web — Opus pour la calibration γ_i uniquement

> **Règle de session :** ce fichier est le seul contexte de cette session.
> Commence par : `git pull` + lecture de `STATUS.md` + lecture de
> `theory/tie_formal.md` (version Sprint 0.5, commité).
> La source de vérité est le repo — pas cette conversation.

> **Principe de cette session :** tu instrumentes les trois canaux comme
> des boîtes noires interchangeables. Tu ne produis pas de résultats,
> tu ne fais pas d'expériences. Ton seul objectif est que les trois canaux
> passent les tests unitaires et produisent des sorties de format identique.

---

## Ce que tu dois savoir sur ce sprint

Le projet compare trois canaux de communication entre agents IA :
- **Canal A (texte)** : encode l'état interne via un décodeur softmax → token → embedding
- **Canal B (latent)** : transmet le vecteur d'état interne directement (connexion résiduelle)
- **Canal C (CLAIM)** : transforme l'état interne en une structure épistémique formelle

Ces trois canaux seront utilisés dans des expériences de comparaison (sprints suivants).
**Ce sprint implémente les canaux. Il ne les compare pas.**

Tu as besoin de connaître :
- Les paramètres techniques dans `VARIABLES.md` (déjà commité)
- Les définitions formelles dans `theory/tie_formal.md` (déjà commité)
- Les contrats API définis ci-dessous

Tu n'as pas besoin de connaître :
- Ce que les expériences vont mesurer
- Les hypothèses statistiques du projet
- Les sprints théoriques (Sprint 7)
- La structure du papier final

---

## Tâche 1.1 — Canal A : texte via softmax (0.5 jour)

**Fichier :** `src/channels.py` — classe `TextChannel`

### Contrat API (R-API-01)

```python
class TextChannel:
    """
    Canal de communication texte.
    Encode un état latent h via softmax → token → re-embedding.
    Pure function : mêmes entrées → mêmes sorties, toujours.
    Pas de state interne entre appels.
    """

    def __init__(self, model_name: str = "gpt2", seed: int = 42):
        """
        model_name : identifiant HuggingFace (défaut : "gpt2")
        seed       : seed global pour reproductibilité
        Postcondition : self.model est en mode eval(), grad désactivé.
        """

    def encode(self, h: torch.Tensor) -> torch.Tensor:
        """
        Entrée  : h de shape (batch, hidden_dim) — état latent normalisé
        Sortie  : h_out de shape (batch, hidden_dim) — état latent re-encodé
        Contrat : encode(h) est deterministe pour h fixé et seed fixé.
        Contrat : aucune modification de h en place.
        """

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        """
        Retourne ‖J_C(h)‖₂ — norme spectrale du jacobien de encode() en h.
        Utilisé pour la mesure expérimentale (sprints suivants).
        Contrat : résultat ≥ 0, sans exception.
        """

    def get_output_entropy(self, h: torch.Tensor) -> float:
        """
        Retourne H(p) = -Σ p_i log p_i sur la distribution softmax en h.
        Contrat : résultat ∈ [0, log(vocab_size)].
        """
```

### Contraintes d'implémentation

- Le modèle GPT-2 small doit être chargé **une seule fois** à l'init, pas à chaque appel.
- `torch.manual_seed(seed)` appelé dans `__init__` avant tout appel HuggingFace.
- `model.eval()` et `torch.no_grad()` forcés — pas de gradient actif sauf dans `get_jacobian_norm`.
- La norme du jacobien est calculée via `torch.autograd.functional.jacobian` sur le forward pass complet (h → softmax → argmax → embedding).
- **Pas de closure sur des données pré-calculées.** Toute variable nécessaire au calcul est passée en argument ou calculée à partir des arguments. (`#16 Pure Function Contract`)

### Test unitaire minimal (obligatoire avant commit)

```python
def test_text_channel_pure():
    """Vérifie que TextChannel est une fonction pure."""
    ch = TextChannel(seed=42)
    h1 = torch.randn(1, 768, generator=torch.Generator().manual_seed(0))
    h2 = torch.randn(1, 768, generator=torch.Generator().manual_seed(1))

    # Même entrée → même sortie
    assert torch.allclose(ch.encode(h1), ch.encode(h1)), \
        "encode() n'est pas déterministe"

    # Entrées différentes → sorties différentes (détecte les closures sur état figé)
    assert not torch.allclose(ch.encode(h1), ch.encode(h2)), \
        "encode() retourne le même résultat pour des entrées différentes — closure suspectée"

    # Jacobien défini et positif
    jac = ch.get_jacobian_norm(h1)
    assert jac >= 0, "jacobien négatif — impossible"

    # Entropie dans [0, log(vocab_size)]
    ent = ch.get_output_entropy(h1)
    assert 0 <= ent <= math.log(50257), "entropie hors borne"
```

---

## Tâche 1.2 — Canal B : latent via connexion résiduelle (0.25 jour)

**Fichier :** `src/channels.py` — classe `LatentChannel`

### Contrat API

```python
class LatentChannel:
    """
    Canal de communication latent.
    Transmet l'état interne via une connexion résiduelle apprise.
    Gradient-preserving par construction (jacobien ≈ I + ε).
    """

    def __init__(self, hidden_dim: int = 768, seed: int = 42):
        """
        hidden_dim : dimension de l'espace latent (défaut : 768 pour GPT-2 small)
        seed       : seed global
        """

    def encode(self, h: torch.Tensor) -> torch.Tensor:
        """
        Entrée  : h de shape (batch, hidden_dim)
        Sortie  : h_out = h + f(h) de shape (batch, hidden_dim)
                  où f est une petite MLP (2 couches, activation GELU)
        Contrat : encode(h) est déterministe pour h fixé et seed fixé.
        Contrat : ‖J_C(h)‖₂ ≥ 0.5 pour tout h (gradient-preserving par construction).
        """

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        """Même contrat que TextChannel.get_jacobian_norm."""

    def get_output_entropy(self, h: torch.Tensor) -> float:
        """
        Pour le canal latent, l'entropie est calculée sur la distribution
        des composantes de h_out après normalisation (soft histogram, 50 bins).
        Contrat : résultat ∈ [0, log(50)].
        """
```

### Test unitaire minimal

```python
def test_latent_channel_gradient_preserving():
    """Vérifie que LatentChannel préserve le gradient par construction."""
    ch = LatentChannel(seed=42)
    h = torch.randn(1, 768, generator=torch.Generator().manual_seed(0))

    jac = ch.get_jacobian_norm(h)
    assert jac >= 0.5, \
        f"Canal latent non gradient-preserving : ‖J‖ = {jac:.4f} < 0.5"

    # Pure function check
    h2 = torch.randn(1, 768, generator=torch.Generator().manual_seed(1))
    assert not torch.allclose(ch.encode(h), ch.encode(h2)), \
        "LatentChannel : closure sur état figé suspectée"
```

---

## Tâche 1.3 — Canal C : CLAIM epistémique (0.5 jour)

**Fichier :** `src/channels.py` — classe `CLAIMChannel`
**Fichier :** `src/calibration.py` — fonction `calibrate_claim_channel`

### Contexte

Le canal C transforme un état latent h en une structure CLAIM formelle.
La structure CLAIM est définie dans `theory/tie_formal.md` (commité).
Elle comporte cinq champs. Pour ce sprint, l'implémentation est simplifiée :
les champs `freshness` et `provenance` sont des stubs fonctionnels.

### Contrat API — CLAIMChannel

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class CLAIM:
    """
    Structure épistémique formelle.
    frozen=True : immuable après création — pas de modification en place.
    """
    proposition: str                               # Θ ∈ {ami, ennemi, neutre, inconnu}
    belief_mass: dict[str, float]                  # m : 2^Θ → [0,1], Σ = 1, m(∅) ≥ 0
    belnap_state: Literal["T", "F", "B", "N"]     # état épistémique
    illocution: Literal["OBSERVE", "INFER",
                        "DEDUCE", "ASSUME"]        # type d'acte illocutoire
    freshness: tuple[float, float]                 # (t_obs, Δt_valid) — stub
    provenance: str                                # chain_id — stub


class CLAIMChannel:
    """
    Canal de communication CLAIM.
    Transforme un état latent h en une structure CLAIM via une tête
    de calibration légère (linear head → softmax sur 2^|Θ|).
    """

    def __init__(self, theta: list[str], seed: int = 42):
        """
        theta : cadre de discernement Θ (liste de labels)
                Défaut : ["ami", "ennemi", "neutre", "inconnu"]
        seed  : seed global
        """

    def encode(self, h: torch.Tensor) -> CLAIM:
        """
        Entrée  : h de shape (1, hidden_dim) — un seul vecteur latent
        Sortie  : une structure CLAIM immuable
        Contrat : encode(h) est déterministe pour h fixé et seed fixé.
        Contrat : CLAIM.belief_mass satisfait Σ_{A ⊆ Θ} m(A) = 1.
        Contrat : CLAIM.belief_mass[frozenset()] = m(∅) explicite (conflit).
        """

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        """
        Le jacobien est calculé sur la tête de calibration (h → masses).
        Contrat : résultat ≥ 0.
        Note : ce canal est attendu non-gradient-preserving.
               Le test ne vérifie pas un seuil minimum — il mesure la valeur.
        """

    def get_output_entropy(self, h: torch.Tensor) -> float:
        """
        Entropie de Shannon sur la distribution de masses belief_mass.
        Contrat : résultat ∈ [0, log(2^|Θ|)].
        """

    def inject_conflict(self, h: torch.Tensor,
                        conflict_level: float) -> CLAIM:
        """
        Variante de encode() pour les expériences avec conflit injecté.
        conflict_level ∈ {0.0, 0.2, 0.5, 0.8} (voir VARIABLES.md)
        Contrat : CLAIM.belief_mass[frozenset()] = conflict_level ± 0.01.
        Contrat : R-CONFLIT-01 — cette méthode est obligatoire pour Canal C.
        """
```

### Calibration γ_i (Tâche Opus — 0.25 jour séparé)

La méthode de calibration est décidée dans BR-002 (commité en Sprint 0).
L'implémentation suit la décision du LLM Council.

**Si BR-002 → k-NN :**
```python
def calibrate_claim_channel(
    channel: CLAIMChannel,
    reference_set: list[tuple[torch.Tensor, str]],
    k: int = 5
) -> CLAIMChannel:
    """
    Calibre la tête de calibration via k-NN dans l'espace latent.
    reference_set : liste de (h, label) avec label ∈ Θ
    k             : nombre de voisins
    Retourne le channel calibré (nouvel objet — pas de mutation).
    """
```

**Si BR-002 → Deep EK-NN :**
```python
def calibrate_claim_channel(
    channel: CLAIMChannel,
    reference_set: list[tuple[torch.Tensor, str]],
    distance_metric: str = "euclidean"
) -> CLAIMChannel:
    """
    Calibre via Deep EK-NN (Hoarau et al. 2025).
    Sépare incertitude épistémique (non-spécificité) et aléatoire (discord).
    Retourne le channel calibré (nouvel objet — pas de mutation).
    """
```

**Vérification de calibration obligatoire (R-REPRO-02) :**
```python
def verify_calibration(channel: CLAIMChannel,
                       test_set: list[tuple[torch.Tensor, str]],
                       seed: int = 42) -> dict:
    """
    Vérifie que le canal calibré est bit-à-bit reproductible.
    Retourne : {"correlation": float, "is_calibrated": bool,
                "seed_check": bool}
    Contrat : seed_check = True si deux runs avec seed=42 donnent
              des CLAIM identiques sur le même h.
    Seuil d'alerte : correlation < 0.5 → logguer QO-S1-01 dans BR-002.
    """
```

### Test unitaire minimal — Canal C

```python
def test_claim_channel_invariants():
    """Vérifie les invariants de la structure CLAIM."""
    theta = ["ami", "ennemi", "neutre", "inconnu"]
    ch = CLAIMChannel(theta=theta, seed=42)
    h = torch.randn(1, 768, generator=torch.Generator().manual_seed(0))

    claim = ch.encode(h)

    # Invariant 1 : masses somment à 1
    total = sum(claim.belief_mass.values())
    assert abs(total - 1.0) < 1e-5, f"Masses ne somment pas à 1 : {total}"

    # Invariant 2 : m(∅) explicite et ≥ 0
    assert frozenset() in claim.belief_mass, "m(∅) absent"
    assert claim.belief_mass[frozenset()] >= 0, "m(∅) négatif"

    # Invariant 3 : belnap_state valide
    assert claim.belnap_state in ("T", "F", "B", "N"), \
        f"belnap_state invalide : {claim.belnap_state}"

    # Invariant 4 : structure immuable
    import dataclasses
    assert dataclasses.is_dataclass(claim) and claim.__dataclass_params__.frozen, \
        "CLAIM n'est pas frozen"

    # Invariant 5 : déterminisme (pure function)
    claim2 = ch.encode(h)
    assert claim == claim2, "CLAIMChannel non déterministe"

def test_claim_conflict_injection():
    """Vérifie que inject_conflict respecte le niveau de conflit."""
    theta = ["ami", "ennemi", "neutre", "inconnu"]
    ch = CLAIMChannel(theta=theta, seed=42)
    h = torch.randn(1, 768, generator=torch.Generator().manual_seed(0))

    for level in [0.0, 0.2, 0.5, 0.8]:
        claim = ch.inject_conflict(h, conflict_level=level)
        m_vide = claim.belief_mass[frozenset()]
        assert abs(m_vide - level) < 0.01, \
            f"Niveau de conflit {level} non respecté : m(∅) = {m_vide:.4f}"
```

---

## Tâche 1.4 — Interface commune et harness de test (0.25 jour)

**Fichier :** `src/channels.py` — protocol `Channel`

Tous les canaux doivent satisfaire une interface commune pour que le
code expérimental (sprints suivants) soit canal-agnostique.

```python
from typing import Protocol, Union

Output = Union[torch.Tensor, CLAIM]

class Channel(Protocol):
    """Interface commune à tous les canaux."""

    def encode(self, h: torch.Tensor) -> Output:
        """Encode un état latent. Déterministe, sans side-effects."""
        ...

    def get_jacobian_norm(self, h: torch.Tensor) -> float:
        """Retourne ‖J_C(h)‖₂. Toujours ≥ 0."""
        ...

    def get_output_entropy(self, h: torch.Tensor) -> float:
        """Retourne H(sortie). Toujours ≥ 0."""
        ...
```

**Harness de test (`tests/test_channels.py`) :**

```python
@pytest.mark.parametrize("channel_cls,kwargs", [
    (TextChannel,   {"seed": 42}),
    (LatentChannel, {"seed": 42}),
    (CLAIMChannel,  {"theta": ["ami","ennemi","neutre","inconnu"], "seed": 42}),
])
def test_channel_interface_compliance(channel_cls, kwargs):
    """Vérifie que chaque canal satisfait le protocol Channel."""
    ch = channel_cls(**kwargs)
    h = torch.randn(1, 768, generator=torch.Generator().manual_seed(0))

    out = ch.encode(h)
    assert out is not None

    jac = ch.get_jacobian_norm(h)
    assert isinstance(jac, float) and jac >= 0

    ent = ch.get_output_entropy(h)
    assert isinstance(ent, float) and ent >= 0
```

---

## Livrables Sprint 1

```
src/channels.py          ← TextChannel + LatentChannel + CLAIMChannel + Channel protocol
src/calibration.py       ← calibrate_claim_channel + verify_calibration
tests/test_channels.py   ← tests unitaires des 4 tâches
reviews/REV-S1.md        ← Rapport Analyste (voir ci-dessous)
```

**Commit final :** tous les tests passent (`pytest tests/test_channels.py -v`).
`STATUS.md` mis à jour : Sprint courant = 2.

---

## Analyste Sprint 1 — questions soumises

Invoquer une **instance Opus séparée** (sans accès à la conversation de travail)
avec uniquement `src/channels.py`, `src/calibration.py`, `tests/test_channels.py`
commités, et ces deux questions :

**Q1 — Pure Function Contract :**
Y a-t-il une closure sur un état figé dans l'une des trois implémentations ?
Une closure produirait `encode(h_A) == encode(h_B)` pour `h_A ≠ h_B`.
Indiquer la ligne et la variable si détectée.

**Q2 — Reproductibilité :**
Le canal C est-il bit-à-bit reproductible entre deux sessions Python distinctes
(nouveau processus, même seed) ? Identifier tout appel non-déterministe
(opérations CUDA, hash Python, etc.) qui briserait `R-REPRO-02`.

---

## Critère de passage Sprint 1

> **`pytest tests/test_channels.py -v` : 0 erreur, 0 failure.**
> **REV-S1 : aucune closure détectée (Q1), reproductibilité confirmée (Q2).**
> **Score GNG-PAPER ≥ 60 sur Solidité expérimentale + Reproductibilité.**

Si la corrélation de calibration est < 0.5 : ouvrir `QO-S1-01` dans BR-002
avec la valeur observée, et continuer — les expériences ne démarrent pas
avant que cette question soit résolue ou documentée comme acceptable.

---

## Paramètres techniques de référence

Tous issus de `VARIABLES.md` (source de vérité) :

| Paramètre | Valeur |
|-----------|--------|
| Modèle base | GPT-2 small (117M, `"gpt2"`) |
| `hidden_dim` | 768 |
| `SEED_GLOBAL` | 42 |
| Cadre Θ | `["ami", "ennemi", "neutre", "inconnu"]` |
| `2^|Θ|` | 16 sous-ensembles |
| Niveaux de conflit | `{0.0, 0.2, 0.5, 0.8}` |
| Niveaux d'entropie | `{0.05, 0.1, 0.2, 0.5, 1.0, 2.0}` |

---

*Fichier de session — ne pas modifier après la session*
*Sprint 1 — v4 — Mai 2026*
