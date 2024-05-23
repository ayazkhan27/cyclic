import numpy as np
import sympy
from concurrent.futures import ProcessPoolExecutor, as_completed

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

# Function to analyze a given cyclic sequence for a known prime
def analyze_cyclic_sequence(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    
    # Define positions for single or multi-digit sequences
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

    # Check conditions
    superposition_movements = [m for m in movements if abs(m) == sequence_length // 2]
    non_superposition_movements = [m for m in movements if abs(m) != sequence_length // 2]
    net_movement = sum(non_superposition_movements)
    unique_movements = len(movements) == len(set(movements))
    superposition_condition = len(superposition_movements) == 1

    return net_movement == 0, unique_movements, superposition_condition, movements

# Function to generate a random sequence in chunks
def generate_random_sequence(sequence_length):
    chunk_size = 10  # Chunk size to avoid memory overflow
    sequence = []
    for _ in range(sequence_length // chunk_size):
        sequence.extend(np.random.choice(list('0123456789'), chunk_size))
    sequence.extend(np.random.choice(list('0123456789'), sequence_length % chunk_size))
    return ''.join(sequence)

# Function to find a cyclic sequence that satisfies all conditions for a given prime
def find_cyclic_sequence(prime):
    sequence_length = prime - 1
    while True:
        random_sequence = generate_random_sequence(sequence_length)
        net_movement_zero, unique_movements, superposition_condition, movements = analyze_cyclic_sequence(prime, random_sequence)
        if net_movement_zero and unique_movements and superposition_condition:
            return prime, random_sequence, movements

# Main function
def main():
    start_number = 100  # Starting from the number just greater than the largest known full reptend prime
    with ProcessPoolExecutor() as executor:
        futures = []
        for i in range(start_number, start_number + 100):  # Initial batch
            futures.append(executor.submit(find_cyclic_sequence, i))
        
        while True:
            for future in as_completed(futures):
                result = future.result()
                if result:
                    prime, cyclic_sequence, movements = result
                    print(f"FOUND: Cyclic sequence for prime {prime}: {cyclic_sequence}")
                    print(f"Calculated Movements: {movements}")
                    print(f"Net Movement is Zero: True")
                    print(f"Superposition Movement Found: True")
                    print(f"Cyclic Sequence Length: {len(cyclic_sequence)} digits")
                    return
                
            # Add more tasks to the pool if needed
            futures = []
            start_number += 100
            for i in range(start_number, start_number + 100):
                futures.append(executor.submit(find_cyclic_sequence, i))

if __name__ == "__main__":
    main()
