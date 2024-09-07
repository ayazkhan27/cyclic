import random
import string
import importlib.util
import sys
import time
from decimal import Decimal, getcontext

# Import the khan_encryption module from a specific path
module_name = "khan_encryption"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def measure_encryption_decryption(plaintext, start_position, superposition_sequence_length):
    global cyclic_prime
    cyclic_prime = 323901749  # Set cyclic prime value

    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Encrypt the plaintext
    start_time = time.time()
    ciphertext, _, _, _, _, _, _, _ = ke.khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, start_position)
    encryption_time = time.time() - start_time

    # Decrypt the ciphertext
    start_time = time.time()
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time

    # Check if decryption is successful
    decryption_successful = plaintext == decrypted_text

    return encryption_time, decryption_time, decryption_successful

def main():
    # Get user input for private keys
    start_position = int(input(f"User 1: Enter the starting dial position (integer between 1 and 323901748): "))
    superposition_sequence_length = int(input("User 2: Enter the superposition sequence length (even integer): "))

    # Generate random plaintext
    plaintext = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))

    # Measure encryption and decryption
    encryption_time, decryption_time, decryption_successful = measure_encryption_decryption(plaintext, start_position, superposition_sequence_length)

    # Display results
    print("\nEncryption and Decryption Results:")
    print(f"Original Plaintext: {plaintext}")
    print(f"Encryption Time: {encryption_time} seconds")
    print(f"Decryption Time: {decryption_time} seconds")
    print("Decryption Successful" if decryption_successful else "Decryption Failed")

if __name__ == "__main__":
    main()
