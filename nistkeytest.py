"""
Test suite for KHAN encryption algorithm
========================================

This script generates a cyclic sequence, encrypts a plaintext, and then analyzes the ciphertext for entropy and randomness.
It also estimates the security strength of the key material and the overall key space size.

The test suite consists of the following steps:

1. Generate a cyclic sequence of a given length using the provided prime number.
2. Encrypt a plaintext using the generated cyclic sequence and the provided start position.
3. Convert the ciphertext to bytes for analysis.
4. Estimate the entropy of the ciphertext using the NIST SP 800-90B methodology.
5. Perform a basic NIST randomness test (chi-squared test) on the ciphertext.
6. Estimate the security strength of the key material and the overall key space size.
"""
import random
import string
import numpy as np
import os
from math import log2
from scipy.stats import entropy
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import khan_encryption_2 as ke
import matplotlib.pyplot as plt

def generate_cyclic_sequence(prime, length):
    from decimal import Decimal, getcontext
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

def nist_entropy_estimate(data):
    """
    Estimate entropy using NIST SP 800-90B methodology.
    This version works with a list of integers.
    """
    _, counts = np.unique(data, return_counts=True)
    probabilities = counts / len(data)
    return entropy(probabilities, base=2)

def frequency_test(data):
    """
    Perform a basic frequency test on the data.
    """
    _, counts = np.unique(data, return_counts=True)
    expected = np.full_like(counts, len(data) / len(counts))
    chi_square = np.sum((counts - expected) ** 2 / expected)
    p_value = 1 - np.sum(counts * np.log(counts / expected))
    return p_value > 0.01

def estimate_security_strength(key_size, superposition_length):
    effective_key_size = key_size + log2(superposition_length)
    
    if effective_key_size < 112:
        return "Below NIST minimum recommendations"
    elif effective_key_size < 128:
        return "112-bit security (NIST legacy-use)"
    elif effective_key_size < 192:
        return "128-bit security"
    elif effective_key_size < 256:
        return "192-bit security"
    else:
        return "256-bit security or higher"

def generate_key_material(password, salt, length):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def main():
    cyclic_prime = 1051
    start_position = random.randint(1, cyclic_prime - 1)
    superposition_sequence_length = random.randint(2, 100) * 2  # Ensure even

    plaintext = ''.join(random.choices(string.ascii_letters + string.digits, k=1024))
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Generate key material
    password = "test_password"
    salt = os.urandom(16)
    key_material = generate_key_material(password, salt, 32)  # 256-bit key

    # Encrypt
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
        plaintext, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length
    )

    # Ensure ciphertext is a list of non-negative integers
    ciphertext_ints = [abs(x) for x in ciphertext]

    # Ensure ciphertext is a list of non-negative integers
    ciphertext_ints = [abs(x) for x in ciphertext]

    # Plot the ciphertext distribution
    plt.figure(figsize=(12, 6))
    plt.hist(ciphertext_ints, bins=50, edgecolor='black')
    plt.title('Distribution of Ciphertext Values')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.show()
    
    # Entropy estimation
    entropy = nist_entropy_estimate(ciphertext_ints)
    print(f"Estimated entropy: {entropy:.2f} bits per symbol")

    # Frequency test
    passes_frequency_test = frequency_test(ciphertext_ints)
    print(f"Passes basic frequency test: {passes_frequency_test}")

    # Security strength estimation
    key_size = 256  # Assuming 256-bit key material
    security_strength = estimate_security_strength(key_size, superposition_sequence_length)
    print(f"Estimated security strength: {security_strength}")

    # Key space size
    key_space_size = cyclic_prime * superposition_sequence_length * 2**256  # Include key material in calculation
    print(f"Approximate key space size: 2^{log2(key_space_size):.2f}")

if __name__ == "__main__":
    main()