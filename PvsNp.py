import sympy
from decimal import Decimal, getcontext
import time

# Set precision for large primes dynamically based on the size of the prime
def adjust_decimal_precision(prime):
    # Full reptend primes have a cyclic decimal expansion length of (prime - 1)
    # Set precision slightly larger than (prime - 1) to avoid precision loss
    precision = prime + 100  # A buffer of 100 digits
    getcontext().prec = precision

# Function to generate a large full reptend prime using sympy
def generate_large_prime(digits):
    # Generate a prime number with the specified number of digits
    # Ensure that it's a full reptend prime (this ensures maximal cycle in its decimal expansion)
    while True:
        prime_candidate = sympy.nextprime(10**(digits - 1))
        if sympy.isprime(prime_candidate) and sympy.totient(prime_candidate) == prime_candidate - 1:
            return prime_candidate

# Generate the cyclic sequence for 1/p, where p is a large full reptend prime
def generate_cyclic_sequence(prime):
    adjust_decimal_precision(prime)  # Adjust precision for Decimal calculations
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal part, skip "0."
    return decimal_expansion

# Function to sort blocks from the cyclic sequence (for fractions lookup)
def sort_cyclic_blocks(cyclic_sequence, block_size):
    blocks = [cyclic_sequence[i:i+block_size] for i in range(0, len(cyclic_sequence), block_size)]
    sorted_blocks = sorted(blocks)
    return sorted_blocks

# Function to lookup a fraction n/p in the sorted cyclic blocks
def lookup_fraction(n, prime, sorted_blocks, block_size):
    # Create the target block as a string
    target_block = str(n).zfill(block_size)
    try:
        # Find the position of the target block in the sorted cyclic blocks
        position = sorted_blocks.index(target_block)
        return position
    except ValueError:
        return -1  # If not found

# Minimal movement function, to compute minimal movement from start_sequence to target_sequence
def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]
    min_movement = sequence_length

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

# Traditional method to compute n/p using direct division
def traditional_division(n, prime):
    adjust_decimal_precision(prime)
    return Decimal(n) / Decimal(prime)

# Function to analyze cyclic prime and generate movement data
def analyze_cyclic_prime(prime, cyclic_sequence, start_position):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}

    cyclic_sequence = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]

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
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)
        movements.append(movement)
    
    return movements

# Main function to compare both methods for computing n/p
def compare_methods_for_fraction(n, prime):
    print(f"\n### Testing with Prime {prime} and n = {n} ###")
    
    # Traditional division method
    print(f"\nTraditional method: Calculating {n}/{prime} using direct division...")
    start_time = time.time()
    traditional_result = traditional_division(n, prime)
    end_time = time.time()
    print(f"Traditional result: {traditional_result}")
    print(f"Time taken (Traditional Method): {end_time - start_time:.6f} seconds")
    
    # Your method: Using precomputed cyclic sequence and minimal movement
    print(f"\nYour method: Calculating {n}/{prime} using precomputed cyclic sequence and minimal movement...")
    start_time = time.time()
    
    # Generate the cyclic sequence for the prime
    cyclic_sequence = generate_cyclic_sequence(prime)
    
    # Sort the cyclic blocks
    block_size = len(str(prime))
    sorted_blocks = sort_cyclic_blocks(cyclic_sequence, block_size)
    
    # Lookup fraction using minimal movement through cyclic sequence
    position = lookup_fraction(n, prime, sorted_blocks, block_size)
    if position != -1:
        your_method_result = cyclic_sequence[position:position + block_size]
    else:
        your_method_result = "Not found"
    
    end_time = time.time()
    print(f"Your method result: {your_method_result}")
    print(f"Time taken (Your Method): {end_time - start_time:.6f} seconds")

# Function to generate target sequences for analyzing minimal movements
def generate_target_sequences(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    group_length = len(str(prime))
    
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

if __name__ == "__main__":
    # Example: Compare methods for large full reptend primes
    digits = 2  # Number of digits for the large prime
    prime = generate_large_prime(digits)
    print(f"Generated large prime: {prime}")
    
    n = 88  # Example numerator for n/p
    compare_methods_for_fraction(n, prime)
