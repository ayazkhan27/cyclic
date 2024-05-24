from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

def rsa_encrypt_decrypt():
    # Generate RSA keys
    key = RSA.generate(2048)
    public_key = key.publickey()
    private_key = key

    # Encrypt
    cipher_rsa = PKCS1_OAEP.new(public_key)
    plaintext = "KnownPlaintext"
    ciphertext = cipher_rsa.encrypt(plaintext.encode())

    # Decrypt
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted_text = cipher_rsa.decrypt(ciphertext).decode()

    print(f"RSA Original Text: {plaintext}")
    print(f"RSA Decrypted Text: {decrypted_text}")

    # Known Plaintext Attack
    return plaintext == decrypted_text

rsa_result = rsa_encrypt_decrypt()
print(f"RSA Known Plaintext Attack Successful: {rsa_result}")

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def aes_encrypt_decrypt():
    key = get_random_bytes(16)  # AES-128
    cipher_aes = AES.new(key, AES.MODE_CBC)
    iv = cipher_aes.iv

    # Encrypt
    plaintext = "KnownPlaintext"
    ciphertext = cipher_aes.encrypt(pad(plaintext.encode(), AES.block_size))

    # Decrypt
    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
    decrypted_text = unpad(cipher_aes.decrypt(ciphertext), AES.block_size).decode()

    print(f"AES Original Text: {plaintext}")
    print(f"AES Decrypted Text: {decrypted_text}")

    # Known Plaintext Attack
    return plaintext == decrypted_text

aes_result = aes_encrypt_decrypt()
print(f"AES Known Plaintext Attack Successful: {aes_result}")

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

def chacha20_encrypt_decrypt():
    key = get_random_bytes(32)  # ChaCha20 requires 256-bit key
    cipher_chacha20 = ChaCha20.new(key=key)
    nonce = cipher_chacha20.nonce

    # Encrypt
    plaintext = "KnownPlaintext"
    ciphertext = cipher_chacha20.encrypt(plaintext.encode())

    # Decrypt
    cipher_chacha20 = ChaCha20.new(key=key, nonce=nonce)
    decrypted_text = cipher_chacha20.decrypt(ciphertext).decode()

    print(f"ChaCha20 Original Text: {plaintext}")
    print(f"ChaCha20 Decrypted Text: {decrypted_text}")

    # Known Plaintext Attack
    return plaintext == decrypted_text

chacha20_result = chacha20_encrypt_decrypt()
print(f"ChaCha20 Known Plaintext Attack Successful: {chacha20_result}")

from Crypto.Cipher import Salsa20
from Crypto.Random import get_random_bytes

def salsa20_encrypt_decrypt():
    key = get_random_bytes(32)  # Salsa20 requires 256-bit key
    cipher_salsa20 = Salsa20.new(key=key)
    nonce = cipher_salsa20.nonce

    # Encrypt
    plaintext = "KnownPlaintext"
    ciphertext = cipher_salsa20.encrypt(plaintext.encode())

    # Decrypt
    cipher_salsa20 = Salsa20.new(key=key, nonce=nonce)
    decrypted_text = cipher_salsa20.decrypt(ciphertext).decode()

    print(f"Salsa20 Original Text: {plaintext}")
    print(f"Salsa20 Decrypted Text: {decrypted_text}")

    # Known Plaintext Attack
    return plaintext == decrypted_text

salsa20_result = salsa20_encrypt_decrypt()
print(f"Salsa20 Known Plaintext Attack Successful: {salsa20_result}")



