import random
import string
from sympy.ntheory import isprime, primitive_root, primerange

# Helper function to check if a prime is a full reptend prime
def is_full_reptend_prime(prime):
    """
    Check if the given prime is a full reptend prime.
    A full reptend prime has a maximal-length decimal expansion when 1 is divided by the prime.
    """
    # Full reptend prime if the smallest primitive root of the prime is 10
    return isprime(prime) and primitive_root(prime) == 10

# Function to generate a cyclic sequence using a prime and its primitive root
def generate_cyclic_sequence(prime, length):
    """
    Generate a cyclic sequence using the primitive root of a prime number.
    Primitive roots guarantee full-length cyclic behavior under modulo.
    """
    if not is_full_reptend_prime(prime):
        raise ValueError(f"The prime {prime} is not a full reptend prime.")
    
    # Generate sequence using the primitive root
    root = primitive_root(prime)
    cyclic_sequence = [(root ** i) % prime for i in range(1, length + 1)]
    
    # Ensure diversity in the sequence (at least 50% unique elements)
    if len(set(cyclic_sequence)) < length // 2:
        raise ValueError("The cyclic sequence did not generate enough diversity.")
    
    return cyclic_sequence

# Encryption function
def khan_encrypt(plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length):
    """
    Encrypts a plaintext using the KHAN encryption method with a cyclic sequence.
    """
    # Generate the superposition sequence, which must be a series of -1 and 1
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    
    # Calculate Z-value based on superposition sequence
    z_value = sum(1 for i in range(1, len(superposition_sequence)) if superposition_sequence[i] == superposition_sequence[i - 1])
    
    # Initialize encryption
    ciphertext = []
    
    for i, char in enumerate(plaintext):
        # Map each character to a movement in the cyclic sequence
        movement = cyclic_sequence[(start_position + i) % len(cyclic_sequence)]
        z_layer = (movement + z_value) % prime
        encrypted_value = ord(char) + z_layer  # Encrypt the character using the z-layer and cyclic movement
        ciphertext.append(encrypted_value)
    
    return ciphertext, superposition_sequence, z_value

# Decryption function
def khan_decrypt(ciphertext, prime, cyclic_sequence, start_position, superposition_sequence, z_value):
    """
    Decrypts the ciphertext using the KHAN decryption method.
    """
    plaintext = []
    
    for i, value in enumerate(ciphertext):
        # Reverse the z-layer calculation
        movement = cyclic_sequence[(start_position + i) % len(cyclic_sequence)]
        z_layer = (movement + z_value) % prime
        decrypted_value = value - z_layer  # Decrypt the value by reversing z-layer
        plaintext.append(chr(decrypted_value))
    
    return ''.join(plaintext)

# Key generation and testing function
def test_khan_encryption():
    """
    Test the KHAN encryption algorithm by generating a cyclic sequence, encrypting a plaintext, and then decrypting it.
    """
    # Choose a valid prime for generating a cyclic sequence
    full_reptend_primes = [p for p in primerange(1000, 20000) if is_full_reptend_prime(p)]
    if not full_reptend_primes:
        raise ValueError("No full reptend primes found in the specified range.")
    
    prime = random.choice(full_reptend_primes)
    
    # Generate a cyclic sequence from the prime
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    
    # Example plaintext
    plaintext = "This is a test message for KHAN encryption."
    
    # Parameters for encryption
    start_position = random.randint(1, prime - 1)
    superposition_sequence_length = random.randint(5000, 10000)  # Ensure a reasonable length
    
    # Encrypt the message
    ciphertext, superposition_sequence, z_value = khan_encrypt(plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length)
    
    # Decrypt the message
    decrypted_text = khan_decrypt(ciphertext, prime, cyclic_sequence, start_position, superposition_sequence, z_value)
    
    # Output results
    print(f"Original Plaintext: {plaintext}")
    print(f"Decrypted Text: {decrypted_text}")
    print(f"Encryption Success: {'Success' if plaintext == decrypted_text else 'Failure'}")

if __name__ == "__main__":
    test_khan_encryption()
