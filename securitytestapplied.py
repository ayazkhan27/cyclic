import random
import string
import numpy as np
import os
from math import log2
from scipy.stats import entropy
import khan_encryption_2 as ke
import matplotlib.pyplot as plt

def generate_cyclic_sequence(prime, length):
    from decimal import Decimal, getcontext
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

def analyze_cyclic_sequence(sequence):
    """
    Analyze the cyclic sequence for repeating patterns or structure.
    This checks for periodicity or predictability in the cyclic sequence.
    """
    length = len(sequence)
    half_len = length // 2
    periodicities = []
    
    # Check if any segments of the sequence repeat periodically
    for i in range(1, half_len + 1):
        if sequence[:i] == sequence[i:2*i]:
            periodicities.append(i)
    
    if periodicities:
        print(f"Detected periodicities at positions: {periodicities}")
    else:
        print("No periodic patterns detected in the cyclic sequence.")

def analyze_superposition_sequence(sequence):
    """
    Analyze the superposition sequence for randomness using a runs test and autocorrelation.
    """
    def runs_test(seq):
        """Check the number of runs (sequences of consecutive identical values) in the sequence."""
        runs = 1
        for i in range(1, len(seq)):
            if seq[i] != seq[i-1]:
                runs += 1
        return runs
    
    def autocorrelation_test(seq):
        """Check if the sequence has significant autocorrelation."""
        mean = np.mean(seq)
        normalized_seq = [x - mean for x in seq]
        autocorr = np.correlate(normalized_seq, normalized_seq, mode='full') / len(seq)
        autocorr = autocorr[len(autocorr)//2:]  # Get the positive lag values
        return autocorr
    
    # Perform runs test
    runs = runs_test(sequence)
    print(f"Number of runs in superposition sequence: {runs}")
    
    # Perform autocorrelation test
    autocorr = autocorrelation_test(sequence)
    plt.figure(figsize=(8, 4))
    plt.plot(autocorr, label="Autocorrelation")
    plt.title("Autocorrelation of Superposition Sequence")
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.grid(True)
    plt.legend()
    plt.show()

def analyze_z_layers(z_layers):
    """
    Analyze Z-layer behavior for uniformity and distribution. Z-layers should be spread uniformly across a range.
    """
    plt.figure(figsize=(8, 4))
    plt.hist(z_layers, bins=range(min(z_layers), max(z_layers)+1), edgecolor='black', alpha=0.7)
    plt.title("Distribution of Z-layers")
    plt.xlabel("Z-layer value")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)
    plt.show()

    # Check for uniformity in Z-layers
    _, counts = np.unique(z_layers, return_counts=True)
    expected = len(z_layers) / len(counts)
    chi_square = np.sum((counts - expected) ** 2 / expected)
    print(f"Chi-square statistic for Z-layer distribution: {chi_square}")

def estimate_key_space_size(cyclic_prime, superposition_length):
    """
    Estimate the total key space size, which depends on the prime, superposition sequence, and key material.
    """
    key_space_size = cyclic_prime * superposition_length * 2**256  # Include key material in calculation
    return key_space_size

def main():
    cyclic_prime = 1051
    start_position = random.randint(1, cyclic_prime - 1)
    superposition_sequence_length = random.randint(2, 100) * 2  # Ensure even

    plaintext = ''.join(random.choices(string.ascii_letters + string.digits, k=1024))
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Analyze cyclic sequence for patterns
    print("Analyzing cyclic sequence...")
    analyze_cyclic_sequence(cyclic_sequence)

    # Encrypt the plaintext using KHAN encryption
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
        plaintext, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length
    )

    # Ensure ciphertext is a list of non-negative integers
    ciphertext_ints = [abs(x) for x in ciphertext]

    # Analyze the superposition sequence for randomness
    print("Analyzing superposition sequence...")
    analyze_superposition_sequence(superposition_sequence)

    # Analyze Z-layer distribution
    print("Analyzing Z-layer distribution...")
    analyze_z_layers(z_layers)

    # Estimate key space size
    key_space_size = estimate_key_space_size(cyclic_prime, superposition_sequence_length)
    print(f"Approximate key space size: 2^{log2(key_space_size):.2f}")

if __name__ == "__main__":
    main()
