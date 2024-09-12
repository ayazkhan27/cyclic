import math
import random
import string
from collections import Counter
import importlib.util
import sys
from decimal import Decimal, getcontext

# Import the module dynamically
def import_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Paths to both encryption modules
khan_encryption_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption.py"
cyclic_khan_encryption_path = "/home/zephyr27/Documents/GitHub/cyclic/cyclic_khan_encryption.py"

# Import both modules
ke = import_module("khan_encryption", khan_encryption_path)
cke = import_module("cyclic_khan_encryption", cyclic_khan_encryption_path)

# Helper functions
def calculate_entropy(data):
    """Calculate the Shannon entropy of the data."""
    data_count = Counter(data)
    entropy = 0.0
    length = len(data)
    for count in data_count.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy

def estimate_security_bits(keyspace_size):
    """Estimate security bits based on the keyspace size."""
    return math.log2(keyspace_size)

def estimate_keyspace_size(prime, cyclic_sequence_length, superposition_sequence_length):
    """Estimate the keyspace size of the algorithm."""
    keyspace_size = prime * cyclic_sequence_length * (2 ** superposition_sequence_length)  # Adjusted for binary superposition sequence
    return keyspace_size

def test_algorithm(algorithm_name, encrypt_fn, decrypt_fn, plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length=None):
    """Test the given encryption algorithm and measure its entropy, security bits, and keyspace."""
    try:
        if algorithm_name == "Cyclic KHAN":
            # Debugging: Print input parameters
            print(f"Testing {algorithm_name} with parameters:")
            print(f"plaintext: {plaintext}")
            print(f"prime: {prime}")
            print(f"cyclic_sequence: {cyclic_sequence}")
            print(f"start_position: {start_position}")
            print(f"superposition_sequence_length: {superposition_sequence_length}")

            ciphertext, superposition_sequence, z_value = encrypt_fn(
                plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length
            )
            decrypted_text = decrypt_fn(ciphertext, prime, cyclic_sequence, start_position, superposition_sequence, z_value)
        else:
            # Debugging: Print input parameters
            print(f"Testing {algorithm_name} with parameters:")
            print(f"plaintext: {plaintext}")
            print(f"prime: {prime}")
            print(f"cyclic_sequence: {cyclic_sequence}")
            print(f"start_position: {start_position}")

            ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = encrypt_fn(
                plaintext, prime, cyclic_sequence, start_position
            )
            decrypted_text = decrypt_fn(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence)

        # Test encryption and decryption accuracy
        encryption_success = plaintext == decrypted_text
        print(f"{algorithm_name} Encryption Success: {encryption_success}")

        # Calculate entropy of the ciphertext
        entropy = calculate_entropy(ciphertext)
        print(f"{algorithm_name} Ciphertext Entropy: {entropy:.4f} bits/symbol")

        # Estimate keyspace size and security bits
        keyspace_size = estimate_keyspace_size(prime, len(cyclic_sequence), len(superposition_sequence) if superposition_sequence is not None else 0)
        security_bits = estimate_security_bits(keyspace_size)
        print(f"{algorithm_name} Security Bits: {security_bits:.2f}")

        return encryption_success, entropy, security_bits

    except Exception as e:
        print(f"Error occurred while testing {algorithm_name}: {e}")
        return None, None, None


def main():
    # Sample parameters for testing
    plaintext = ke.generate_plaintext(128)
    
    # Parameters for cyclic_khan_encryption (first algorithm)
    prime_cyclic_khan = 1051  # Example prime for cyclic KHAN encryption
    cyclic_sequence_cyclic_khan = [random.randint(1, prime_cyclic_khan - 1) for _ in range(prime_cyclic_khan - 1)]
    start_position_cyclic_khan = random.randint(1, prime_cyclic_khan - 1)
    superposition_sequence_length_cyclic_khan = 100

    # Parameters for khan_encryption (second algorithm)
    prime_khan_2 = 1051  # Example prime for second KHAN encryption
    cyclic_sequence_khan_2 = [random.randint(1, prime_khan_2 - 1) for _ in range(prime_khan_2 - 1)]
    start_position_khan_2 = random.randint(1, prime_khan_2 - 1)

    # Test cyclic_khan_encryption (first algorithm)
    print("\nTesting Cyclic KHAN Encryption:")
    test_algorithm("Cyclic KHAN", cke.khan_encrypt, cke.khan_decrypt, plaintext, prime_cyclic_khan, cyclic_sequence_cyclic_khan, start_position_cyclic_khan, superposition_sequence_length_cyclic_khan)

    # Test khan_encryption (second algorithm)
    print("\nTesting KHAN Encryption Version 2:")
    test_algorithm("KHAN Encryption Version 2", ke.khan_encrypt, ke.khan_decrypt, plaintext, prime_khan_2, cyclic_sequence_khan_2, start_position_khan_2)

if __name__ == "__main__":
    main()
