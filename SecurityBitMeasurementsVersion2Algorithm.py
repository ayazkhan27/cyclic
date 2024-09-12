import random
import string
import time
import math
from sympy.ntheory import isprime, primitive_root, primerange

# Define the KHAN encryption and decryption functions
def is_full_reptend_prime(prime):
    """Check if a prime is a full reptend prime."""
    return isprime(prime) and primitive_root(prime) == 10

def generate_cyclic_sequence(prime, length):
    """Generate a cyclic sequence using the primitive root of a prime number."""
    if not is_full_reptend_prime(prime):
        raise ValueError(f"The prime {prime} is not a full reptend prime.")
    root = primitive_root(prime)
    cyclic_sequence = [(root ** i) % prime for i in range(1, length + 1)]
    if len(set(cyclic_sequence)) < length // 2:
        raise ValueError("The cyclic sequence did not generate enough diversity.")
    return cyclic_sequence

def khan_encrypt(plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length):
    """Encrypts plaintext using KHAN encryption method with a cyclic sequence."""
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    z_value = sum(1 for i in range(1, len(superposition_sequence)) if superposition_sequence[i] == superposition_sequence[i - 1])
    ciphertext = []
    for i, char in enumerate(plaintext):
        movement = cyclic_sequence[(start_position + i) % len(cyclic_sequence)]
        z_layer = (movement + z_value) % prime
        encrypted_value = ord(char) + z_layer
        ciphertext.append(encrypted_value)
    return ciphertext, superposition_sequence, z_value

def khan_decrypt(ciphertext, prime, cyclic_sequence, start_position, superposition_sequence, z_value):
    """Decrypts ciphertext using KHAN decryption method."""
    plaintext = []
    for i, value in enumerate(ciphertext):
        movement = cyclic_sequence[(start_position + i) % len(cyclic_sequence)]
        z_layer = (movement + z_value) % prime
        decrypted_value = value - z_layer
        plaintext.append(chr(decrypted_value))
    return ''.join(plaintext)

def calculate_entropy(ciphertext):
    """Calculate the entropy of the ciphertext."""
    total_chars = len(ciphertext)
    frequency_dict = {char: ciphertext.count(char) for char in set(ciphertext)}
    entropy = -sum(frequency / total_chars * math.log2(frequency / total_chars) for frequency in frequency_dict.values())
    return entropy

def calculate_keyspace(prime, superposition_sequence_length):
    """Calculate the keyspace size."""
    return prime * (2 ** superposition_sequence_length)

def calculate_security_bits(keyspace_size):
    """Calculate security bits based on keyspace size."""
    return math.log2(keyspace_size)

def test_khan_encryption():
    """Test the KHAN encryption algorithm."""
    # Choose a valid prime for generating a cyclic sequence
    full_reptend_primes = [p for p in primerange(100, 2000) if is_full_reptend_prime(p)]
    if not full_reptend_primes:
        raise ValueError("No full reptend primes found in the specified range.")
    
    prime = random.choice(full_reptend_primes)
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    
    plaintext = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
    
    start_position = random.randint(1, prime - 1)
    superposition_sequence_length = random.randint(5000, 10000)
    
    # Measure encryption time
    start_time = time.time()
    ciphertext, superposition_sequence, z_value = khan_encrypt(
        plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length)
    encryption_time = time.time() - start_time
    
    # Measure decryption time
    start_time = time.time()
    decrypted_text = khan_decrypt(ciphertext, prime, cyclic_sequence, start_position, superposition_sequence, z_value)
    decryption_time = time.time() - start_time
    
    # Calculate entropy
    entropy_value = calculate_entropy(ciphertext)
    
    # Calculate keyspace and security bits
    keyspace_size = calculate_keyspace(prime, superposition_sequence_length)
    security_bits = calculate_security_bits(keyspace_size)
    
    # Output results
    print(f"Original Plaintext: {plaintext}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Decrypted Text: {decrypted_text}")
    print(f"Encryption Time: {encryption_time:.4f} seconds")
    print(f"Decryption Time: {decryption_time:.4f} seconds")
    print(f"Entropy of Ciphertext: {entropy_value:.4f}")
    print(f"Keyspace Size: {keyspace_size}")
    print(f"Security Bits: {security_bits:.2f}")
    print(f"Decryption Successful: {'Success' if plaintext == decrypted_text else 'Failure'}")

if __name__ == "__main__":
    test_khan_encryption()
