import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

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

    # Dynamically set the superposition movement
    superposition_movement = (prime - 1) // 2
    superposition_index = len(movements) - 1
    movements[superposition_index] = superposition_movement  # Start with positive superposition movement

    # Print movements before calculating net overall movement
    print(f"Cyclic Prime {prime}")
    print("Target Sequences:", target_sequences)
    print("Calculated Movements:", movements)

    # Calculate net overall movement excluding the superposition movement
    net_movement = sum(movements[:-1])

    print("Superposition Movements:", [superposition_movement, -superposition_movement])
    print("Net Overall Movement (excluding superposition):", net_movement)

    return movements, fractions, superposition_movement

# Function to update the plot for animation
def update(frame, ax, x_vals, y_vals, z_vals, colors, prime, movements, superposition_movement, fractions):
    ax.cla()
    z = frame // (len(fractions) * prime)
    for idx in range(frame % (len(fractions) * prime) + 1):
        i = idx // prime
        current_prime_fraction = idx % prime
        n = fractions[current_prime_fraction - 1]
        m = movements[current_prime_fraction - 1]
        x_vals.append((i * prime) + n)
        y_vals.append(m)
        z_vals.append(z)
        if m == superposition_movement:
            colors.append('green' if superposition_movement > 0 else 'yellow')
        elif m == -superposition_movement:
            colors.append('yellow' if superposition_movement > 0 else 'green')
        else:
            colors.append('blue')
        if current_prime_fraction == prime - 1:
            z += 1
    
    ax.plot(x_vals, y_vals, z_vals, color='blue')
    for x, y, z, c in zip(x_vals, y_vals, z_vals, colors):
        ax.scatter(x, y, z, color=c)

    # Label x-axis with fractions
    ax.set_xticks([(i * prime) + prime//2 for i in range(z+1)])
    ax.set_xticklabels([f"{i * prime + prime}/{prime}" for i in range(z+1)])

    ax.set_xlabel('Fraction (n/n)')
    ax.set_ylabel('Movement on Dial')
    ax.set_zlabel('Z Axis')
    ax.set_title(f'3D Minimal Movements for Cyclic Prime {prime}')

# Function to create the animation
def create_animation(prime, cyclic_sequence):
    movements, fractions, superposition_movement = analyze_cyclic_prime(prime, cyclic_sequence)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Initial values for the plot
    x_vals = []
    y_vals = []
    z_vals = []
    colors = []

    ani = FuncAnimation(fig, update, frames=range(100), fargs=(ax, x_vals, y_vals, z_vals, colors, prime, movements, superposition_movement, fractions), repeat=True)
    plt.show()

# Example usage
create_animation(17, '0588235294117647')
