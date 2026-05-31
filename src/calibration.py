import torch
import numpy as np
from typing import List, Tuple, Union
from .channels import CLAIMChannel
import math


def calibrate_claim_channel(
    channel: CLAIMChannel,
    reference_set: List[Tuple[torch.Tensor, str]],
    k: int = 5
) -> CLAIMChannel:
    """
    Calibre la tête de calibration via k-NN dans l'espace latent.
    reference_set : liste de (h, label) avec label ∈ Θ
    k             : nombre de voisins
    Retourne le channel calibré (nouvel objet — pas de mutation).
    """
    # Create a deep copy of the channel
    import copy
    calibrated_channel = copy.deepcopy(channel)
    
    # Extract reference vectors and labels
    reference_vectors = [item[0] for item in reference_set]
    reference_labels = [item[1] for item in reference_set]
    
    # Store the reference set in the channel for use during encoding
    calibrated_channel.reference_vectors = reference_vectors
    calibrated_channel.reference_labels = reference_labels
    calibrated_channel.k = k
    
    # Override the encode method to use k-NN calibration
    original_encode = calibrated_channel.encode
    
    def calibrated_encode(self, h: torch.Tensor) -> type(original_encode.__globals__['CLAIM']):
        # Ensure we're working with the right shape
        if h.dim() != 2 or h.size(0) != 1:
            raise ValueError(f"CLAIMChannel expects input of shape (1, hidden_dim), got {h.shape}")
        
        # Ensure linear layer is initialized
        calibrated_channel._ensure_linear_layer(h.size(-1))
        
        # Get raw masses from the linear layer
        with torch.no_grad():
            logits = calibrated_channel.linear(h)  # (1, powerset_size)
            raw_masses = torch.softmax(logits, dim=-1)  # (1, powerset_size)
            raw_masses = raw_masses.squeeze(0)  # (powerset_size,)
        
        # If we don't have a reference set, return raw masses
        if not hasattr(calibrated_channel, 'reference_vectors') or not calibrated_channel.reference_vectors:
            # Convert raw masses to belief mass dictionary
            belief_mass = {}
            for i, mass_val in enumerate(raw_masses):
                fs = calibrated_channel._index_to_frozenset[i]
                belief_mass[fs] = mass_val.item()
            
            # Determine proposition, belnap state, etc. as in original encode
            proposition = calibrated_channel._determine_proposition(belief_mass)
            belnap_state = calibrated_channel._determine_belnap_state(belief_mass)
            illocution = "OBSERVE"
            freshness = (0.0, 1.0)
            provenance = "chain_0"
            
            from .channels import CLAIM
            return CLAIM(
                proposition=proposition,
                belief_mass=belief_mass,
                belnap_state=belnap_state,
                illocution=illocution,
                freshness=freshness,
                provenance=provenance
            )
        
        # Compute distances from input to all reference vectors
        h_flat = h.squeeze(0)  # (hidden_dim,)
        distances = []
        for ref_vec in calibrated_channel.reference_vectors:
            ref_flat = ref_vec.squeeze(0) if ref_vec.dim() == 2 else ref_vec
            dist = torch.norm(h_flat - ref_flat, p=2).item()
            distances.append(dist)
        
        # Get k nearest neighbors
        k_nearest_indices = np.argsort(distances)[:calibrated_channel.k]
        k_nearest_labels = [calibrated_channel.reference_labels[i] for i in k_nearest_indices]
        k_nearest_distances = [distances[i] for i in k_nearest_indices]
        
        # Convert distances to weights (closer = higher weight)
        # Add small epsilon to avoid division by zero
        k_nearest_distances = np.array(k_nearest_distances)
        weights = 1.0 / (k_nearest_distances + 1e-8)
        weights = weights / np.sum(weights)  # Normalize
        
        # Create a voting distribution over the powerset
        # For each neighbor, we get their label and convert it to a frozenset
        # Then we accumulate weighted votes for each possible subset
        powerset_size = calibrated_channel.powerset_size
        voted_masses = np.zeros(powerset_size)
        
        # Map from label to frozenset (singleton sets for now)
        label_to_frozenset = {}
        for label in calibrated_channel.theta:
            label_to_frozenset[label] = frozenset([label])
        
        # For each neighbor, add weighted vote to its corresponding singleton set
        for i, (label, weight) in enumerate(zip(k_nearest_labels, weights)):
            if label in label_to_frozenset:
                fs = label_to_frozenset[label]
                idx = calibrated_channel._frozenset_to_index[fs]
                voted_masses[idx] += weight
        
        # Convert to tensor and normalize to ensure it's a valid probability distribution
        voted_masses = torch.tensor(voted_masses, dtype=torch.float32)
        voted_masses = voted_masses / torch.sum(voted_masses)
        
        # Convert to belief mass dictionary
        belief_mass = {}
        for i, mass_val in enumerate(voted_masses):
            fs = calibrated_channel._index_to_frozenset[i]
            belief_mass[fs] = mass_val.item()
        
        # Determine proposition, belnap state, etc. as in original encode
        proposition = calibrated_channel._determine_proposition(belief_mass)
        belnap_state = calibrated_channel._determine_belnap_state(belief_mass)
        illocution = "OBSERVE"
        freshness = (0.0, 1.0)
        provenance = "chain_0"
        
        from .channels import CLAIM
        return CLAIM(
            proposition=proposition,
            belief_mass=belief_mass,
            belnap_state=belnap_state,
            illocution=illocution,
            freshness=freshness,
            provenance=provenance
        )
    
    # Replace the encode method
    calibrated_channel.encode = calibrated_encode.__get__(calibrated_channel, type(calibrated_channel))
    
    return calibrated_channel


