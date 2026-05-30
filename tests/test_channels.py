import torch
import numpy as np
import math
from src.channels import TextChannel, LatentChannel, CLAIMChannel, CLAIM
from src.calibration import calibrate_claim_channel, verify_calibration


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


def test_channel_interface_compliance():
    """Vérifie que chaque canal satisfait le protocol Channel."""
    # Test all three channel types
    channel_configs = [
        (TextChannel, {"seed": 42}),
        (LatentChannel, {"seed": 42}),
        (CLAIMChannel, {"theta": ["ami", "ennemi", "neutre", "inconnu"], "seed": 42}),
    ]
    
    for channel_cls, kwargs in channel_configs:
        ch = channel_cls(**kwargs)
        h = torch.randn(1, 768, generator=torch.Generator().manual_seed(0))

        out = ch.encode(h)
        assert out is not None

        jac = ch.get_jacobian_norm(h)
        assert isinstance(jac, float) and jac >= 0

        ent = ch.get_output_entropy(h)
        assert isinstance(ent, float) and ent >= 0


def test_calibration_functions():
    """Test the calibration functions."""
    # Create a simple reference set for testing
    theta = ["ami", "ennemi", "neutre", "inconnu"]
    channel = CLAIMChannel(theta=theta, seed=42)
    
    # Create reference set: (h, label) pairs
    reference_set = []
    for i, label in enumerate(theta):
        # Create a simple vector for each label
        h = torch.zeros(1, 768)
        h[0, i * 192] = 1.0  # Simple one-hot like encoding
        reference_set.append((h, label))
    
    # Test calibration
    calibrated_channel = calibrate_claim_channel(channel, reference_set, k=2)
    
    # Test that calibrated channel still works
    h_test = torch.randn(1, 768, generator=torch.Generator().manual_seed(42))
    claim = calibrated_channel.encode(h_test)
    assert isinstance(claim, CLAIM)
    
    # Test verification
    test_set = [(torch.randn(1, 768, generator=torch.Generator().manual_seed(i)), theta[i % len(theta)]) 
                for i in range(5)]
    result = verify_calibration(calibrated_channel, test_set, seed=42)
    
    assert "correlation" in result
    assert "is_calibrated" in result
    assert "seed_check" in result
    assert isinstance(result["correlation"], float)
    assert isinstance(result["is_calibrated"], bool)
    assert isinstance(result["seed_check"], bool)


if __name__ == "__main__":
    # Run tests manually if called directly
    test_text_channel_pure()
    print("✓ TextChannel pure function test passed")
    
    test_latent_channel_gradient_preserving()
    print("✓ LatentChannel gradient preserving test passed")
    
    test_claim_channel_invariants()
    print("✓ CLAIMChannel invariants test passed")
    
    test_claim_conflict_injection()
    print("✓ CLAIMChannel conflict injection test passed")
    
    test_channel_interface_compliance()
    print("✓ Channel interface compliance test passed")
    
    test_calibration_functions()
    print("✓ Calibration functions test passed")
    
    print("\n🎉 All tests passed!")