import os
import time
import random
import string
import importlib.util
import sys
from decimal import Decimal, getcontext

# Set the encryption file path directly in the script for IDLE
# Uncomment the next line and update the path to your file if running in IDLE
os.environ['ENCRYPTION_FILE_PATH'] = 'C:/Users/admin/Documents/GitHub/cyclic/khan_encryption_2.py'

# Get the encryption file path from the environment variable
file_path = os.getenv('ENCRYPTION_FILE_PATH')
if not file_path:
    raise EnvironmentError("ENCRYPTION_FILE_PATH environment variable is not set.")
else:
    print(f"ENCRYPTION_FILE_PATH is set to: {file_path}")

# Load the khan_encryption_2 module from the specified file path
module_name = "khan_encryption_2"
spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def get_user_input():
    start_position = int(input(f"User 1: Enter the starting dial position (integer between 1 and {cyclic_prime - 1}): "))
    while True:
        superposition_sequence_length = int(input("User 2: Enter the superposition sequence length (even integer): "))
        if superposition_sequence_length % 2 == 0:
            break
        else:
            print("Superposition sequence length must be an even integer. Please try again.")
    return start_position, superposition_sequence_length

def calculate_z_value(superposition_sequence_length):
    z_value = superposition_sequence_length - 1
    return z_value

def measure_khan_encryption(plaintext, start_position, superposition_sequence_length):
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    while sum(superposition_sequence) != 0:
        superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    z_value = calculate_z_value(superposition_sequence_length)
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
        plaintext, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)
    encryption_time = time.time() - start_time
    start_time = time.time()
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time
    return encryption_time, decryption_time, decrypted_text

def main():
    global cyclic_prime
    cyclic_prime = 1051  # Set the cyclic prime to 1051
    start_position, superposition_sequence_length = get_user_input()
    plaintext = ke.generate_plaintext(128)
    encryption_time, decryption_time, decrypted_text = measure_khan_encryption(plaintext, start_position, superposition_sequence_length)
    print("\nEncryption and Decryption Results:")
    print("Original Plaintext:", plaintext)
    print("Decrypted Plaintext:", decrypted_text)
    print(f"Encryption Time: {encryption_time} seconds")
    print(f"Decryption Time: {decryption_time} seconds")
    print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
