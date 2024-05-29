import random
import string
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from decimal import Decimal

def calculate_entropy(ciphertext):
    total_chars = len(ciphertext)
    frequency_dict = {char: ciphertext.count(char) for char in set(ciphertext)}
    entropy = Decimal(0)
    for char, frequency in frequency_dict.items():
        probability = Decimal(frequency) / total_chars
        entropy -= probability * probability.log10()
    return entropy

def test_rsa_metrics():
    plaintext_length = 128
    
    # Generate RSA key pair
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    
    # Create RSA cipher objects
    rsa_cipher_public = PKCS1_OAEP.new(RSA.import_key(public_key))
    rsa_cipher_private = PKCS1_OAEP.new(RSA.import_key(private_key))
    
    # Generate random plaintext
    plaintext = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(plaintext_length))
    
    # Encrypt plaintext using RSA public key
    ciphertext = rsa_cipher_public.encrypt(plaintext.encode())
    
    # Print the ciphertext
    print("Ciphertext:", ciphertext.hex())
    
    # Test Avalanche Effect
    modified_plaintext = plaintext[:plaintext_length//2] + 'A' + plaintext[plaintext_length//2 + 1:]
    modified_ciphertext = rsa_cipher_public.encrypt(modified_plaintext.encode())
    avalanche_count = sum(c1 != c2 for c1, c2 in zip(ciphertext, modified_ciphertext))
    avalanche_ratio = avalanche_count / len(ciphertext)
    print("Avalanche Ratio:", avalanche_ratio)
    
    # Test Propagation of Changes
    modified_plaintext = 'A' * (plaintext_length // 2) + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(plaintext_length // 2))
    modified_ciphertext = rsa_cipher_public.encrypt(modified_plaintext.encode())
    propagation_count = sum(c1 != c2 for c1, c2 in zip(ciphertext, modified_ciphertext))
    propagation_ratio = propagation_count / len(ciphertext)
    print("Propagation Ratio:", propagation_ratio)
    
    # Perform Entropy Analysis (not applicable for RSA ciphertext as it's not text-based)
    # ...

if __name__ == "__main__":
    test_rsa_metrics()

input("Press Enter to exit...")

