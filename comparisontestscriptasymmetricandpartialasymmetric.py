import time
import math
import random
import string
from collections import Counter
import matplotlib.pyplot as plt

# Import functions from asymmetricdemo.py
from asymmetricdemo import generate_cyclic_sequence as gen_cyclic_seq_ad
from asymmetricdemo import generate_keypair as gen_keypair_ad
from asymmetricdemo import encrypt as encrypt_ad
from asymmetricdemo import decrypt as decrypt_ad

# Import functions from khan_encryption_2.py
from khan_encryption_2 import generate_plaintext
from khan_encryption_2 import generate_keys as gen_keys_ke2
from khan_encryption_2 import khan_encrypt as encrypt_ke2
from khan_encryption_2 import khan_decrypt as decrypt_ke2

# Utility functions
def calculate_entropy(data):
    frequency = Counter(data)
    data_len = len(data)
    entropy = -sum((freq / data_len) * math.log2(freq / data_len) for freq in frequency.values())
    return entropy

def measure_avalanche_effect(algorithm_encrypt, plaintext1, plaintext2, *args, **kwargs):
    ciphertext1, *rest1 = algorithm_encrypt(plaintext1, *args, **kwargs)
    ciphertext2, *rest2 = algorithm_encrypt(plaintext2, *args, **kwargs)
    # Flatten ciphertexts if they are lists of numbers
    if isinstance(ciphertext1, list):
        ciphertext1_bits = ''.join(format(x, 'b') for x in ciphertext1)
        ciphertext2_bits = ''.join(format(x, 'b') for x in ciphertext2)
    else:
        ciphertext1_bits = format(ciphertext1, 'b')
        ciphertext2_bits = format(ciphertext2, 'b')
    # Pad the shorter one
    max_len = max(len(ciphertext1_bits), len(ciphertext2_bits))
    ciphertext1_bits = ciphertext1_bits.zfill(max_len)
    ciphertext2_bits = ciphertext2_bits.zfill(max_len)
    # Calculate bit differences
    differences = sum(bit1 != bit2 for bit1, bit2 in zip(ciphertext1_bits, ciphertext2_bits))
    total_bits = max_len
    avalanche_effect = (differences / total_bits) * 100  # As percentage
    return avalanche_effect

def measure_encryption_time(algorithm_encrypt, plaintext, *args, **kwargs):
    start_time = time.time()
    result = algorithm_encrypt(plaintext, *args, **kwargs)
    end_time = time.time()
    encryption_time = end_time - start_time
    return encryption_time, result

def measure_decryption_time(algorithm_decrypt, *args, **kwargs):
    start_time = time.time()
    result = algorithm_decrypt(*args, **kwargs)
    end_time = time.time()
    decryption_time = end_time - start_time
    return decryption_time, result

def test_encryption_algorithm(name, encrypt_func, decrypt_func, plaintext, encrypt_args, decrypt_args):
    print(f"\nTesting {name} Encryption Algorithm")

    # Measure encryption time and get ciphertext
    encryption_time, encryption_result = measure_encryption_time(encrypt_func, plaintext, *encrypt_args)
    ciphertext = encryption_result[0] if isinstance(encryption_result, tuple) else encryption_result

    # Measure decryption time and get decrypted text
    decryption_time, decrypted_text = measure_decryption_time(decrypt_func, *decrypt_args(ciphertext, encryption_result))

    # Calculate entropy
    entropy = calculate_entropy(ciphertext)

    # Print results
    print(f"Plaintext: {plaintext}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Decrypted Text: {decrypted_text}")
    print(f"Encryption Time: {encryption_time:.6f} seconds")
    print(f"Decryption Time: {decryption_time:.6f} seconds")
    print(f"Entropy of Ciphertext: {entropy:.6f} bits per symbol")

    # Check if decryption is successful
    if decrypted_text == plaintext:
        print("Decryption Successful")
    else:
        print("Decryption Failed")

    # Return results for further analysis
    return {
        'ciphertext': ciphertext,
        'encryption_time': encryption_time,
        'decryption_time': decryption_time,
        'entropy': entropy,
        'decrypted_text': decrypted_text,
        'encryption_result': encryption_result
    }

