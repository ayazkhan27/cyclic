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
# Updated function to return movements and superposition points
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
    superposition_points = []

    # Calculate movements for each target sequence
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    for i, target_sequence in enumerate(target_sequences):
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence)
        movements.append(movement)

        # Detect superposition points (where minimal movement is half the sequence length)
        if abs(movement) == sequence_length // 2:
            superposition_points.append(i)

    # Return the movements and superposition points
    return movements, superposition_points


def run_tests():
    primes = [7, 17, 19, 23]
    cyclic_sequences = [
        '142857',  # Cyclic sequence for 7
        '0588235294117647',  # Cyclic sequence for 17
        '052631578947368421',  # Cyclic sequence for 19
        '0434782608695652173913'  # Cyclic sequence for 23
    ]
    
    for prime, cyclic_sequence in zip(primes, cyclic_sequences):
        print(f"Running tests for cyclic prime: {prime}")
        analyze_cyclic_prime(prime, cyclic_sequence)

# Run the tests
run_tests()
