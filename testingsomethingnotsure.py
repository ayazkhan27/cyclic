print("Refer to https://oeis.org/A086018 , these number of full reptend primes less than 10^n for n=1, 2, 3, 4 ... were calculated without using Artin's conjecture constant.")

import sympy
from decimal import Decimal, getcontext

def generate_cyclic_sequence(base, prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(base) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

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

def verify_generalized_theorems(base, prime):
    cyclic_sequence = generate_cyclic_sequence(base, prime, prime - 1)
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

    # New theorem: Total unique movements excluding 0 and superposition movement
    total_unique_movements = len(unique_movements) - 2  # Exclude 0 and superposition movement

    return {
        'prime': prime,
        'unique_movements': len(unique_movements) == len(movements),
        'net_movement_zero': net_movement == 0,
        'superposition_movement': superposition_movement in movements,
        'unique_movements_count': total_unique_movements == (prime - 3)
    }

def get_primes(limit):
    primes = []
    candidate = 2  # Start from the smallest prime
    while candidate < limit:
        if sympy.isprime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes

def main():
    base = 10  # For base 10, which is relevant to full reptend primes
    max_n = 4  # Set the maximum n value as per the OEIS A086018 sequence
    results = []

    for n in range(1, max_n + 1):
        limit = 10 ** n
        primes = get_primes(limit)
        full_reptend_count = 0
        
        for prime in primes:
            result = verify_generalized_theorems(base, prime)
            if all(result.values()):
                full_reptend_count += 1
        
        results.append(full_reptend_count)
        print(f"A086018 for 10^{n}: {full_reptend_count}")

if __name__ == "__main__":
    main()

input("Press Enter to exit...")
