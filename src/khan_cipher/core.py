"""
KHAN Stream Cipher Core Module

This module implements a high-performance stream cipher utilizing the maximum-length
recurring sequences of Full Reptend Primes (Primitive Roots) to construct a non-linear
Pseudorandom Number Generator (PRNG).
"""

import os
import hmac
from hashlib import sha256

# Optional C++ extension import
try:
    from .ckhan import bulk_xor
except ImportError:
    bulk_xor = None


class KhanDecryptionError(Exception):
    """Raised when MAC verification fails during decryption or data is tampered with."""
    pass


def derive_key(master_key: bytes, salt: bytes) -> bytes:
    """
    Derives a secure PRNG state key using HMAC-SHA256.

    Args:
        master_key (bytes): The 256-bit explicit master key.
        salt (bytes): A random 16-byte salt.

    Returns:
        bytes: The derived 32-byte key.
    """
    return hmac.new(master_key, salt, sha256).digest()


class KhanKeystream:
    """
    The mathematical PRNG Sequence Generator utilizing Primitive Roots Modulo P.
    Generates state on-the-fly using O(1) memory discrete logarithm tracking.
    """

    def __init__(self, key: bytes, prime: int, iv: bytes):
        self.prime = prime

        # Calculate start position based on key and IV
        key_int = int.from_bytes(key, 'big')
        iv_int = int.from_bytes(iv, 'big')

        # The sequence length of a full reptend prime is always p - 1
        self.position = (key_int ^ iv_int) % (self.prime - 1)

        # O(1) On-the-fly state calculation: 10^position mod p
        self.current_rem = pow(10, self.position, self.prime)

        self.previous_hash = sha256(key + iv).digest()

    def get_next_byte(self) -> int:
        current_val = self.current_rem % 256

        # Advance the dial by multiplying by 10 mod p (O(1) time complexity)
        self.current_rem = (self.current_rem * 10) % self.prime
        next_val = self.current_rem % 256

        # Calculate minimal movement vector mod 256
        movement = (next_val - current_val) % 256

        # Mathematical Z-Layer application
        hash_val = self.previous_hash[0]
        out_byte = movement ^ hash_val

        # Update running hash
        self.previous_hash = sha256(
            self.previous_hash + bytes([out_byte])).digest()
        return out_byte


def encrypt(plaintext: bytes, key: bytes, prime: int = 100003) -> bytes:
    """
    Encrypts a plaintext using the KHAN PRNG stream cipher.

    Args:
        plaintext (bytes): The arbitrary data to encrypt.
        key (bytes): The master cryptographic key (should be 32 bytes).
        prime (int): The cyclic full reptend prime to use. Defaults to 100003.

    Returns:
        bytes: Target payload consisting of [Salt(16) | IV(16) | Ciphertext(N) | MAC(32)].

    Raises:
        ValueError: If plaintext is empty.
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    if not plaintext:
        raise ValueError("Plaintext cannot be empty.")

    iv = os.urandom(16)
    salt = os.urandom(16)

    derived_key = derive_key(key, salt)
    ksg = KhanKeystream(derived_key, prime, iv)

    # Generate keystream buffer
    # If C++ bulk_xor extension is available, use it
    if bulk_xor is not None:
        keystream_bytes = bytes([ksg.get_next_byte()
                                for _ in range(len(plaintext))])
        ciphertext = bulk_xor(plaintext, keystream_bytes)
    else:
        ciphertext = bytes([p ^ ksg.get_next_byte() for p in plaintext])

    mac = hmac.new(key, ciphertext, sha256).digest()

    return salt + iv + ciphertext + mac


def decrypt(payload: bytes, key: bytes, prime: int = 100003) -> bytes:
    """
    Decrypts a KHAN payload back to plaintext.

    Args:
        payload (bytes): The full encrypted byte array [Salt | IV | Ciphertext | MAC].
        key (bytes): The symmetric master key.
        prime (int): The cyclic full reptend prime used for encryption.

    Returns:
        bytes: The pristine original plaintext.

    Raises:
        KhanDecryptionError: If the payload length is invalid or MAC verification fails.
    """
    if len(payload) < 64:
        raise KhanDecryptionError(
            "Payload is too short to contain Salt, IV, and MAC.")

    salt = payload[:16]
    iv = payload[16:32]
    mac_provided = payload[-32:]
    ciphertext = payload[32:-32]

    mac_calculated = hmac.new(key, ciphertext, sha256).digest()

    if not hmac.compare_digest(mac_calculated, mac_provided):
        raise KhanDecryptionError(
            "MAC verification failed. Data may have been tampered with.")

    derived_key = derive_key(key, salt)
    ksg = KhanKeystream(derived_key, prime, iv)

    if bulk_xor is not None:
        keystream_bytes = bytes([ksg.get_next_byte()
                                for _ in range(len(ciphertext))])
        plaintext = bulk_xor(ciphertext, keystream_bytes)
    else:
        plaintext = bytes([c ^ ksg.get_next_byte() for c in ciphertext])

    return plaintext
