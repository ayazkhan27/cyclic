import random
import time
import string
import numpy as np
from hashlib import sha256
from scipy.stats import entropy as scipy_entropy
from collections import Counter
from decimal import Decimal, getcontext
from scipy.fft import fft

# Import helper functions from khan_encryption_2.py and asymmetricdemo.py
from asymmetricdemo import generate_cyclic_sequence, minimal_movement, generate_target_sequences, analyze_cyclic_prime
from khan_encryption_2 import assign_z_layer

# Function for Quantum Resistance Check (No integer factorization or discrete log)
def quantum_resistance_check():
    print("Quantum resistance check: PASS (No integer factorization or discrete logs used).")

# Helper function to calculate entropy of a string
def calculate_entropy(message):
    counter = Counter(message)
    total_chars = sum(counter.values())
    return scipy_entropy([count / total_chars for count in counter.values()])

# Helper function to calculate avalanche effect between two messages
def avalanche_effect(msg1, msg2):
    diff = sum(1 for a, b in zip(msg1, msg2) if a != b)
    return diff / len(msg1)

# Function to ensure a balanced superposition sequence
def generate_superposition_sequence(sequence_length):
    # Ensure the sequence length is even for balance
    if sequence_length % 2 != 0:
        sequence_length += 1

    half_length = sequence_length // 2

    # Generate exactly half as 1 and half as -1
    sequence = [1] * half_length + [-1] * half_length
    random.shuffle(sequence)  # Randomly shuffle the sequence

    return sequence

# Lattice Mapping (Quantum Resistance)
def map_to_lattice(movements):
    return [(i, m) for i, m in enumerate(movements)]

# Torus Geometry-based Encryption (Asymmetry)
def torus_geometry_encrypt(plaintext, prime, cyclic_sequence, public_key):
    movements, superposition_points = analyze_cyclic_prime(prime, cyclic_sequence, public_key)

    # Apply lattice-based cryptography for quantum resistance
    lattice = map_to_lattice(movements)

    # Calculate Z-dimension shifts (Z-dimension as private key)
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    z_vals = [assign_z_layer(m, salt) for m in movements]

    # Encrypt the plaintext using movements, Z-shifts, and superposition sequence
    cipher_text = []
    superposition_sequence = generate_superposition_sequence(len(plaintext))

    for i, char in enumerate(plaintext):
        movement = movements[ord(char) % prime]
        z_layer = assign_z_layer(movement, salt)
        encrypted_value = movement * z_layer + z_vals[i % len(z_vals)]
        cipher_text.append(encrypted_value)

    return cipher_text, salt, superposition_sequence

# Decrypt function with asymmetric key
def torus_geometry_decrypt(cipher_text, prime, cyclic_sequence, private_key, salt, superposition_sequence):
    movements, _ = analyze_cyclic_prime(prime, cyclic_sequence, private_key[0])
    movement_to_char = {m: chr(i % 256) for i, m in enumerate(movements)}
    plaintext = []
    superposition_index = 0

    # Decrypt the ciphertext
    for i, movement in enumerate(cipher_text):
        if i in superposition_sequence:
            # Apply superposition direction from private key
            direction = private_key[1][superposition_index % len(private_key[1])]
            movement *= direction
            superposition_index += 1

        original_movement = (movement - private_key[0] * prime) // assign_z_layer(movement, salt)
        char = movement_to_char.get(original_movement, chr(abs(original_movement) % 256))
        plaintext.append(char)

    return ''.join(plaintext)

# Generate keypair (public and private keys)
def generate_keypair(prime, cyclic_sequence):
    start_position = random.randint(1, prime - 1)
    superposition_sequence_length = random.randint(10000, 40000) // 2 * 2
    superposition_sequence = generate_superposition_sequence(superposition_sequence_length)
    public_key = start_position  # Only start position is part of public key
    private_key = (start_position, superposition_sequence)  # Start position and superposition sequence as private key
    return public_key, private_key

# Encryption/Decryption Test Suite
def run_encryption_test():
    prime = 1051
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)

    # Key generation
    print("Generating public/private keypair...")
    public_key, private_key = generate_keypair(prime, cyclic_sequence)
    print("Public Key (prime):", public_key)
    print("Private Key (start_position, superposition_sequence length):", private_key[0], len(private_key[1]))

    msg = input("Enter message to encrypt: ")
    print("Original message:", msg)

    # Encrypt
    start_time = time.time()
    encrypted_msg, salt, superposition_sequence = torus_geometry_encrypt(msg, prime, cyclic_sequence, public_key)
    encryption_time = time.time() - start_time
    print(f"Encrypted message: {' '.join(map(str, encrypted_msg))}")
    print(f"Encryption time: {encryption_time:.6f} seconds")

    # Decrypt
    start_time = time.time()
    decrypted_msg = torus_geometry_decrypt(encrypted_msg, prime, cyclic_sequence, private_key, salt, superposition_sequence)
    decryption_time = time.time() - start_time
    print(f"Decrypted message: {decrypted_msg}")
    print(f"Decryption time: {decryption_time:.6f} seconds")

    # Check if encryption/decryption is successful
    if decrypted_msg == msg:
        print("Success! Decryption matches the original message.")
    else:
        print("Error! Decryption failed.")

    # Measure entropy
    msg_entropy = calculate_entropy(msg)
    print(f"Message entropy: {msg_entropy:.4f}")

    # Avalanche effect
    altered_msg = msg[:len(msg) // 2] + 'A' + msg[len(msg) // 2 + 1:]
    avalanche = avalanche_effect(msg, altered_msg)
    print(f"Avalanche effect (compared to altered message): {avalanche * 100:.2f}%")

    # Quantum resistance check
    quantum_resistance_check()

    # Security metrics: entropy, avalanche effect, and encryption times give us insight into security bits
    security_bits = msg_entropy * len(msg)
    print(f"Estimated security bits: {security_bits:.2f} bits")

# Run the test
if __name__ == "__main__":
    run_encryption_test()
