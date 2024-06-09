import matplotlib.pyplot as plt
import numpy as np

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

    # Print movements and net overall movement before plotting
    superposition_movements = [m for m in movements if abs(m) == sequence_length // 2]
    non_superposition_movements = [m for m in movements if abs(m) != sequence_length // 2]
    net_movement = sum(non_superposition_movements)

    print(f"Cyclic Prime {prime}")
    print("Target Sequences:", target_sequences)
    print("Calculated Movements:", movements)
    print("Superposition Movement Magnitude:", superposition_movements)
    print("Net Overall Movement:", net_movement)

    # Visualization
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot movements
    for idx, (n, m) in enumerate(zip(fractions, movements)):
        fraction_label = f"{n}/{prime}"
        if abs(m) == sequence_length // 2:
            ax.plot([idx, idx], [0, -m], 'purple', linestyle='dotted')
            ax.plot([idx, idx], [0, m], 'purple', linestyle='dotted')
        else:
            color = 'blue' if m > 0 else 'red' if m < 0 else 'green'
            ax.plot([idx, idx], [0, m], marker='o', color=color)

    # Setting x-axis with fractions
    ax.set_xticks(range(len(fractions)))
    ax.set_xticklabels([f'{n}/{prime}' for n in fractions])

    # Setting y-axis with movements
    ax.set_yticks(range(-sequence_length, sequence_length + 1))
    ax.set_yticklabels(range(-sequence_length, sequence_length + 1))

    # Adding second y-axis for cyclic sequence
    secax = ax.secondary_yaxis('right')
    # Calculate tick positions for cyclic sequence
    sequence_ticks = list(range(-sequence_length, sequence_length + 1))
    cyclic_labels = list(cyclic_sequence) * ((len(sequence_ticks) // sequence_length) + 1)
    cyclic_labels = cyclic_labels[:len(sequence_ticks)]
    secax.set_yticks(sequence_ticks)
    secax.set_yticklabels(cyclic_labels)

    # Adjust secondary y-axis position to prevent overlap
    secax.spines['right'].set_position(('outward', 40))

    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.grid(color='gray', linestyle='--', linewidth=0.5)
    ax.set_title(f'Minimal Movements for Cyclic Prime {prime}')
    ax.set_ylabel('Movement on Dial')
    ax.set_xlabel(f'Fraction n/{prime}')

    plt.show()

# Analyzing cyclic primes
analyze_cyclic_prime(7, '142857')
analyze_cyclic_prime(17, '0588235294117647')
analyze_cyclic_prime(19, '052631578947368421')
analyze_cyclic_prime(23, '0434782608695652173913')
