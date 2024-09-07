import random
import numpy as np
from sympy import Matrix, mod_inverse
from collections import Counter, defaultdict
import networkx as nx
from scipy.stats import entropy
import time
import khan_encryption as ke
import DEMOFileMasterpiece as dfm

TIMEOUT_LIMIT = 1800  # 30 minutes total
cyclic_prime = 1051
MIN_MOVEMENT = -(cyclic_prime - 1) // 2
MAX_MOVEMENT = (cyclic_prime - 1) // 2

def generate_attack_data(num_plaintexts=10, length=128):
    cyclic_sequence = dfm.generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)
    start_position = random.randint(1, cyclic_prime - 1)
    plaintexts = [ke.generate_plaintext(length) for _ in range(num_plaintexts)]
    ciphertexts = []
    for pt in plaintexts:
        ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
            pt, cyclic_prime, cyclic_sequence, start_position)
        ciphertexts.append((ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers))
    return plaintexts, ciphertexts, cyclic_sequence, start_position

def algebraic_attack(ciphertexts):
    movements = [ct[0] for ct in ciphertexts]
    group_elements = set()
    for movement_set in movements:
        group_elements.update(movement_set)
    
    # Analyze group structure
    order = len(group_elements)
    generator = max(group_elements, key=lambda x: sum(pow(x, i, cyclic_prime) for i in range(cyclic_prime)) % cyclic_prime)
    
    print(f"Group order: {order}")
    print(f"Potential generator: {generator}")
    
    # Look for fixed points or patterns
    fixed_points = [e for e in group_elements if pow(e, 2, cyclic_prime) == e]
    print(f"Fixed points: {fixed_points}")

def topological_analysis(ciphertexts):
    G = nx.DiGraph()
    for ct, _, _, _, _, _, _, _ in ciphertexts:
        for i in range(len(ct) - 1):
            G.add_edge(ct[i], ct[i+1])
    
    # Analyze graph structure
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    
    # Find cycles
    cycles = list(nx.simple_cycles(G))
    print(f"Number of cycles found: {len(cycles)}")
    if cycles:
        print(f"Example cycle: {cycles[0]}")

def lattice_attack(ciphertexts):
    movements = [ct[0] for ct in ciphertexts]
    lattice_basis = Matrix(movements)
    
    # Perform LLL reduction
    reduced_basis = lattice_basis.lll()
    
    print("Reduced lattice basis:")
    print(reduced_basis)
    
    # Try to reconstruct plaintext using the reduced basis
    for row in reduced_basis.tolist():
        possible_plaintext = ''.join(chr((x % 26) + 65) for x in row)  # Simple ASCII mapping
        print(f"Possible plaintext: {possible_plaintext[:50]}...")  # First 50 characters

def superposition_analysis(ciphertexts):
    superposition_sequences = [ct[4] for ct in ciphertexts]
    
    # Analyze superposition sequence patterns
    seq_counts = Counter(tuple(seq) for seq in superposition_sequences)
    most_common = seq_counts.most_common(1)[0]
    print(f"Most common superposition sequence: {most_common[0]}, count: {most_common[1]}")
    
    # Calculate entropy of superposition sequences
    probs = [count / len(superposition_sequences) for count in seq_counts.values()]
    seq_entropy = entropy(probs)
    print(f"Entropy of superposition sequences: {seq_entropy}")

def z_layer_analysis(ciphertexts):
    z_layers = [ct[7] for ct in ciphertexts]
    
    # Analyze Z-layer patterns
    z_layer_counts = Counter(tuple(layer) for layer in z_layers)
    most_common = z_layer_counts.most_common(1)[0]
    print(f"Most common Z-layer pattern: {most_common[0]}, count: {most_common[1]}")
    
    # Look for correlations between Z-layers and movements
    correlations = defaultdict(list)
    for (ct, _, _, _, _, _, _, layers) in ciphertexts:
        for movement, layer in zip(ct, layers):
            correlations[layer].append(movement)
    
    for layer, movements in correlations.items():
        avg_movement = sum(movements) / len(movements)
        print(f"Average movement for Z-layer {layer}: {avg_movement}")

def probabilistic_attack(ciphertexts):
    movements = [ct[0] for ct in ciphertexts]
    
    # Calculate transition probabilities
    transitions = defaultdict(Counter)
    for movement_set in movements:
        for i in range(len(movement_set) - 1):
            transitions[movement_set[i]][movement_set[i+1]] += 1
    
    # Normalize probabilities
    for state, next_states in transitions.items():
        total = sum(next_states.values())
        for next_state in next_states:
            next_states[next_state] /= total
    
    # Print most likely transitions
    for state, next_states in transitions.items():
        print(f"From state {state}, most likely next state: {next_states.most_common(1)[0]}")

def main():
    start_time = time.time()
    plaintexts, ciphertexts, cyclic_sequence, start_position = generate_attack_data()

    print("Starting comprehensive attack on KHAN encryption...")

    print("\n1. Algebraic Attack:")
    algebraic_attack(ciphertexts)

    if time.time() - start_time > TIMEOUT_LIMIT:
        print("Timeout reached. Stopping attack.")
        return

    print("\n2. Topological Analysis:")
    topological_analysis(ciphertexts)

    if time.time() - start_time > TIMEOUT_LIMIT:
        print("Timeout reached. Stopping attack.")
        return

    print("\n3. Lattice Attack:")
    lattice_attack(ciphertexts)

    if time.time() - start_time > TIMEOUT_LIMIT:
        print("Timeout reached. Stopping attack.")
        return

    print("\n4. Superposition Analysis:")
    superposition_analysis(ciphertexts)

    if time.time() - start_time > TIMEOUT_LIMIT:
        print("Timeout reached. Stopping attack.")
        return

    print("\n5. Z-Layer Analysis:")
    z_layer_analysis(ciphertexts)

    if time.time() - start_time > TIMEOUT_LIMIT:
        print("Timeout reached. Stopping attack.")
        return

    print("\n6. Probabilistic Attack:")
    probabilistic_attack(ciphertexts)

    print("\nAttack completed. Unable to fully break the encryption.")

if __name__ == "__main__":
    main()