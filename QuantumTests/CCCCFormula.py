import math
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# 1. Data Generation Functions
# -----------------------------

# List of known full reptend primes (from OEIS A001913)
full_reptend_primes = [
    7, 17, 19, 23, 29, 47, 59, 61, 97, 109, 113,
    131, 149, 167, 179, 181, 193, 223, 229, 233,
    257, 263, 269, 313, 337, 367, 379, 383, 389,
    419, 433, 461, 487, 491, 499, 503, 509, 541,
    571, 577, 593, 619, 647, 659, 701, 709, 727,
    743, 811, 821, 823, 857, 863, 887, 937, 941,
    953, 971, 977, 983
]

def get_reptend_sequence(p):
    """
    Generate the repeating decimal sequence of 1/p for a full reptend prime p.

    Parameters:
    - p (int): Full reptend prime.

    Returns:
    - str: Repeating decimal sequence of 1/p.
    """
    remainders = []
    digits = []
    remainder = 1
    while True:
        remainder *= 10
        digit = remainder // p
        remainder = remainder % p
        if remainder == 0 or remainder in remainders:
            break
        remainders.append(remainder)
        digits.append(str(digit))
    return ''.join(digits)

def minimal_movement(cyclic_sequence, start_sequence, target_sequence):
    """
    Calculate the minimal movement needed to transition between two sequences.

    Parameters:
    - cyclic_sequence (str): The full repeating decimal sequence.
    - start_sequence (str): The starting sequence.
    - target_sequence (str): The target sequence to reach.

    Returns:
    - int: Minimal movement (positive for clockwise, negative for anticlockwise).
    """
    sequence_length = len(cyclic_sequence)
    start_positions = [i for i in range(sequence_length) if cyclic_sequence.startswith(start_sequence, i)]
    target_positions = [i for i in range(sequence_length) if cyclic_sequence.startswith(target_sequence, i)]
    min_movement = sequence_length  # Initialize with a large value

    for start_pos in start_positions:
        for target_pos in target_positions:
            # Calculate clockwise and anticlockwise movements
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length

            if clockwise_movement < anticlockwise_movement:
                movement = clockwise_movement
            elif anticlockwise_movement < clockwise_movement:
                movement = -anticlockwise_movement
            else:
                # Movements are equal; choose direction randomly
                movement = clockwise_movement if np.random.rand() < 0.5 else -anticlockwise_movement

            if abs(movement) < abs(min_movement):
                min_movement = movement

    return min_movement

def generate_minimal_movements(p):
    """
    Generate minimal movements for a given full reptend prime.

    Parameters:
    - p (int): Full reptend prime.

    Returns:
    - list of int: Minimal movements.
    - int: Superposition movement value.
    - float: Proportion of superposition movements.
    """
    cyclic_sequence = get_reptend_sequence(p)
    sequence_length = len(cyclic_sequence)
    group_length = len(str(p))

    # Generate target sequences
    cyclic_groups = []
    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) < group_length:
            group += cyclic_sequence[:group_length - len(group)]
        cyclic_groups.append(group)
    # Remove duplicates and ensure we have p - 1 groups
    target_sequences = sorted(set(cyclic_groups))[:p - 1]

    minimal_movements = []
    superposition_movement = sequence_length // 2
    superposition_count = 0

    start_sequence = cyclic_sequence[:group_length]

    for target_sequence in target_sequences:
        movement = minimal_movement(cyclic_sequence, start_sequence, target_sequence)
        minimal_movements.append(movement)
        if abs(movement) == superposition_movement:
            superposition_count += 1

    total_movements = len(minimal_movements)
    superposition_proportion = superposition_count / total_movements if total_movements > 0 else 0

    return minimal_movements, superposition_movement, superposition_proportion

# -----------------------------
# 2. Simulate Quantum Angular Momentum States
# -----------------------------

def simulate_quantum_angular_momentum(num_samples, max_magnitude):
    """
    Simulate quantum angular momentum states using actual probability distributions.

    Parameters:
    - num_samples (int): Number of samples to generate.
    - max_magnitude (float): Maximum angular momentum magnitude to simulate.

    Returns:
    - np.ndarray: Array of simulated angular momentum movements.
    """
    # Quantum numbers from l = 0 to l_max
    l_max = int(max_magnitude)
    quantum_numbers = np.arange(0, l_max + 1)

    # Calculate angular momentum magnitudes L = sqrt(l(l+1))
    L_values = np.sqrt(quantum_numbers * (quantum_numbers + 1))

    # Use normalized probability distribution for l
    # Degeneracy d = 2l + 1
    degeneracy = 2 * quantum_numbers + 1
    probabilities = degeneracy / np.sum(degeneracy)

    # Sample angular momentum magnitudes
    samples = np.random.choice(L_values, size=num_samples, p=probabilities)
    # Assign random signs to simulate directionality
    signs = np.random.choice([-1, 1], size=num_samples)
    movements = samples * signs
    return movements

