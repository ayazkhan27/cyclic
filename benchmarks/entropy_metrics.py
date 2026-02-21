import os
import math
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from khan_cipher.core import encrypt

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({'font.family': 'serif', 'font.size': 12})

def calculate_shannon(data: bytes) -> float:
    if not data:
        return 0.0
    entropy = 0
    length = len(data)
    counts = Counter(data)
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def main():
    # Ensure directory exists
    os.makedirs('benchmarks/plots', exist_ok=True)
    os.makedirs('benchmarks/data', exist_ok=True)

    # Generate 1MB of pure keystream (encrypt zeros)
    # Master key = 32 bytes of zeros for deterministic testing or urandom for actual entropy test
    # We will use a fixed key here for reproducibility in benchmark
    master_key = b'\x00' * 32
    plaintext = b'\x00' * 1024 * 1024  # 1MB
    
    # Encrypt
    payload = encrypt(plaintext, master_key)
    # The payload is [salt(16) | iv(16) | ciphertext | mac(32)]
    # The keystream is equivalent to ciphertext because plaintext is all zeros (0 ^ K = K)
    ciphertext = payload[32:-32]
    
    # 1. Rolling Entropy Plot
    chunk_size = 1000
    entropies = []
    
    for i in range(0, len(ciphertext), chunk_size):
        chunk = ciphertext[i:i+chunk_size]
        if len(chunk) == chunk_size:
            entropies.append(calculate_shannon(chunk))
            
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(entropies)), entropies, color='b', alpha=0.7, label='Rolling Entropy (1KB Chunks)')
    plt.axhline(y=7.99, color='r', linestyle='--', label='Ideal Target (7.99 bits)')
    plt.xlabel('Keystream Block (1KB)')
    plt.ylabel('Shannon Entropy (Bits/Byte)')
    plt.title('KHAN Stream Cipher - Shannon Entropy Verification')
    plt.legend()
    plt.tight_layout()
    plt.savefig('benchmarks/plots/shannon_entropy.png', dpi=300)
    plt.close()
    
    # 2. Histogram of Byte Frequencies
    byte_counts = Counter(ciphertext)
    sorted_counts = [byte_counts.get(i, 0) for i in range(256)]
    
    plt.figure(figsize=(12, 6))
    plt.bar(range(256), sorted_counts, color='teal', edgecolor='black', alpha=0.8)
    plt.xlabel('Byte Value (0-255)')
    plt.ylabel('Frequency')
    plt.title('KHAN PRNG Output Byte Uniformity (1MB)')
    plt.axhline(y=len(ciphertext)/256, color='r', linestyle='--', label='Ideal Uniform Distribution')
    plt.legend()
    plt.tight_layout()
    plt.savefig('benchmarks/plots/byte_histogram.png', dpi=300)
    plt.close()
    
    print(f"Global Shannon Entropy of 1MB Keystream: {calculate_shannon(ciphertext):.5f} bits/byte")

if __name__ == "__main__":
    main()
