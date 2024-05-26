import sympy
from decimal import Decimal, getcontext

def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]

    min_movement = sequence_length  # Initialize with a value larger than any possible movement

    for start_pos in start_positions:
        for target_pos in target_positions:
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length
            
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
            else:
                wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
                cyclic_groups.append(wrap_around_group)
        
        cyclic_groups = sorted(set(cyclic_groups))
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
            else:
                wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
                if wrap_around_group in digit_positions:
                    digit_positions[wrap_around_group].append(i)
                else:
                    digit_positions[wrap_around_group] = [i]

    target_sequences = generate_target_sequences(prime, cyclic_sequence)
    movements = []

    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)
        movements.append(movement)

    unique_movements = set(movements)
    non_superposition_movements = [m for m in movements if abs(m) != sequence_length // 2]
    net_movement = sum(non_superposition_movements)
    superposition_movement = sequence_length // 2

    total_unique_movements = len(unique_movements) - 2  # Exclude 0 and superposition movement

    return {
        'prime': prime,
        'cyclic_sequence': cyclic_sequence,
        'unique_movements': len(unique_movements) == len(movements),
        'net_movement_zero': net_movement == 0,
        'superposition_movement': superposition_movement in movements,
        'unique_movements_count': total_unique_movements == (prime - 3),
        'is_full_reptend_prime': len(unique_movements) == len(movements) and net_movement == 0 and superposition_movement in movements and total_unique_movements == (prime - 3)
    }

# General function to test all primes up to a given limit
def test_full_reptend_primes(limit):
    primes = list(sympy.primerange(2, limit))
    full_reptend_primes = []

    for prime in primes:
        result = verify_khan_theorems(prime)
        if result['is_full_reptend_prime']:
            full_reptend_primes.append(result)

    return full_reptend_primes

def find_possible_cyclic_sequences(prime):
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    possible_sequences = []
    for i in range(len(cyclic_sequence)):
        possible_sequence = cyclic_sequence[i:] + cyclic_sequence[:i]
        possible_sequences.append(possible_sequence)
    return possible_sequences

def analyze_diagonal_symmetry(cyclic_sequence):
    length = len(cyclic_sequence)
    diagonal_counts = {str(i): 0 for i in range(10)}  # Initialize counts for digits 0-9
    
    for i in range(length):
        digit = cyclic_sequence[i]
        diagonal_counts[digit] += 1
    
    return diagonal_counts

def main():
    limit = 50  # Define the limit up to which primes are tested
    full_reptend_primes = test_full_reptend_primes(limit)

    for result in full_reptend_primes:
        prime = result['prime']
        cyclic_sequence = result['cyclic_sequence']
        possible_sequences = find_possible_cyclic_sequences(prime)
        print(f"Prime: {prime}, Cyclic Sequence: {cyclic_sequence}")
        print("Possible Cyclic Sequences:")
        for sequence in possible_sequences:
            print(sequence)
        
        # Analyze diagonal symmetry
        diagonal_counts = analyze_diagonal_symmetry(cyclic_sequence)
        print("Diagonal Symmetry Analysis:")
        print(diagonal_counts)
        print()

if __name__ == "__main__":
    main()
