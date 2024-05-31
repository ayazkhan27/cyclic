from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives.asymmetric import ec

def aes_security_bits(key_size):
    key = get_random_bytes(key_size // 8)  # key_size is in bits, convert to bytes
    cipher = AES.new(key, AES.MODE_EAX)
    plaintext = b'This is a test message'
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return key_size

def rsa_security_bits(key_size):
    key = RSA.generate(key_size)
    security_bits = key_size // 2
    return security_bits

def ecc_security_bits(curve):
    private_key = ec.generate_private_key(curve)
    if curve.name == 'secp256r1':
        security_bits = 128
    elif curve.name == 'secp384r1':
        security_bits = 192
    elif curve.name == 'secp521r1':
        security_bits = 256
    else:
        security_bits = 0
    return security_bits

# Test AES security bits
aes_128_security = aes_security_bits(128)
aes_192_security = aes_security_bits(192)
aes_256_security = aes_security_bits(256)

# Test RSA security bits
rsa_2048_security = rsa_security_bits(2048)
rsa_4096_security = rsa_security_bits(4096)

# Test ECC security bits
ecc_256_security = ecc_security_bits(ec.SECP256R1())
ecc_384_security = ecc_security_bits(ec.SECP384R1())
ecc_521_security = ecc_security_bits(ec.SECP521R1())

print(f"AES-128 Security Bits: {aes_128_security}")
print(f"AES-192 Security Bits: {aes_192_security}")
print(f"AES-256 Security Bits: {aes_256_security}")

print(f"RSA-2048 Security Bits: {rsa_2048_security}")
print(f"RSA-4096 Security Bits: {rsa_4096_security}")

print(f"ECC-256 Security Bits: {ecc_256_security}")
print(f"ECC-384 Security Bits: {ecc_384_security}")
print(f"ECC-521 Security Bits: {ecc_521_security}")
