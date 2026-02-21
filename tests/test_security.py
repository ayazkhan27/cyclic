import os
import pytest
from khan_cipher.core import encrypt, decrypt, KhanDecryptionError

def test_mac_tamper_rejection():
    master_key = os.urandom(32)
    plaintext = b"Sensitive Corporate Data"
    payload = bytearray(encrypt(plaintext, master_key))
    
    # Flip exactly one bit in the ciphertext portion (which starts at index 32)
    payload[32] ^= 0x01
    
    with pytest.raises(KhanDecryptionError):
        decrypt(bytes(payload), master_key)

def test_iv_uniqueness():
    master_key = os.urandom(32)
    plaintext = b"The exact same text."
    
    payload1 = encrypt(plaintext, master_key)
    payload2 = encrypt(plaintext, master_key)
    
    # Payloads must be different because of random IV and salt
    assert payload1 != payload2
    
    # The ciphertext (bytes 32 to -32) needs to be different too
    assert payload1[32:-32] != payload2[32:-32]
