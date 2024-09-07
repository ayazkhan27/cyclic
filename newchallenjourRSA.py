import random
import string
import time
from Crypto.PublicKey import RSA
from decimal import Decimal, getcontext

# Import the khan_encryption module from a specific path
import importlib.util
import sys

module_name = "khan_encryption"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

# Define the generate_cyclic_sequence function
def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def generate_random_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def measure_khan_encryption_decryption(plaintext, prime, cyclic_sequence, start_position):
    start_time = time.time()
    # Call khan_encrypt from the imported module directly
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(plaintext, prime, cyclic_sequence, start_position)
    encryption_time = time.time() - start_time

    start_time = time.time()
    # Call khan_decrypt from the imported module directly
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time

def generate_rsa_key(key_size):
    if key_size < 1024:
        raise ValueError("RSA modulus length must be >= 1024")
    return RSA.generate(key_size)

def measure_rsa_encryption_decryption(plaintext, rsa_key):
    start_time = time.time()
    ciphertext = rsa_key.encrypt(plaintext.encode(), 0)[0]
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_text = rsa_key.decrypt(ciphertext).decode()
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time

def main():
    # Parameters for KHAN encryption
    prime = 1051  # 8-bit prime number
    cyclic_sequence_length = 10246  # Length of the cyclic sequence
    start_position = 3314  # Starting position for the cyclic sequence

    # Generate random plaintext
    plaintext = generate_random_plaintext(50)

    # Measure encryption and decryption for KHAN encryption
    khan_encryption_time, khan_decryption_time = measure_khan_encryption_decryption(plaintext, prime, generate_cyclic_sequence(prime, cyclic_sequence_length), start_position)

    # Generate RSA key
    rsa_key_size = 2048
    rsa_key = generate_rsa_key(rsa_key_size)

    # Measure encryption and decryption for RSA
    rsa_encryption_time, rsa_decryption_time = measure_rsa_encryption_decryption(plaintext, rsa_key)

    # Display results for KHAN encryption
    print("\nKHAN Encryption:")
    print("Encryption Time:", khan_encryption_time, "seconds")
    print("Decryption Time:", khan_decryption_time, "seconds")

    # Display results for RSA
    print("\nRSA Encryption:")
    print("Encryption Time:", rsa_encryption_time, "seconds")
    print("Decryption Time:", rsa_decryption_time, "seconds")

if __name__ == "__main__":
    main()
