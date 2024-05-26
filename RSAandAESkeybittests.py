import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
import math

def generate_rsa_key(key_size):
    if key_size < 1024:
        raise ValueError("RSA modulus length must be >= 1024")
    return RSA.generate(key_size)

def measure_rsa_encryption_decryption(plaintext, rsa_key):
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    start_time = time.time()
    ciphertext = cipher_rsa.encrypt(plaintext)
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_text = cipher_rsa.decrypt(ciphertext)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time

def generate_aes_key(key_size):
    if key_size not in [128, 192, 256]:
        raise ValueError("AES key size must be 128, 192, or 256 bits")
    key = b'This is a key123'  # Convert the key to bytes
    return AES.new(key, AES.MODE_ECB)

def measure_aes_encryption_decryption(plaintext, aes_key):
    plaintext = pad(plaintext, AES.block_size)  # Pad the plaintext to ensure it's aligned to the block boundary
    start_time = time.time()
    ciphertext = aes_key.encrypt(plaintext)
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_text = unpad(aes_key.decrypt(ciphertext), AES.block_size)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time

def main():
    # List of key sizes to test
    rsa_key_sizes = [1024, 2048, 4096]
    aes_key_sizes = [128, 192, 256]

    for rsa_key_size, aes_key_size in zip(rsa_key_sizes, aes_key_sizes):
        rsa_key = generate_rsa_key(rsa_key_size)
        aes_key = generate_aes_key(aes_key_size)

        # Generate random plaintext
        plaintext = b'This is a test plaintext.'

        # Measure encryption and decryption for RSA
        rsa_encryption_time, rsa_decryption_time = measure_rsa_encryption_decryption(plaintext, rsa_key)

        # Measure encryption and decryption for AES
        aes_encryption_time, aes_decryption_time = measure_aes_encryption_decryption(plaintext, aes_key)

        # Calculate the number of possible keys for RSA and AES
        rsa_num_possible_keys = 2 ** rsa_key_size
        aes_num_possible_keys = 2 ** aes_key_size

        # Calculate the security level in bits for RSA and AES
        rsa_security_level_bits = math.log2(rsa_num_possible_keys)
        aes_security_level_bits = aes_key_size

        # Display results for RSA
        print("\nRSA Key Size:", rsa_key_size, "bits")
        print("RSA Security Level (in bits):", rsa_security_level_bits)
        print("RSA Encryption Time:", rsa_encryption_time, "seconds")
        print("RSA Decryption Time:", rsa_decryption_time, "seconds")

        # Display results for AES
        print("\nAES Key Size:", aes_key_size, "bits")
        print("AES Security Level (in bits):", aes_security_level_bits)
        print("AES Encryption Time:", aes_encryption_time, "seconds")
        print("AES Decryption Time:", aes_decryption_time, "seconds")

if __name__ == "__main__":
    main()
