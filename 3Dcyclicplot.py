import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Function to compute minimal movement for a cyclic prime
def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]

    min_movement = sequence_length  # Initialize with a value larger than any possible movement

    for start_pos in start_positions:
        for target_pos in target_positions:
            # Calculate clockwise and anticlockwise movements
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length
            
            # Find the minimal movement
            if clockwise_movement <= anticlockwise_movement:
                movement = clockwise_movement
            else:
                movement = -anticlockwise_movement

            if abs(movement) < abs(min_movement):
                min_movement = movement

    return min_movement

# Function to generate target sequences based on the prime length
def generate_target_sequences(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    group_length = len(str(prime))

    if prime < 10:
        return sorted(set(cyclic_sequence))
    else:
        cyclic_groups = []
        for i in range(sequence_length):
            group = cyclic_sequence[i:i+group_length]
            if len(group) == group_length:
                cyclic_groups.append(group)
            else:  # Wrap-around case
                wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
                cyclic_groups.append(wrap_around_group)
        
        cyclic_groups = sorted(set(cyclic_groups))

        # Ensure we have n-1 elements in the target sequences
        return cyclic_groups[:prime - 1]

# Function to analyze and plot for a given cyclic prime
def analyze_cyclic_prime(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    
    # Define positions for single or multi-digit sequences
    if prime < 10:
        digit_positions = {digit: [idx for idx, d in enumerate(cyclic_sequence) if d == digit] for digit in set(cyclic_sequence)}
    else:
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

    # Calculate movements for each target sequence
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence)
        movements.append(movement)

    # Dynamically find superposition movement
    superposition_movement = (prime - 1) // 2
    superposition_indices = [i for i, m in enumerate(movements) if abs(m) == superposition_movement]

    # Print movements before calculating net overall movement
    print(f"Cyclic Prime {prime}")
    print("Target Sequences:", target_sequences)
    print("Calculated Movements:", movements)

    # Mark and display the superposition movements
    print(f"Superposition Movements Detected at Indices: {superposition_indices}")
    for idx in superposition_indices:
        print(f"Superposition Movement at Index {idx}: {movements[idx]}")

    # Calculate the superposition sequence length
    superposition_sequence_length = len(superposition_indices)
    print(f"Superposition Sequence Length: {superposition_sequence_length}")

    # Calculate net overall movement excluding the superposition movement
    net_movement = sum(m for i, m in enumerate(movements) if i not in superposition_indices)

    print("Net Overall Movement (excluding superposition):", net_movement)

    # 3D Visualization
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot movements in 3D
    z = 0
    x_vals = []
    y_vals = []
    z_vals = []
    colors = []

    for i in range(4):  # Change the range for more steps
        for idx, (n, m) in enumerate(zip(fractions, movements)):
            x_vals.append((i * prime) + n)
            y_vals.append(m)
            z_vals.append(z)
            if idx in superposition_indices:
                colors.append('green' if m > 0 else 'yellow')
            else:
                colors.append('blue')
        
        z += 1
        x_vals.append(i * prime + prime)
        y_vals.append(0)
        z_vals.append(z)
        colors.append('blue')

        # Alternate superposition movement for next level
        for idx in superposition_indices:
            movements[idx] = -movements[idx]

    ax.plot(x_vals, y_vals, z_vals, color='blue')
    for x, y, z, c in zip(x_vals, y_vals, z_vals, colors):
        ax.scatter(x, y, z, color=c)

    # Label x-axis with fractions
    x_ticks = [(i * prime) + n for i in range(4) for n in range(prime)]
    x_labels = [f"{n}/{prime}" if n != 0 else f"{prime}" for i in range(4) for n in range(prime)]

    ax.set_xticks([i * prime + prime//2 for i in range(4)])
    ax.set_xticklabels([f"{i * prime + prime}/{prime}" for i in range(4)])

    ax.set_xlabel('Fraction (n/n)')
    ax.set_ylabel('Movement on Dial')
    ax.set_zlabel('Z Axis')
    ax.set_title(f'3D Minimal Movements for Cyclic Prime {prime}')

    plt.show()

# Example usage
analyze_cyclic_prime(17, '0588235294117647')
