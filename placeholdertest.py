import random
import string
import importlib.util
import sys
from decimal import Decimal, getcontext
import time

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

def calculate_entropy(ciphertext):
    total_chars = len(ciphertext)
    frequency_dict = {char: ciphertext.count(char) for char in set(ciphertext)}
    entropy = Decimal(0)
    for char, frequency in frequency_dict.items():
        probability = Decimal(frequency) / total_chars
        entropy -= probability * probability.log10()
    return entropy

def measure_khan_encryption(plaintext, start_position, superposition_sequence_length):
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

    return encryption_time, decryption_time, decrypted_text

def display_encryption_decryption_results(plaintext, decrypted_text, encryption_time, decryption_time):
    print("\nEncryption and Decryption Results:")
    print("Original Plaintext:", plaintext)
    print("Decrypted Plaintext:", decrypted_text)
    print(f"Encryption Time: {encryption_time} seconds")
    print(f"Decryption Time: {decryption_time} seconds")
    print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")

def display_analysis_results(avalanche_ratio, propagation_ratio, entropy):
    print("Avalanche Ratio:", avalanche_ratio)
    print("Propagation Ratio:", propagation_ratio)
    print("Entropy:", entropy)

def main():
    global cyclic_prime
    cyclic_prime = 1051
    
    # Get user input for private keys
    start_position, superposition_sequence_length = get_user_input()

    # Generate random plaintext
    plaintext = ke.generate_plaintext(128)

    # Measure encryption and decryption
    encryption_time, decryption_time, decrypted_text = measure_khan_encryption(plaintext, start_position, superposition_sequence_length)

    # Display encryption and decryption results
    display_encryption_decryption_results(plaintext, decrypted_text, encryption_time, decryption_time)

    # Measure avalanche ratio, propagation ratio, and entropy
    avalanche_ratio = 0.5  # Placeholder value
    propagation_ratio = 0.5  # Placeholder value
    entropy = 0.5  # Placeholder value

    # Display analysis results
    display_analysis_results(avalanche_ratio, propagation_ratio, entropy)

if __name__ == "__main__":
    main()
