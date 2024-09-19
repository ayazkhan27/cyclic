import itertools
import string
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes

# -----------------------------------
# DES Encryption and Decryption Setup
# -----------------------------------

def pad(text):
    """
    Pads the input text to be a multiple of 8 bytes (DES block size).
    """
    while len(text) % 8 != 0:
        text += ' '
    return text

def des_encrypt(plaintext, key):
    """
    Encrypts plaintext using DES encryption.
    """
    cipher = DES.new(key, DES.MODE_ECB)
    padded_text = pad(plaintext)
    ciphertext = cipher.encrypt(padded_text.encode('utf-8'))
    return ciphertext

def des_decrypt(ciphertext, key):
    """
    Decrypts ciphertext using DES decryption.
    """
    cipher = DES.new(key, DES.MODE_ECB)
    decrypted_text = cipher.decrypt(ciphertext).decode('utf-8')
    return decrypted_text.strip()

# ------------------------
# Brute-Force Cracking DES
# ------------------------

def brute_force_des(ciphertext, known_plaintext):
    """
    Attempts to brute-force DES encryption by trying all possible keys.
    Args:
        ciphertext (bytes): The encrypted message.
        known_plaintext (str): The original plaintext message.
    Returns:
        str: The recovered key if successful, else None.
    """
    print("Starting brute-force attack on DES...")
    # DES key is 8 bytes, but only 56 bits are used (the last bit of each byte is parity)
    # For simplicity, we'll iterate through all possible 3-character keys (24 bits)
    # WARNING: Extending this to 56 bits is computationally intensive and not practical in standard environments.

    # Example: For demonstration, we'll use a smaller key space (e.g., printable ASCII characters)
    characters = string.ascii_letters + string.digits + string.punctuation
    total_keys = len(characters) ** 3  # Adjust the exponent based on desired key length

    for key_tuple in itertools.product(characters, repeat=3):
        key_str = ''.join(key_tuple)
        key_bytes = key_str.encode('utf-8')
        # DES requires 8-byte keys; we'll pad the key with spaces
        key_padded = key_bytes.ljust(8, b' ')
        try:
            decrypted = des_decrypt(ciphertext, key_padded)
            if decrypted == known_plaintext:
                print(f"Key found: '{key_str}'")
                return key_padded
        except:
            # Ignore decryption errors due to incorrect padding or non-printable characters
            continue
        if (key_tuple[0] == 'z' and key_tuple[1] == 'z' and key_tuple[2] == 'z'):
            print("Brute-force attack completed. Key not found in the given key space.")
            return None
    return None

# -----------------------------------
# Demonstration of DES Encryption
# -----------------------------------

def demo_des():
    # Example plaintext
    plaintext = "HelloWorld"

    # Example key (8 bytes)
    key = b'secret_k'

    print(f"Original Plaintext: {plaintext}")
    print(f"Encryption Key: {key.decode('utf-8').strip()}")

    # Encrypt the plaintext
    ciphertext = des_encrypt(plaintext, key)
    print(f"Ciphertext (hex): {ciphertext.hex()}")

    # Decrypt the ciphertext
    decrypted = des_decrypt(ciphertext, key)
    print(f"Decrypted Text: {decrypted}")

    # Attempt to brute-force the key
    recovered_key = brute_force_des(ciphertext, plaintext)
    if recovered_key:
        print(f"Recovered Key: {recovered_key}")
    else:
        print("Failed to recover the key.")

if __name__ == "__main__":
    demo_des()