def verify_calibration(channel: CLAIMChannel,
                      test_set: List[Tuple[torch.Tensor, str]],
                      seed: int = 42) -> dict:
    """
    Vérifie que le canal calibré est bit-à-bit reproductible.
    Retourne : {"correlation": float, "is_calibrated": bool,
                "seed_check": bool}
    Contrat : seed_check = True si deux runs avec seed=42 donnent
              des CLAIM identiques sur le même h.
    Seuil d'alerte : correlation < 0.5 → logguer QO-S1-01 dans BR-002.
    """
    # Set seeds for reproducibility
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    if not test_set:
        return {"correlation": 0.0, "is_calibrated": False, "seed_check": False}
    
    # Test 1: Check if two runs with same seed produce identical results
    first_results = []
    second_results = []
    
    # First run
    torch.manual_seed(seed)
    np.random.seed(seed)
    for h, label in test_set:
        claim = channel.encode(h)
        # Extract a numeric representation for comparison
        # We'll use the belief mass values as a vector
        masses = [claim.belief_mass[fs] for fs in sorted(claim.belief_mass.keys(), key=lambda x: str(x))]
        first_results.append(masses)
    
    # Second run with same seed
    torch.manual_seed(seed)
    np.random.seed(seed)
    for h, label in test_set:
        claim = channel.encode(h)
        masses = [claim.belief_mass[fs] for fs in sorted(claim.belief_mass.keys(), key=lambda x: str(x))]
        second_results.append(masses)
    
    # Check if results are identical (bit-to-bit reproducibility)
    identical = True
    if len(first_results) != len(second_results):
        identical = False
    else:
        for i in range(len(first_results)):
            if len(first_results[i]) != len(second_results[i]):
                identical = False
                break
            for j in range(len(first_results[i])):
                if abs(first_results[i][j] - second_results[i][j]) > 1e-10:
                    identical = False
                    break
            if not identical:
                break
    
    seed_check = identical
    
    # Test 2: Compute correlation between predicted and true labels
    # For simplicity, we'll compute how often the predicted singleton matches the true label
    correct_predictions = 0
    total_predictions = 0
    
    for h, true_label in test_set:
        claim = channel.encode(h)
        
        # Find the singleton with highest mass
        max_singleton_mass = 0.0
        predicted_label = None
        
        for fs, mass in claim.belief_mass.items():
            if len(fs) == 1:  # Singleton
                label = next(iter(fs))
                if mass > max_singleton_mass:
                    max_singleton_mass = mass
                    predicted_label = label
        
        if predicted_label == true_label:
            correct_predictions += 1
        total_predictions += 1
    
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
    
    # For correlation, we'll use accuracy as a simple measure
    # In a more sophisticated implementation, we might compute actual correlation
    correlation = accuracy
    
    # Determine if calibrated (using accuracy > 0.5 as threshold for simplicity)
    is_calibrated = correlation >= 0.5
    
    return {
        "correlation": correlation,
        "is_calibrated": is_calibrated,
        "seed_check": seed_check
    }