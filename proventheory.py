import random
from decimal import Decimal, getcontext
import matplotlib.pyplot as plt
import sympy

# Function to compute minimal movement for a cyclic prime
def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
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

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def verify_khan_theorems(prime):
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    start_sequence = cyclic_sequence[:len(str(prime))]

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

    target_sequences = generate_target_sequences(prime, cyclic_sequence)
    movements = []

    # Calculate movements for each target sequence
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)
        movements.append(movement)

    # Verify properties
    unique_movements = set(movements)
    non_superposition_movements = [m for m in movements if abs(m) != sequence_length // 2]
    net_movement = sum(non_superposition_movements)
    superposition_movement = sequence_length // 2

    return {
        'prime': prime,
        'unique_movements': len(unique_movements) == len(movements),
        'net_movement_zero': net_movement == 0,
        'superposition_movement': superposition_movement in movements
    }

def get_first_n_full_reptend_primes(n):
    full_reptend_primes = []
    candidate = 7  # Start from the smallest known full reptend prime
    while len(full_reptend_primes) < n:
        if sympy.isprime(candidate) and sympy.is_primitive_root(10, candidate):
            full_reptend_primes.append(candidate)
        candidate += 2  # Increment by 2 to check the next odd number
    return full_reptend_primes

def main():
    full_reptend_primes = get_first_n_full_reptend_primes(1000)

    results = []
    success_count = 0
    for prime in full_reptend_primes:
        result = verify_khan_theorems(prime)
        results.append(result)
        if all(result.values()):
            success_count += 1

    success_percentage = (success_count / len(full_reptend_primes)) * 100
    print(f"Success Percentage: {success_percentage:.2f}%")

    failure_count = len(full_reptend_primes) - success_count

    # Generate bar plots
    labels = ['Successes', 'Failures']
    counts = [success_count, failure_count]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color=['green', 'red'])
    plt.xlabel('Outcome')
    plt.ylabel('Count')
    plt.title('Success vs Failure Counts for Full Reptend Primes')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
