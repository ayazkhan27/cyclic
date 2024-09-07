import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from cyclicprimerelations import generate_target_sequences, minimal_movement  # Import necessary functions

def generate_cyclic_shifts(sequence):
    """ Generate all cyclic shifts of a given sequence. """
    shifts = [sequence[i:] + sequence[:i] for i in range(len(sequence))]
    return shifts

def create_graph_for_shifts(prime, cyclic_sequence):
    """ Create and visualize a graph representing cyclic shifts of a sequence. """
    shifts = generate_cyclic_shifts(cyclic_sequence)
    G = nx.DiGraph()

    # Add nodes and edges to the graph
    for i, shift in enumerate(shifts):
        G.add_node(i, label=shift)
        next_index = (i + 1) % len(shifts)
        G.add_edge(i, next_index, label=f'Shift {i} -> {next_index}')

    # Draw the graph
    pos = nx.circular_layout(G)
    labels = nx.get_edge_attributes(G, 'label')
    node_labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_weight='bold', arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='red')
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12)

    plt.title(f'Graph of Cyclic Shifts for Sequence: {cyclic_sequence}')
    plt.show()

def analyze_cyclic_prime(prime, cyclic_sequence):
    """ Analyze cyclic prime and visualize its shifts. """
    # Generate and visualize cyclic shifts
    create_graph_for_shifts(prime, cyclic_sequence)

    # Optional: Additional analysis with minimal movement
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    
    group_length = len(str(prime))
    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) == group_length:
            if group in digit_positions:
                digit_positions[group].append(i)
            else:
                digit_positions[group] = [i]
        else:  # Wrap-around case
            wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
            if wrap_around_group in digit_positions:
                digit_positions[wrap_around_group].append(i)
            else:
                digit_positions[wrap_around_group] = [i]

    fractions = list(range(1, prime))
    target_sequences = generate_target_sequences(prime, cyclic_sequence)
    movements = []

    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence)
        movements.append(movement)

    # Print the movements
    print(f"Cyclic Prime {prime}")
    print("Target Sequences:", target_sequences)
    print("Calculated Movements:", movements)

# Example usage with cyclic primes
analyze_cyclic_prime(7, '142857')
analyze_cyclic_prime(17, '0588235294117647')
analyze_cyclic_prime(19, '052631578947368421')
analyze_cyclic_prime(23, '0434782608695652173913')
