import time
import random
import string
import importlib.util
import sys
from decimal import Decimal, getcontext

# Import the khan_encryption_2 module from a specific path
module_name = "khan_encryption_2"
file_path = "C:/Users/admin/Documents/GitHub/cyclic/khan_encryption_2.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def calculate_z_value(superposition_sequence_length):
    # Calculate z_value based on the superposition sequence length
    z_value = superposition_sequence_length - 1
    return z_value

def measure_khan_encryption(plaintext, start_position, superposition_sequence_length):
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Generate superposition sequence
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    while sum(superposition_sequence) != 0:
        superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]

    # Calculate z_value
    z_value = calculate_z_value(superposition_sequence_length)

    # Encrypt the plaintext
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
        plaintext, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)

    # Decrypt the ciphertext
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)

    return decrypted_text

def initialize_dictionaries(prime):
    all_chars = string.ascii_letters + string.digits + string.punctuation + ' '
    char_to_movement = {char: i for i, char in enumerate(all_chars)}
    movement_to_char = {i: char for i, char in enumerate(all_chars)}

    # Ensure all movements within the range are covered
    max_movement = (prime - 1) // 2
    for movement in range(-max_movement, max_movement + 1):
        if movement not in movement_to_char:
            # Assign a character for this movement
            char = chr((movement + 256) % 256)  # Use modulo to cycle through ASCII characters
            char_to_movement[char] = movement
            movement_to_char[movement] = char

    return char_to_movement, movement_to_char

def test_vectors():
    # Initialize log file
    with open('test_log.txt', 'w') as log_file:
        for start_position in range(1, cyclic_prime):
            for superposition_sequence_length in range(2, 102, 2):
                # Generate random plaintext
                plaintext = ke.generate_plaintext(16)

                try:
                    # Measure encryption and decryption
                    decrypted_text = measure_khan_encryption(plaintext, start_position, superposition_sequence_length)

                    # Validate the encryption and decryption
                    if plaintext == decrypted_text:
                        log_file.write(f"Passed for start_position {start_position} and length {superposition_sequence_length}\n")
                    else:
                        log_file.write(f"Failed for start_position {start_position} and length {superposition_sequence_length}: Decrypted text does not match\n")
                except ValueError as e:
                    log_file.write(f"Error for start_position {start_position} and length {superposition_sequence_length}: {e}\n")

    print("All tests completed. Check test_log.txt for results.")

def main():
    global cyclic_prime
    cyclic_prime = 1051  # Set the cyclic prime to 1051

    test_vectors()

if __name__ == "__main__":
    main()
