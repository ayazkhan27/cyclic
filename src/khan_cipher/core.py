"""
KHAN Stream Cipher Core Module

This module implements a high-performance stream cipher utilizing the maximum-length
recurring sequences of Full Reptend Primes (Primitive Roots) to construct a non-linear
Pseudorandom Number Generator (PRNG).
"""

import os
import hmac
import struct
from hashlib import sha256

# Optional C++ extension import
try:
    from .ckhan import bulk_xor  # type: ignore[import-untyped]
except ImportError:
    bulk_xor = None

from .primes import DEFAULT_PRIME


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


def _encode_prime(prime: int) -> bytes:
    """Encode a prime as a length-prefixed big-endian byte string."""
    prime_bytes = prime.to_bytes(
        (prime.bit_length() + 7) // 8, byteorder='big'
    )
    return struct.pack('>H', len(prime_bytes)) + prime_bytes


def _decode_prime(data: bytes, offset: int) -> tuple[int, int]:
    """Decode a length-prefixed prime from a byte buffer.

    Returns:
        (prime, new_offset) tuple.
    """
    prime_len = struct.unpack('>H', data[offset:offset + 2])[0]
    offset += 2
    prime = int.from_bytes(data[offset:offset + prime_len], byteorder='big')
    return prime, offset + prime_len


def encrypt(
    plaintext: bytes, key: bytes, prime: int | None = None
) -> bytes:
    """
    Encrypts a plaintext using the KHAN PRNG stream cipher.

    When no prime is specified, the pre-computed 128-bit default full reptend
    prime is used and embedded in the output payload for self-describing
    decryption.

    Args:
        plaintext (bytes): The arbitrary data to encrypt.
        key (bytes): The master cryptographic key (should be 32 bytes).
        prime (int | None): An explicit full reptend prime, or None to
            use the default 128-bit prime (embedded in payload).

    Returns:
        bytes: Encrypted payload.
            - With embedded prime:
              [Salt(16) | IV(16) | PrimeLen(2) | Prime(N) | CT(M) | MAC(32)]
            - With explicit prime (caller-managed):
              [Salt(16) | IV(16) | Ciphertext(M) | MAC(32)]

    Raises:
        ValueError: If plaintext is empty.
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    if not plaintext:
        raise ValueError("Plaintext cannot be empty.")

    embed_prime = prime is None
    if prime is None:
        prime = DEFAULT_PRIME

    iv = os.urandom(16)
    salt = os.urandom(16)

    derived_key = derive_key(key, salt)
    ksg = KhanKeystream(derived_key, prime, iv)

    # Generate keystream buffer
    if bulk_xor is not None:
        keystream_bytes = bytes([ksg.get_next_byte()
                                for _ in range(len(plaintext))])
        ciphertext = bulk_xor(plaintext, keystream_bytes)
    else:
        ciphertext = bytes([p ^ ksg.get_next_byte() for p in plaintext])

    if embed_prime:
        body = salt + iv + _encode_prime(prime) + ciphertext
    else:
        body = salt + iv + ciphertext

    mac = hmac.new(key, body, sha256).digest()
    return body + mac


def decrypt(
    payload: bytes, key: bytes, prime: int | None = None
) -> bytes:
    """
    Decrypts a KHAN payload back to plaintext.

    If no prime is provided, the prime is read from the payload header
    (new self-describing format).  For backward compatibility with legacy
    payloads that used an explicit prime, the caller may pass one directly.

    Args:
        payload (bytes): The full encrypted byte array.
        key (bytes): The symmetric master key.
        prime (int | None): Explicit prime override, or None to read
            from the payload.

    Returns:
        bytes: The pristine original plaintext.

    Raises:
        KhanDecryptionError: If the payload is invalid or MAC fails.
    """
    min_len = 64 if prime is not None else 67
    if len(payload) < min_len:
        raise KhanDecryptionError(
            "Payload is too short.")

    mac_provided = payload[-32:]
    body = payload[:-32]

    mac_calculated = hmac.new(key, body, sha256).digest()

    if not hmac.compare_digest(mac_calculated, mac_provided):
        raise KhanDecryptionError(
            "MAC verification failed. Data may have been tampered with.")

    salt = body[:16]
    iv = body[16:32]

    if prime is not None:
        # Legacy mode: caller provides the prime, rest is ciphertext
        ciphertext = body[32:]
    else:
        # New format: prime is embedded after IV
        prime, ct_offset = _decode_prime(body, 32)
        ciphertext = body[ct_offset:]

    derived_key = derive_key(key, salt)
    ksg = KhanKeystream(derived_key, prime, iv)

    if bulk_xor is not None:
        keystream_bytes = bytes([ksg.get_next_byte()
                                for _ in range(len(ciphertext))])
        plaintext = bulk_xor(ciphertext, keystream_bytes)
    else:
        plaintext = bytes([c ^ ksg.get_next_byte() for c in ciphertext])

    return plaintext