# -----------------------------
# 3. Applying the CMCQS Formula
# -----------------------------

def apply_cmcqs(prime, minimal_movements):
    """
    Apply the Cyclic Movement Conservation in Quantum Systems (CMCQS) formula.

    Parameters:
    - prime (int): Full reptend prime.
    - minimal_movements (list of int): Minimal movements.

    Returns:
    - float: Real part of cyclic sum.
    - float: Imaginary part of cyclic sum.
    - float: Magnitude of cyclic sum.
    """
    N = prime - 1  # Number of movements
    theta_i = [2 * np.pi * i / N for i in range(1, N + 1)]  # Equally spaced phases
    M_i = minimal_movements  # Minimal movements

    # Calculate the cyclic sum
    cyclic_sum = sum([m * np.exp(1j * theta) for m, theta in zip(M_i, theta_i)])

    # Extract real and imaginary parts
    cyclic_sum_real = np.real(cyclic_sum)
    cyclic_sum_imag = np.imag(cyclic_sum)
    magnitude = np.abs(cyclic_sum)

    return cyclic_sum_real, cyclic_sum_imag, magnitude

# -----------------------------
# 4. Visualization Function
# -----------------------------

def plot_cyclic_sum(cyclic_sum_real, cyclic_sum_imag, prime, label):
    """
    Plot the cyclic sum in the complex plane.

    Parameters:
    - cyclic_sum_real (float): Real part of cyclic sum.
    - cyclic_sum_imag (float): Imaginary part of cyclic sum.
    - prime (int): Prime number.
    - label (str): Label for the plot.
    """
    plt.figure(figsize=(6, 6))
    plt.plot(cyclic_sum_real, cyclic_sum_imag, 'o', label=f'Prime {prime} Sum ({label})')
    plt.axhline(0, color='gray', linestyle='--')
    plt.axvline(0, color='gray', linestyle='--')
    plt.xlabel('Real Part')
    plt.ylabel('Imaginary Part')
    plt.title(f'Cyclic Sum for Prime {prime} ({label})')
    plt.legend()
    plt.grid(True)
    plt.show()

# -----------------------------
# 5. Main Analysis Function
# -----------------------------

def main():
    print("Applying the Cyclic Movement Conservation in Quantum Systems (CMCQS) Formula:\n")
    for p in full_reptend_primes:
        minimal_movements, superposition_movement, superposition_proportion = generate_minimal_movements(p)
        if len(minimal_movements) == 0:
            continue  # Skip if no movements

        # Apply CMCQS formula to minimal movements
        cyclic_sum_real, cyclic_sum_imag, magnitude = apply_cmcqs(p, minimal_movements)

        print(f"Prime: {p}")
        print(f"  Cyclic Sum Real Part: {cyclic_sum_real:.4f}")
        print(f"  Cyclic Sum Imaginary Part: {cyclic_sum_imag:.4f}")
        print(f"  Magnitude of Cyclic Sum: {magnitude:.4f}")

        # Plot the cyclic sum for minimal movements
        plot_cyclic_sum(cyclic_sum_real, cyclic_sum_imag, p, "Minimal Movements")

        # Assess the sum
        threshold = 1e-2  # Define a small threshold
        if magnitude < threshold:
            print("  CMCQS Formula holds: The cyclic sum is approximately zero.\n")
        else:
            print("  CMCQS Formula does not hold: The cyclic sum is significantly different from zero.\n")

        # Simulate and apply CMCQS to quantum angular momentum data
        num_samples = p - 1
        quantum_movements = simulate_quantum_angular_momentum(num_samples, superposition_movement)
        quantum_cyclic_sum_real, quantum_cyclic_sum_imag, quantum_magnitude = apply_cmcqs(p, quantum_movements)

        print(f"  Quantum Simulation:")
        print(f"    Cyclic Sum Real Part: {quantum_cyclic_sum_real:.4f}")
        print(f"    Cyclic Sum Imaginary Part: {quantum_cyclic_sum_imag:.4f}")
        print(f"    Magnitude of Cyclic Sum: {quantum_magnitude:.4f}")

        # Plot the cyclic sum for quantum simulation
        plot_cyclic_sum(quantum_cyclic_sum_real, quantum_cyclic_sum_imag, p, "Quantum Simulation")

        if quantum_magnitude < threshold:
            print("    CMCQS Formula holds for Quantum Simulation: The cyclic sum is approximately zero.\n")
        else:
            print("    CMCQS Formula does not hold for Quantum Simulation: The cyclic sum is significantly different from zero.\n")

if __name__ == "__main__":
    main()
