import time
import random
import string
import math
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from eciespy import generate_eth_key, encrypt as ecc_encrypt, decrypt as ecc_decrypt
import numpy as np

# Import your KHAN encryption functions here
from asymmetricdemo import generate_keypair, encrypt, decrypt, generate_cyclic_sequence

# Helper functions
def calculate_entropy(data):
    _, counts = np.unique(list(data), return_counts=True)
    probabilities = counts / len(data)
    entropy = -sum(probabilities * np.log2(probabilities))
    return entropy

def calculate_avalanche_effect(original, modified):
    bit_changes = sum(bin(ord(a) ^ ord(b)).count('1') for a, b in zip(original, modified))
    return bit_changes / (8 * len(original))

def calculate_propagation_ratio(original_cipher, modified_cipher):
    bit_changes = sum(bin(int(a) ^ int(b)).count('1') for a, b in zip(original_cipher, modified_cipher))
    return bit_changes / (8 * len(original_cipher))

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

# ECC functions
def generate_ecc_keypair():
    private_key = generate_eth_key()
    public_key = private_key.public_key
    return public_key.to_hex(), private_key.to_hex()

# Comparison function
def compare_algorithms(message, key_size):
    results = {}

    # KHAN Encryption
    prime = key_size  # Assuming prime is equivalent to key size for KHAN
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    khan_public_key, khan_private_key = generate_keypair(prime, cyclic_sequence)

    start_time = time.time()
    khan_cipher, temp_start, superposition_points = encrypt(message, khan_public_key)
    khan_encrypt_time = time.time() - start_time

    start_time = time.time()
    khan_decrypted = decrypt(khan_cipher, khan_public_key, khan_private_key, temp_start, superposition_points)
    khan_decrypt_time = time.time() - start_time

    khan_entropy = calculate_entropy(''.join(map(str, khan_cipher)))
    khan_keyspace = prime * (2 ** len(khan_private_key[1]))  # Estimate based on prime and superposition sequence

    # RSA
    rsa_public_key, rsa_private_key = generate_rsa_keypair(key_size)

    start_time = time.time()
    rsa_cipher = rsa_encrypt(message, rsa_public_key)
    rsa_encrypt_time = time.time() - start_time

    start_time = time.time()
    rsa_decrypted = rsa_decrypt(rsa_cipher, rsa_private_key)
    rsa_decrypt_time = time.time() - start_time

    rsa_entropy = calculate_entropy(rsa_cipher)
    rsa_keyspace = 2 ** key_size

    # ECC
    ecc_public_key, ecc_private_key = generate_ecc_keypair()

    start_time = time.time()
    ecc_cipher = ecc_encrypt(ecc_public_key, message.encode())
    ecc_encrypt_time = time.time() - start_time

    start_time = time.time()
    ecc_decrypted = ecc_decrypt(ecc_private_key, ecc_cipher).decode()
    ecc_decrypt_time = time.time() - start_time

    ecc_entropy = calculate_entropy(ecc_cipher)
    ecc_keyspace = 2 ** (key_size // 2)  # ECC key size is typically half of RSA for equivalent security

    # Calculate avalanche effect and propagation ratio
    modified_message = message[:len(message)//2] + 'X' + message[len(message)//2+1:]

    khan_mod_cipher, _, _ = encrypt(modified_message, khan_public_key)
    khan_avalanche = calculate_avalanche_effect(message, modified_message)
    khan_propagation = calculate_propagation_ratio(khan_cipher, khan_mod_cipher)

    rsa_mod_cipher = rsa_encrypt(modified_message, rsa_public_key)
    rsa_avalanche = calculate_avalanche_effect(message, modified_message)
    rsa_propagation = calculate_propagation_ratio(rsa_cipher, rsa_mod_cipher)

    ecc_mod_cipher = ecc_encrypt(ecc_public_key, modified_message.encode())
    ecc_avalanche = calculate_avalanche_effect(message, modified_message)
    ecc_propagation = calculate_propagation_ratio(ecc_cipher, ecc_mod_cipher)

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
        'security_bits': key_size
    }

    results['ECC'] = {
        'encrypt_time': ecc_encrypt_time,
        'decrypt_time': ecc_decrypt_time,
        'entropy': ecc_entropy,
        'keyspace': ecc_keyspace,
        'avalanche': ecc_avalanche,
        'propagation': ecc_propagation,
        'security_bits': key_size // 2
    }

    return results

# Main execution
if __name__ == "__main__":
    message = "This is a test message for comparing asymmetric encryption algorithms."
    key_size = 2048  # Adjust as needed, ensuring it's a valid key size for all algorithms

    results = compare_algorithms(message, key_size)

    print(f"Comparison Results (Key Size: {key_size} bits)")
    print("-" * 50)
    for algo, metrics in results.items():
        print(f"{algo}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")
        print()