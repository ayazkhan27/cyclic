import random
import string
import importlib.util
import sys
from decimal import Decimal, getcontext
import time

# Import the khan_encryption module from the specific path
module_name = "khan_encryption"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption_2.py"

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

def measure_khan_encryption(plaintext, start_position, superposition_sequence_length):
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Generate superposition sequence
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    while sum(superposition_sequence) != 0:
        superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]

    # Calculate z_value
    z_value = calculate_z_value(superposition_sequence_length)

    # Encrypt the plaintext
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
        plaintext, cyclic_prime, cyclic_sequence, start_position)
    encryption_time = time.time() - start_time

    # Decrypt the ciphertext
    start_time = time.time()
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, decrypted_text, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers

def reduced_grovers_attack(ciphertext, keyspace, cyclic_prime, start_position, cyclic_sequence):
    # Simulating Grover's algorithm by reducing the search space
    reduced_keyspace = keyspace[:int(len(keyspace) ** 0.5)]  # Quadratic speedup

    for possible_key in reduced_keyspace:
        decrypted_text = ke.khan_decrypt(ciphertext, possible_key['char_to_movement'], possible_key['movement_to_char'], 
                                      possible_key['z_value'], possible_key['superposition_sequence'], 
                                      possible_key['iv'], possible_key['salt'], possible_key['z_layers'], 
                                      cyclic_prime, start_position, cyclic_sequence)
        if is_valid_plaintext(decrypted_text):
            return decrypted_text, possible_key

    return None, None

def is_valid_plaintext(plaintext):
    # Example check for valid plaintext, adjust according to the context
    return all(char in string.printable for char in plaintext)

def main():
    global cyclic_prime
    cyclic_prime = 1051  # Set the cyclic prime to 1051

    # Get user input for private keys
    start_position, superposition_sequence_length = get_user_input()

    # Generate random plaintext
    plaintext = ke.generate_plaintext(128)

    # Measure encryption and decryption
    encryption_time, decryption_time, decrypted_text, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = measure_khan_encryption(plaintext, start_position, superposition_sequence_length)

    # Display encryption and decryption results
    print("\nEncryption and Decryption Results:")
    print("Original Plaintext:", plaintext)
    print("Decrypted Plaintext:", decrypted_text)
    print(f"Encryption Time: {encryption_time} seconds")
    print(f"Decryption Time: {decryption_time} seconds")
    print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")

    # Generate a hypothetical keyspace for simulation
    keyspace = []
    for _ in range(100):  # Reduced keyspace for simulation
        possible_key = {
            'char_to_movement': char_to_movement,
            'movement_to_char': movement_to_char,
            'z_value': z_value,
            'superposition_sequence': superposition_sequence,
            'iv': iv,
            'salt': salt,
            'z_layers': z_layers
        }
        keyspace.append(possible_key)

    # Simulate Grover's attack
    decrypted_text, found_key = reduced_grovers_attack(ciphertext, keyspace, cyclic_prime, start_position, cyclic_sequence)
    
    if decrypted_text:
        print(f"Decryption Successful: {decrypted_text}")
    else:
        print("Grover's attack simulation failed to decrypt the message.")

    # Wait for user input before exiting
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
