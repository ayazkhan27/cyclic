# full_reptend_elgamal_timed.py

import random
import time
from sympy import isprime, primitive_root

class FullReptendElGamal:
    def __init__(self):
        self.public_key = None  # (p, g, h)
        self.private_key = None  # x

    def is_full_reptend_prime(self, p):
        """Check if p is a full reptend prime."""
        if not isprime(p):
            return False
        k = 1
        while pow(10, k, p) != 1:
            k += 1
            if k >= p:
                return False
        return k == p - 1

    def generate_full_reptend_prime(self):
        """Select a known small full reptend prime."""
        known_full_reptend_primes = [
            7, 17, 19, 23, 29, 47, 59, 61, 97, 109, 113, 131, 149,
            167, 179, 181, 193, 223, 229, 233, 257, 263, 269, 313, 353
        ]
        # For demonstration, pick a small prime
        p = random.choice(known_full_reptend_primes)
        return p

    def generate_keys(self):
        """Generate public and private keys."""
        p = self.generate_full_reptend_prime()
        g = primitive_root(p)
        x = random.randint(2, p - 2)
        h = pow(g, x, p)
        self.public_key = (p, g, h)
        self.private_key = x

    def encrypt(self, plaintext):
        """Encrypt the plaintext using the public key."""
        p, g, h = self.public_key
        # Map plaintext to integers modulo p
        plaintext_bytes = plaintext.encode('utf-8')
        m_list = [int.from_bytes([byte], 'big') for byte in plaintext_bytes]

        ciphertext = []
        for m in m_list:
            if m >= p:
                raise ValueError("Plaintext integer too large for modulus p.")
            k = random.randint(2, p - 2)
            c1 = pow(g, k, p)
            c2 = (m * pow(h, k, p)) % p
            ciphertext.append((c1, c2))
        return ciphertext

    def decrypt(self, ciphertext):
        """Decrypt the ciphertext using the private key."""
        p, g, h = self.public_key
        x = self.private_key
        m_list = []
        for c1, c2 in ciphertext:
            s = pow(c1, x, p)
            # Compute modular inverse of s modulo p
            s_inv = pow(s, -1, p)
            m = (c2 * s_inv) % p
            m_list.append(m)
        # Convert integers back to bytes and then to string
        plaintext_bytes = bytes([m for m in m_list])
        plaintext = plaintext_bytes.decode('utf-8')
        return plaintext

    def test_avalanche_effect(self, plaintext):
        """Test the avalanche effect by flipping one bit in the plaintext."""
        # Encrypt original plaintext
        ciphertext_original = self.encrypt(plaintext)

        # Flip one bit in the plaintext
        plaintext_bytes = bytearray(plaintext.encode('utf-8'))
        plaintext_bytes[0] ^= 0b00000001  # Flip the least significant bit of the first byte
        plaintext_flipped = plaintext_bytes.decode('utf-8', errors='ignore')

        # Encrypt modified plaintext
        ciphertext_flipped = self.encrypt(plaintext_flipped)

        # Compare ciphertexts
        differences = 0
        total_bits = 0
        for (c1_orig, c2_orig), (c1_flip, c2_flip) in zip(ciphertext_original, ciphertext_flipped):
            c1_diff = c1_orig ^ c1_flip
            c2_diff = c2_orig ^ c2_flip
            differences += bin(c1_diff).count('1') + bin(c2_diff).count('1')
            total_bits += c1_orig.bit_length() + c2_orig.bit_length()
        avalanche_ratio = differences / total_bits if total_bits > 0 else 0
        return avalanche_ratio

    def security_bits(self):
        """Calculate the effective security bits based on the key size."""
        p, _, _ = self.public_key
        key_size = p.bit_length()
        # For discrete logarithm problem, effective security is roughly half the key size
        return key_size // 2

# Example usage with timing and analysis
if __name__ == "__main__":
    cipher = FullReptendElGamal()
    cipher.generate_keys()
    print("Public Key:", cipher.public_key)
    print("Private Key:", cipher.private_key)
    print("Effective Security Bits:", cipher.security_bits())

    plaintext = "Hello, World!"
    print("\nPlaintext:", plaintext)

    # Measure encryption time
    start_time = time.time()
    ciphertext = cipher.encrypt(plaintext)
    encryption_time = time.time() - start_time
    print("\nEncryption Time: {:.6f} seconds".format(encryption_time))

    print("\nCiphertext:")
    for c1, c2 in ciphertext:
        print(f"({c1}, {c2})")

    # Measure decryption time
    start_time = time.time()
    decrypted_plaintext = cipher.decrypt(ciphertext)
    decryption_time = time.time() - start_time
    print("\nDecryption Time: {:.6f} seconds".format(decryption_time))

    print("\nDecrypted Plaintext:", decrypted_plaintext)

    # Test avalanche effect
    avalanche_ratio = cipher.test_avalanche_effect(plaintext)
    print("\nAvalanche Effect Ratio: {:.2%}".format(avalanche_ratio))
