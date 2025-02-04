import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from scipy.optimize import curve_fit

from cyclicprimerelations import minimal_movement, generate_target_sequences

# Given list of full reptend primes (FRPs)
frps = [7, 17, 19, 23, 29, 47, 59, 61, 97, 109, 113, 131, 149, 167,
        179, 181, 193, 223, 229, 233, 257, 263, 269, 313, 337, 367,
        379, 383, 389, 419, 433, 461, 487, 491, 499, 503, 509, 541,
        571, 577, 593, 619, 647, 659, 701, 709, 727, 743, 811, 821,
        823, 857, 863, 887, 937, 941, 953, 971, 977, 983]

def compute_markov_chain(prime, cyclic_sequence):
    """Computes transition matrix from minimal movement states."""
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    group_length = len(str(prime))

    # Identify positions of digit groups
    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) == group_length:
            digit_positions.setdefault(group, []).append(i)
        else:  # Wrap-around case
            wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
            digit_positions.setdefault(wrap_around_group, []).append(i)

    # Compute minimal movements
    target_sequences = generate_target_sequences(prime, cyclic_sequence)
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    movements = [minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence)
                 for target_sequence in target_sequences]

    # Identify unique movement states
    unique_states = sorted(set(movements))
    state_index = {state: idx for idx, state in enumerate(unique_states)}
    num_states = len(unique_states)

    # Initialize transition matrix
    transition_matrix = np.zeros((num_states, num_states))

    # Fill transition matrix by counting state transitions
    for i in range(len(movements) - 1):
        current_state = movements[i]
        next_state = movements[i + 1]
        transition_matrix[state_index[current_state], state_index[next_state]] += 1

    # Normalize rows to convert counts into probabilities
    row_sums = transition_matrix.sum(axis=1, keepdims=True)

    # **Fix Zero Rows**: Replace zero rows with a uniform probability distribution
    zero_rows = (row_sums == 0).flatten()
    transition_matrix[zero_rows] = 1 / num_states  # Assign equal probability to all states

    # Normalize again to ensure valid probabilities
    transition_matrix /= transition_matrix.sum(axis=1, keepdims=True)

    return transition_matrix, unique_states

def analyze_markov_chain(prime, cyclic_sequence):
    """Analyzes Markov chain properties and entropy rate."""
    transition_matrix, unique_states = compute_markov_chain(prime, cyclic_sequence)
    
    # Compute the stationary distribution
    eigvals, eigvecs = np.linalg.eig(transition_matrix.T)
    stationary_distribution = np.real(eigvecs[:, np.isclose(eigvals, 1)].flatten())
    stationary_distribution /= stationary_distribution.sum()

    # Compute entropy rate of Markov process
    entropy_rate = -np.sum(stationary_distribution * np.nansum(transition_matrix * np.log2(transition_matrix + 1e-10), axis=1))

    # Print results
    print(f"\nMarkov Analysis for Cyclic Prime {prime}")
    print("Stationary Distribution:", dict(zip(unique_states, stationary_distribution)))
    print("Entropy Rate:", entropy_rate)

    # Visualize transition matrix as a heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(transition_matrix, annot=True, xticklabels=unique_states, yticklabels=unique_states, cmap="coolwarm", fmt=".2f")
    plt.title(f"Markov Transition Matrix for Prime {prime}")
    plt.xlabel("Next State")
    plt.ylabel("Current State")
    plt.show()

    # Visualize the transition network
    G = nx.DiGraph()
    for i, state_from in enumerate(unique_states):
        for j, state_to in enumerate(unique_states):
            weight = transition_matrix[i, j]
            if weight > 0:
                G.add_edge(state_from, state_to, weight=weight)

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=12)
    edge_labels = {(state_from, state_to): f"{weight:.2f}" for state_from, state_to, weight in G.edges(data='weight')}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    plt.title(f"State Transition Diagram for Cyclic Prime {prime}")
    plt.show()

    return entropy_rate

# Compute entropy rates for all FRPs
entropy_rates = []
for prime in frps:
    cyclic_sequence = str(1 / prime)[2:2 + (prime - 1)]  # Approximate cyclic decimal sequence
    entropy_rate = analyze_markov_chain(prime, cyclic_sequence)
    entropy_rates.append(entropy_rate)

# Fit a trend curve (logarithmic) to see general behavior
def log_fit(x, a, b):
    return a * np.log(x) + b

params, _ = curve_fit(log_fit, frps, entropy_rates)

# Plot entropy rate vs. prime size
plt.figure(figsize=(12, 6))
plt.scatter(frps, entropy_rates, label='Computed Entropy Rates', color='blue')
plt.plot(frps, log_fit(np.array(frps), *params), linestyle='dashed', color='red', label='Logarithmic Fit')

plt.xlabel("Full Reptend Prime (p)")
plt.ylabel("Entropy Rate")
plt.title("Entropy Rate vs. Prime Size for Full Reptend Primes")
plt.legend()
plt.grid(True)
plt.show()
