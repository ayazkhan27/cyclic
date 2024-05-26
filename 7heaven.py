import matplotlib.pyplot as plt

# Function to compute minimal movement for a cyclic prime
def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence):
    # Function logic remains the same as before
    pass

# Function to generate target sequences based on the prime length
def generate_target_sequences(prime, cyclic_sequence):
    # Function logic remains the same as before
    return []  # Assuming it returns an empty list by default

# Function to analyze and plot for cyclic prime 7 with different starting fractions
def analyze_cyclic_prime(start_fraction):
    prime = 7
    cyclic_sequence = '142857'
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

    if not target_sequences:
        print(f"No target sequences generated for cyclic prime {prime}.")
        return

    movements = []

    # Calculate movements for each target sequence
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    start_index = (int(start_fraction.split('/')[0]) - 1) % prime
    start_sequence = cyclic_sequence[start_index:] + cyclic_sequence[:start_index]
    
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
    print("Superposition Movements:", superposition_movements)
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
    ax.set_title(f'Minimal Movements for Cyclic Prime {prime} (Starting Fraction: {start_fraction})')
    ax.set_ylabel('Movement on Dial')
    ax.set_xlabel(f'Fraction n/{prime}')

    plt.show()

# Analyzing cyclic prime 7 with different starting fractions
analyze_cyclic_prime('1/7')
analyze_cyclic_prime('2/7')
analyze_cyclic_prime('3/7')
analyze_cyclic_prime('4/7')
analyze_cyclic_prime('5/7')
analyze_cyclic_prime('6/7')
