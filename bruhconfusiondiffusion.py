import random
import string
from decimal import Decimal, getcontext
import math
import khan_encryption

def generate_cyclic_sequence(prime, length):
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  
    return decimal_expansion[:length]

def calculate_entropy(ciphertext):
    total_chars = len(ciphertext)
    frequency_dict = {char: ciphertext.count(char) for char in set(ciphertext)}
    entropy = Decimal(0)
    for char, frequency in frequency_dict.items():
        probability = Decimal(frequency) / total_chars
        # Using log base 2 for Shannon entropy
        entropy -= probability * Decimal(math.log2(probability))
    return entropy

def test_confusion_and_diffusion():
    prime = 32779  # Example prime number
    sequence_length = 2742  # Example sequence length
    plaintext_length = 128
    
    # Generate a cyclic sequence for testing
    cyclic_sequence = generate_cyclic_sequence(prime, sequence_length)
    
    # Generate random plaintext
    plaintext = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(plaintext_length))
    
    # Encrypt plaintext using Khan Encryption
    start_position = random.randint(0, sequence_length - 1)
    ciphertext, _, _, _, _, _, _, _ = khan_encryption.khan_encrypt(plaintext, prime, cyclic_sequence, start_position)
    
    # Print the ciphertext
    print("Ciphertext:", ''.join(map(str, ciphertext)))
    
    # Test Avalanche Effect
    modified_plaintext = plaintext[:plaintext_length//2] + 'A' + plaintext[plaintext_length//2 + 1:]
    modified_ciphertext, _, _, _, _, _, _, _ = khan_encryption.khan_encrypt(modified_plaintext, prime, cyclic_sequence, start_position)
    avalanche_count = sum(c1 != c2 for c1, c2 in zip(ciphertext, modified_ciphertext))
    avalanche_ratio = avalanche_count / len(ciphertext)
    print("Avalanche Ratio:", avalanche_ratio)
    
    # Test Propagation of Changes
    modified_plaintext = 'A' * (plaintext_length // 2) + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(plaintext_length // 2))
    modified_ciphertext, _, _, _, _, _, _, _ = khan_encryption.khan_encrypt(modified_plaintext, prime, cyclic_sequence, start_position)
    propagation_count = sum(c1 != c2 for c1, c2 in zip(ciphertext, modified_ciphertext))
    propagation_ratio = propagation_count / len(ciphertext)
    print("Propagation Ratio:", propagation_ratio)
    
    # Test Statistical Analysis
    ciphertext_distribution = {char: ciphertext.count(char) for char in set(ciphertext)}
    print("Ciphertext Distribution:", ciphertext_distribution)
    
    # Perform Entropy Analysis
    entropy = calculate_entropy(ciphertext)
    print("Entropy:", entropy)
    
    # Test Cryptanalysis (not implemented for this demonstration)
    # ...

if __name__ == "__main__":
    test_confusion_and_diffusion()

input("Press Enter to exit...")
