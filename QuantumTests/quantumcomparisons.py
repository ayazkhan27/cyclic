import math
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp, norm

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

# Function to get the repeating decimal sequence of 1/p
def get_reptend_sequence(p):
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

# Function to compute minimal movement using your previous method
def minimal_movement(cyclic_sequence, start_sequence, target_sequence):
    sequence_length = len(cyclic_sequence)
    start_positions = [i for i in range(sequence_length) if cyclic_sequence.startswith(start_sequence, i)]
    target_positions = [i for i in range(sequence_length) if cyclic_sequence.startswith(target_sequence, i)]
    min_movement = sequence_length  # Initialize with a large value

    for start_pos in start_positions:
        for target_pos in target_positions:
            # Calculate clockwise and anticlockwise movements
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length

            if clockwise_movement <= anticlockwise_movement:
                movement = clockwise_movement
            else:
                movement = -anticlockwise_movement

            if abs(movement) < abs(min_movement):
                min_movement = movement

    return min_movement

# Function to generate minimal movements for a given full reptend prime
def generate_minimal_movements(p):
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
    superposition_proportion = superposition_count / total_movements

    return minimal_movements, superposition_movement, superposition_proportion

# Simulate quantum mechanics observations dataset using Gaussian distribution
def simulate_quantum_data(num_samples, max_magnitude):
    # Use a Gaussian distribution centered at zero
    sigma = max_magnitude / 3  # Standard deviation
    movements = np.random.normal(loc=0, scale=sigma, size=num_samples)
    # Clip movements to the range [-max_magnitude, max_magnitude]
    movements = np.clip(movements, -max_magnitude, max_magnitude)
    return movements

# Compare datasets and perform statistical analysis
def compare_datasets(full_reptend_data, quantum_data):
    # Collect movement magnitudes for full reptend primes
    reptend_movements = []
    for data in full_reptend_data:
        reptend_movements.extend(data['minimal_movements'])

    reptend_magnitudes = [abs(m) for m in reptend_movements]
    quantum_magnitudes = [abs(m) for m in quantum_data]

    # Plot histograms
    plt.figure(figsize=(12, 6))
    bins = np.linspace(0, max(reptend_magnitudes + list(quantum_magnitudes)), 50)
    plt.hist(reptend_magnitudes, bins=bins, alpha=0.5, label='Full Reptend Primes')
    plt.hist(quantum_magnitudes, bins=bins, alpha=0.5, label='Quantum Data')
    plt.xlabel('Movement Magnitude')
    plt.ylabel('Frequency')
    plt.title('Comparison of Movement Magnitudes')
    plt.legend()
    plt.show()

    # Perform KS test
    statistic, p_value = ks_2samp(reptend_magnitudes, quantum_magnitudes)
    print(f"Kolmogorov-Smirnov test statistic: {statistic}")
    print(f"p-value: {p_value}")

    return statistic, p_value

# Main function to execute the analysis
def main():
    full_reptend_data = []
    for p in full_reptend_primes:
        # Skip primes where the sequence length is less than 2 (to avoid division by zero)
        if p <= 3:
            continue
        minimal_movements, superposition_movement, superposition_proportion = generate_minimal_movements(p)
        full_reptend_data.append({
            'prime': p,
            'minimal_movements': minimal_movements,
            'superposition_movement': superposition_movement,
            'superposition_proportion': superposition_proportion
        })

    # Get the maximum superposition movement to define the range for quantum data simulation
    max_superposition_movement = max(data['superposition_movement'] for data in full_reptend_data)

    # Total number of movements to simulate
    num_samples = sum(len(data['minimal_movements']) for data in full_reptend_data)

    # Simulate quantum data using Gaussian distribution
    quantum_movements = simulate_quantum_data(num_samples, max_superposition_movement)

    # Compare datasets
    statistic, p_value = compare_datasets(full_reptend_data, quantum_movements)

    # Print out the proportions of superposition movements for each prime
    print("\nFull Reptend Primes Data:")
    for data in full_reptend_data:
        print(f"Prime: {data['prime']}, Superposition Movement: ±{data['superposition_movement']}, "
              f"Superposition Proportion: {data['superposition_proportion'] * 100:.2f}%")

if __name__ == "__main__":
    main()