def compare_algorithms():
    # Test parameters
    plaintext_length = 64
    plaintext = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(plaintext_length))

    # Generate plaintexts differing by one bit for avalanche effect
    plaintext_bits = ''.join(format(ord(c), '08b') for c in plaintext)
    # Flip one bit in plaintext
    flipped_bit_index = random.randint(0, len(plaintext_bits) - 1)
    plaintext_bits_flipped = (
        plaintext_bits[:flipped_bit_index] +
        ('1' if plaintext_bits[flipped_bit_index] == '0' else '0') +
        plaintext_bits[flipped_bit_index + 1:]
    )
    # Convert bits back to string
    plaintext_flipped = ''.join(chr(int(plaintext_bits_flipped[i:i+8], 2)) for i in range(0, len(plaintext_bits_flipped), 8))

    # Testing Asymmetric Demo
    print("=== Testing Asymmetric Demo ===")
    prime_ad = 1051
    cyclic_sequence_ad = gen_cyclic_seq_ad(prime_ad, prime_ad - 1)
    public_key_ad, private_key_ad = gen_keypair_ad(prime_ad, cyclic_sequence_ad)
    # Prepare encryption and decryption arguments
    encrypt_args_ad = (public_key_ad,)
    def decrypt_args_ad(ciphertext, encryption_result):
        # Extract necessary values from encryption_result
        temp_start, superposition_points = encryption_result[1], encryption_result[2]
        return (ciphertext, public_key_ad, private_key_ad, temp_start, superposition_points)
    results_ad = test_encryption_algorithm(
        'Asymmetric Demo', encrypt_ad, decrypt_ad, plaintext, encrypt_args_ad, decrypt_args_ad
    )
    # Avalanche Effect for Asymmetric Demo
    avalanche_ad = measure_avalanche_effect(encrypt_ad, plaintext, plaintext_flipped, *encrypt_args_ad)
    print(f"Avalanche Effect (Asymmetric Demo): {avalanche_ad:.2f}%")

    # Testing KHAN Encryption 2
    print("\n=== Testing KHAN Encryption 2 ===")
    prime_ke2 = 1051
    start_position_ke2 = random.randint(0, prime_ke2 - 1)
    superposition_sequence_length_ke2 = 40000
    cyclic_sequence_ke2 = gen_cyclic_seq_ad(prime_ke2, prime_ke2 - 1)  # Assuming same function
    # Generate keys
    char_to_movement_ke2, movement_to_char_ke2 = gen_keys_ke2(prime_ke2, cyclic_sequence_ke2, start_position_ke2)
    # Prepare encryption and decryption arguments
    encrypt_args_ke2 = (prime_ke2, cyclic_sequence_ke2, start_position_ke2, superposition_sequence_length_ke2)
    def decrypt_args_ke2(ciphertext, encryption_result):
        # Extract necessary values from encryption_result
        char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = encryption_result[1:]
        return (
            ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence,
            iv, salt, z_layers, prime_ke2, start_position_ke2, cyclic_sequence_ke2
        )
    results_ke2 = test_encryption_algorithm(
        'KHAN Encryption 2', encrypt_ke2, decrypt_ke2, plaintext, encrypt_args_ke2, decrypt_args_ke2
    )
    # Avalanche Effect for KHAN Encryption 2
    avalanche_ke2 = measure_avalanche_effect(
        encrypt_ke2, plaintext, plaintext_flipped, *encrypt_args_ke2
    )
    print(f"Avalanche Effect (KHAN Encryption 2): {avalanche_ke2:.2f}%")

    # Comparing results
    print("\n=== Comparison Results ===")
    print(f"Asymmetric Demo - Entropy: {results_ad['entropy']:.6f}, Encryption Time: {results_ad['encryption_time']:.6f}, Decryption Time: {results_ad['decryption_time']:.6f}")
    print(f"KHAN Encryption 2 - Entropy: {results_ke2['entropy']:.6f}, Encryption Time: {results_ke2['encryption_time']:.6f}, Decryption Time: {results_ke2['decryption_time']:.6f}")

    # Plotting ciphertext distribution
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.hist(results_ad['ciphertext'], bins=50)
    plt.title("Asymmetric Demo Ciphertext Distribution")
    plt.xlabel("Ciphertext Values")
    plt.ylabel("Frequency")

    plt.subplot(1, 2, 2)
    plt.hist(results_ke2['ciphertext'], bins=50)
    plt.title("KHAN Encryption 2 Ciphertext Distribution")
    plt.xlabel("Ciphertext Values")
    plt.ylabel("Frequency")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    compare_algorithms()
