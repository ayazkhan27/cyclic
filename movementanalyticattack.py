import random
import string
import time
import importlib.util
import sys
from itertools import permutations
from decimal import Decimal, getcontext
from khan_encryption import khan_encrypt, khan_decrypt, generate_plaintext, analyze_cyclic_prime, generate_target_sequences, minimal_movement, generate_keys, calculate_z_value

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def known_plaintext_attack(plaintext, ciphertext, prime, cyclic_sequence, start_position, z_value, superposition_sequence, iv, salt, z_layers):
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    decrypted_text = khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence)
    return decrypted_text == plaintext

def analyze_movements(ciphertext, prime, cyclic_sequence, start_position):
    movements = analyze_cyclic_prime(prime, cyclic_sequence, start_position)
    return movements

def generate_possible_movements(ciphertext, movements):
    # Generate a set of possible movements based on analysis
    possible_movements = set()
    for movement in movements:
        possible_movements.add(movement)
    return possible_movements

def brute_force_attack(ciphertext, possible_movements, movement_to_char, timeout=60):
    start_time = time.time()
    for perm in permutations(possible_movements, len(ciphertext)):
        # Check if the timeout has been reached
        if time.time() - start_time > timeout:
            print("Timeout reached. Stopping brute force attack.")
            return None
        plaintext = []
        try:
            for i, c in enumerate(ciphertext):
                if c == perm[i]:
                    plaintext.append(movement_to_char[perm[i]])
                else:
                    raise ValueError
            return ''.join(plaintext)
        except ValueError:
            continue
    return None

def main():
    cyclic_prime = 1051  # Set the cyclic prime to 1051

    # Generate random plaintext and encrypt it
    plaintext = generate_plaintext(128)
    start_position = 0
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)
    superposition_sequence = [random.choice([-1, 1]) for _ in range(cyclic_prime - 1)]
    z_value = calculate_z_value(superposition_sequence)

    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = khan_encrypt(
        plaintext, cyclic_prime, cyclic_sequence, start_position)

    # Analyze movements
    movements = analyze_movements(ciphertext, cyclic_prime, cyclic_sequence, start_position)
    possible_movements = generate_possible_movements(ciphertext, movements)

    # Perform brute force attack
    decrypted_plaintext = brute_force_attack(ciphertext, possible_movements, movement_to_char)
    print(f"Decrypted Plaintext: {decrypted_plaintext}")

    # Check if decryption is successful
    if decrypted_plaintext:
        print("Decryption Successful" if plaintext == decrypted_plaintext else "Decryption Failed")
    else:
        print("Brute force attack failed to find the plaintext.")

if __name__ == "__main__":
    main()
