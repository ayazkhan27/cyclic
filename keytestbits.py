import random
import string
import importlib.util
import sys
from decimal import Decimal, getcontext
import time
import math
from sympy import isprime

# Import the khan_encryption module from a specific path
module_name = "khan_encryption"
file_path = "C:/Users/admin/Downloads/khan_encryption.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def get_user_input(cyclic_prime):
    # User 1 input for starting dial position
    start_position = int(input(f"User 1: Enter the starting dial position (integer between 1 and {cyclic_prime - 1}): "))

    # User 2 input for superposition sequence (must be an even integer)
    while True:
        superposition_sequence_length = int(input("User 2: Enter the superposition sequence length (even integer): "))
        if superposition_sequence_length % 2 == 0:
            break
        else:
            print("Superposition sequence length must be an even integer. Please try again.")

    return start_position, superposition_sequence_length

def calculate_entropy(ciphertext):
    total_chars = len(ciphertext)
    frequency_dict = {char: ciphertext.count(char) for char in set(ciphertext)}
    entropy = Decimal(0)
    for char, frequency in frequency_dict.items():
        probability = Decimal(frequency) / total_chars
        entropy -= probability * probability.log10()
    return entropy

def measure_khan_encryption(plaintext, start_position, superposition_sequence_length, cyclic_prime):
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Generate superposition sequence
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    while sum(superposition_sequence) != 0:
        superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]

    # Calculate z_value
    z_value = superposition_sequence_length - 1

    # Encrypt the plaintext
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, start_position)
    encryption_time = time.time() - start_time

    # Decrypt the ciphertext
    start_time = time.time()
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time

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

    target_sequences = ke.generate_target_sequences(prime, cyclic_sequence)  # Call from khan_encryption module
    movements = []

    for target_sequence in target_sequences:
        movement = ke.minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)  # Call from khan_encryption module
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

def get_full_reptend_prime(bit_size):
    # Start the search from the smallest full reptend prime greater than the bit_size
    start_prime = 2 ** bit_size + 1

    # Loop until a full reptend prime is found
    while True:
        if isprime(start_prime) and (start_prime - 1) % bit_size == 0 and verify_khan_theorems(start_prime)['is_full_reptend_prime']:
            return start_prime
        # Increment to the next potential full reptend prime
        start_prime += bit_size

def main():
    # List of key sizes to test
    key_sizes = [2, 8, 16]  # Add more key sizes as needed

    for key_size in key_sizes:
        cyclic_prime = get_full_reptend_prime(key_size)

        if verify_khan_theorems(cyclic_prime)['is_full_reptend_prime']:
            # Get user input for private keys
            start_position, superposition_sequence_length = get_user_input(cyclic_prime)

            # Generate random plaintext
            plaintext = ke.generate_plaintext(128)

            # Measure encryption and decryption
            encryption_time, decryption_time = measure_khan_encryption(plaintext, start_position, superposition_sequence_length, cyclic_prime)

            # Calculate the number of possible keys
            num_possible_keys = 2 ** key_size

            # Calculate the security level in bits
            security_level_bits = math.log2(num_possible_keys)

            # Display results
            print("\nKey Size:", key_size, "bits")
            print("Security Level (in bits):", security_level_bits)
            print("Cyclic Prime:", cyclic_prime)
            print("Encryption Time:", encryption_time, "seconds")
            print("Decryption Time:", decryption_time, "seconds")
        else:
            print("\nSkipping key size", key_size, "because the generated prime is not a full reptend prime.")

if __name__ == "__main__":
    main()
