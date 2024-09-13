import time
import random
import string
import math
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import numpy as np

# Import your KHAN encryption functions here
from asymmetricdemo import generate_keypair, encrypt, decrypt, generate_cyclic_sequence

# Helper functions
def calculate_entropy(data):
    if isinstance(data, str):
        data = data.encode()
    _, counts = np.unique(list(data), return_counts=True)
    probabilities = counts / len(data)
    entropy = -sum(probabilities * np.log2(probabilities))
    return entropy

def calculate_avalanche_effect(original, modified):
    return sum(a != b for a, b in zip(original, modified)) / len(original)

def calculate_propagation_ratio(original_cipher, modified_cipher):
    return sum(a != b for a, b in zip(original_cipher, modified_cipher)) / len(original_cipher)

# RSA functions
def generate_rsa_keypair(key_size):
    key = RSA.generate(key_size)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key, private_key

def rsa_encrypt(message, public_key):
    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)
    return cipher.encrypt(message.encode())

def rsa_decrypt(ciphertext, private_key):
    key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(ciphertext).decode()

# Comparison function
def compare_algorithms(message, rsa_key_size, khan_prime):
    results = {}

    # KHAN Encryption
    cyclic_sequence = generate_cyclic_sequence(khan_prime, khan_prime - 1)
    khan_public_key, khan_private_key = generate_keypair(khan_prime, cyclic_sequence)

    start_time = time.time()
    khan_cipher, temp_start, superposition_points = encrypt(message, khan_public_key)
    khan_encrypt_time = time.time() - start_time

    start_time = time.time()
    khan_decrypted = decrypt(khan_cipher, khan_public_key, khan_private_key, temp_start, superposition_points)
    khan_decrypt_time = time.time() - start_time

    khan_entropy = calculate_entropy(''.join(map(str, khan_cipher)))
    khan_keyspace = khan_prime * (2 ** len(khan_private_key[1]))  # Estimate based on prime and superposition sequence

    # RSA
    rsa_public_key, rsa_private_key = generate_rsa_keypair(rsa_key_size)

    start_time = time.time()
    rsa_cipher = rsa_encrypt(message, rsa_public_key)
    rsa_encrypt_time = time.time() - start_time

    start_time = time.time()
    rsa_decrypted = rsa_decrypt(rsa_cipher, rsa_private_key)
    rsa_decrypt_time = time.time() - start_time

    rsa_entropy = calculate_entropy(rsa_cipher)
    rsa_keyspace = 2 ** rsa_key_size

    # Calculate avalanche effect and propagation ratio
    modified_message = message[:len(message)//2] + 'X' + message[len(message)//2+1:]

    khan_mod_cipher, _, _ = encrypt(modified_message, khan_public_key)
    khan_avalanche = calculate_avalanche_effect(str(khan_cipher), str(khan_mod_cipher))
    khan_propagation = calculate_propagation_ratio(str(khan_cipher), str(khan_mod_cipher))

    rsa_mod_cipher = rsa_encrypt(modified_message, rsa_public_key)
    rsa_avalanche = calculate_avalanche_effect(rsa_cipher, rsa_mod_cipher)
    rsa_propagation = calculate_propagation_ratio(rsa_cipher, rsa_mod_cipher)

    results['KHAN'] = {
        'encrypt_time': khan_encrypt_time,
        'decrypt_time': khan_decrypt_time,
        'entropy': khan_entropy,
        'keyspace': khan_keyspace,
        'avalanche': khan_avalanche,
        'propagation': khan_propagation,
        'security_bits': math.log2(khan_keyspace)
    }

    results['RSA'] = {
        'encrypt_time': rsa_encrypt_time,
        'decrypt_time': rsa_decrypt_time,
        'entropy': rsa_entropy,
        'keyspace': rsa_keyspace,
        'avalanche': rsa_avalanche,
        'propagation': rsa_propagation,
        'security_bits': rsa_key_size
    }

    return results

# Main execution
if __name__ == "__main__":
    message = "This is a test message for comparing asymmetric encryption algorithms."
    rsa_key_size = 1024
    khan_prime = 1051  # Adjust this to a suitable full reptend prime

    results = compare_algorithms(message, rsa_key_size, khan_prime)

    print(f"Comparison Results (RSA Key Size: {rsa_key_size} bits, KHAN Prime: {khan_prime})")
    print("-" * 50)
    for algo, metrics in results.items():
        print(f"{algo}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")
        print()