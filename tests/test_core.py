import os
from khan_cipher.core import encrypt, decrypt

def test_encryption_decryption_symmetry():
    master_key = os.urandom(32)
    original = os.urandom(1024) # random 1KB string
    
    payload = encrypt(original, master_key)
    decrypted = decrypt(payload, master_key)
    
    assert original == decrypted
