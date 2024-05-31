import random
import string
import importlib.util
import sys
from decimal import Decimal, getcontext
import numpy as np
from scipy.stats import entropy as kl_divergence
from collections import Counter

# Import the khan_encryption2 module from a specific path
module_name = "khan_encryption2.0"
file_path = "C:/Users/admin/Documents/GitHub/cyclic/khan_encryption_2.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def get_user_input():
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

def calculate_z_value(superposition_sequence_length):
    # Calculate z_value based on the superposition sequence length
    z_value = superposition_sequence_length - 1
    return z_value

def calculate_entropy(ciphertext):
    total_chars = len(ciphertext)
    frequency_dict = {char: ciphertext.count(char) for char in set(ciphertext)}
    entropy = Decimal(0)
    for char, frequency in frequency_dict.items():
        probability = Decimal(frequency) / total_chars
        entropy -= probability * probability.ln() / Decimal(2).ln()  # Convert to base 2
    return entropy

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

    return ciphertext, decrypted_text

def calculate_security_bits(prime, plaintext_length, start_position_range, superposition_length_range):
    total_possible_states_log2 = np.log2(prime) + np.log2(superposition_length_range // 2)
    total_permutations_log2 = total_possible_states_log2 * plaintext_length
    security_bits = total_permutations_log2 - plaintext_length
    return security_bits

def main():
    global cyclic_prime
    cyclic_prime = 1051  # Set the cyclic prime to 1051

    # Get user input for private keys
    start_position, superposition_sequence_length = get_user_input()

    # Generate random plaintext
    plaintext = ke.generate_plaintext(128)

    # Measure encryption and decryption
    ciphertext, decrypted_text = measure_khan_encryption(plaintext, start_position, superposition_sequence_length)

    # Calculate entropy
    entropy_value = calculate_entropy(ciphertext)

    # Calculate security bits
    security_bits = calculate_security_bits(cyclic_prime, len(plaintext), cyclic_prime - 1, 100)

    # Display results
    print("\nEncryption and Decryption Results:")
    print("Original Plaintext:", plaintext)
    print("Decrypted Plaintext:", decrypted_text)
    print("Entropy of Ciphertext:", entropy_value)
    print("Estimated Security Bits:", security_bits)
    print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")

if __name__ == "__main__":
    main()
