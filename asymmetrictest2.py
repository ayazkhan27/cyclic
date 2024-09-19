import random
import time
import sys
import math
from decimal import Decimal, getcontext
from collections import Counter
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# --- KHAN Encryption Functions ---

def generate_cyclic_sequence(prime):
    """Generate the true cyclic decimal sequence based on the prime."""
    length = prime - 1
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    if len(decimal_expansion) < length:
        decimal_expansion += '0' * (length - len(decimal_expansion))
    return decimal_expansion[:length]

def generate_target_sequences(prime, sequence):
    """Generate target sequences for analysis."""
    sequence_length = len(sequence)
    group_length = len(str(prime))
    cyclic_groups = []
    for i in range(sequence_length):
        group = sequence[i:i+group_length]
        if len(group) < group_length:
            group += sequence[:group_length - len(group)]
        cyclic_groups.append(group)
    return sorted(set(cyclic_groups))[:prime - 1]

def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
    """Calculate minimal movement between sequences."""
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]
    min_movement_value = None
    min_movements = []

    for start_pos in start_positions:
        for target_pos in target_positions:
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length
            current_min = min(clockwise_movement, anticlockwise_movement)

            if min_movement_value is None or current_min < min_movement_value:
                min_movement_value = current_min
                min_movements = []

            if current_min == min_movement_value:
                if clockwise_movement == anticlockwise_movement:
                    min_movements.extend([clockwise_movement, -anticlockwise_movement])
                else:
                    if clockwise_movement == current_min:
                        min_movements.append(clockwise_movement)
                    if anticlockwise_movement == current_min:
                        min_movements.append(-anticlockwise_movement)
    return min_movements

def analyze_cyclic_prime(prime, sequence, start_position):
    """Analyze cyclic primes to detect movements and superposition points."""
    sequence_length = len(sequence)
    digit_positions = {}
    shifted_sequence = sequence[start_position:] + sequence[:start_position]
    group_length = len(str(prime))

    for i in range(sequence_length):
        group = shifted_sequence[i:i+group_length]
        if len(group) < group_length:
            group += shifted_sequence[:group_length - len(group)]
        digit_positions.setdefault(group, []).append(i)

    target_sequences = generate_target_sequences(prime, shifted_sequence)
    movements = []
    superposition_points = []
    start_sequence = shifted_sequence[:group_length]

    for i, target_sequence in enumerate(target_sequences):
        min_movements = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)
        if len(set(map(abs, min_movements))) > 1:
            superposition_points.append(i)
            movements.append(min_movements[0])
        else:
            movements.append(min_movements[0])

    return movements, superposition_points

def generate_keypair(prime, cyclic_sequence):
    """Generate public and private keys."""
    start_position = random.randint(1, prime - 1)
    superposition_sequence_length = 100000  # Large value
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    public_key = (prime, cyclic_sequence)
    private_key = (start_position, superposition_sequence)
    return public_key, private_key

def encrypt(plaintext, public_key):
    """Encrypt using only the public key."""
    prime, sequence = public_key
    start_position = random.randint(1, prime - 1)
    movements, superposition_points = analyze_cyclic_prime(prime, sequence, start_position)
    ciphertext = []
    for char in plaintext:
        movement = movements[ord(char) % len(movements)]
        ciphertext.append(movement)
    return ciphertext, start_position, superposition_points

def decrypt(ciphertext, public_key, private_key, encryption_start_position, superposition_points):
    """Decrypt using the private key and public key."""
    prime, sequence = public_key
    start_position, superposition_sequence = private_key
    movements, _ = analyze_cyclic_prime(prime, sequence, encryption_start_position)
    movement_to_char = {m: chr(i % 256) for i, m in enumerate(movements)}
    plaintext = []
    superposition_index = 0
    for i, movement in enumerate(ciphertext):
        if i in superposition_points:
            direction = superposition_sequence[superposition_index % len(superposition_sequence)]
            movement *= direction
            superposition_index += 1
        char = movement_to_char.get(movement, '?')
        plaintext.append(char)
    return ''.join(plaintext)

# --- RSA Encryption Functions ---

def generate_rsa_keys(bits=64):
    """Generate RSA key pair."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    public_key = private_key.public_key()
    return public_key, private_key

def rsa_encrypt(plaintext, public_key):
    """Encrypt using RSA public key."""
    ciphertext = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return ciphertext

def rsa_decrypt(ciphertext, private_key):
    """Decrypt using RSA private key."""
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return plaintext.decode()

# --- Comparison Functions ---

def calculate_entropy(data):
    """Calculate entropy of data."""
    if isinstance(data, list):
        data = ''.join(map(str, data))
    frequency = Counter(data)
    data_len = len(data)
    entropy = -sum((freq / data_len) * math.log2(freq / data_len) for freq in frequency.values())
    return entropy

def measure_avalanche_effect(encrypt_func, plaintext1, plaintext2, *args):
    """Measure the avalanche effect."""
    ciphertext1, *_ = encrypt_func(plaintext1, *args)
    ciphertext2, *_ = encrypt_func(plaintext2, *args)
    bits1 = ''.join(format(abs(hash(x)), 'b') for x in ciphertext1)
    bits2 = ''.join(format(abs(hash(x)), 'b') for x in ciphertext2)
    max_len = max(len(bits1), len(bits2))
    bits1 = bits1.zfill(max_len)
    bits2 = bits2.zfill(max_len)
    differences = sum(b1 != b2 for b1, b2 in zip(bits1, bits2))
    avalanche = (differences / max_len) * 100
    return avalanche

def compare_algorithms():
    """Compare KHAN and RSA encryption algorithms."""
    message = "This is a test message for encryption algorithms comparison."
    message *= 5  # Ensure the message is long enough

    # --- KHAN Encryption ---
    print("=== KHAN Encryption ===")
    prime = 9643  # Larger full reptend prime
    print(f"Using full reptend prime: {prime}")
    cyclic_sequence = generate_cyclic_sequence(prime)

    # Generate keys
    public_key_khan, private_key_khan = generate_keypair(prime, cyclic_sequence)

    # Encrypt
    start_time = time.time()
    encrypted_msg_khan, temp_start, superposition_points = encrypt(message, public_key_khan)
    khan_encryption_time = time.time() - start_time

    # Decrypt
    start_time = time.time()
    decrypted_msg_khan = decrypt(encrypted_msg_khan, public_key_khan, private_key_khan, temp_start, superposition_points)
    khan_decryption_time = time.time() - start_time

    # Entropy
    khan_entropy = calculate_entropy(encrypted_msg_khan)

    # Avalanche Effect
    altered_message = message[:-1] + ('a' if message[-1] != 'a' else 'b')
    khan_avalanche = measure_avalanche_effect(encrypt, message, altered_message, public_key_khan)

    # Security Bits
    khan_security_bits = math.log2(prime)

    # Ciphertext Size
    khan_ciphertext_size = sys.getsizeof(encrypted_msg_khan)

    # Verify decryption
    khan_decryption_success = decrypted_msg_khan == message

    print(f"KHAN Encryption Time: {khan_encryption_time:.6f} seconds")
    print(f"KHAN Decryption Time: {khan_decryption_time:.6f} seconds")
    print(f"KHAN Ciphertext Entropy: {khan_entropy:.6f} bits per symbol")
    print(f"KHAN Avalanche Effect: {khan_avalanche:.2f}%")
    print(f"KHAN Security Bits: {khan_security_bits:.2f}")
    print(f"KHAN Ciphertext Size: {khan_ciphertext_size} bytes")
    print(f"KHAN Decryption Successful: {khan_decryption_success}")

    # --- RSA Encryption ---
    print("\n=== RSA Encryption ===")
    rsa_key_size = 64  # As per your request
    print(f"Using RSA key size: {rsa_key_size} bits.")

    # Generate keys
    rsa_public_key, rsa_private_key = generate_rsa_keys(bits=rsa_key_size)

    # Encrypt
    start_time = time.time()
    encrypted_msg_rsa = rsa_encrypt(message, rsa_public_key)
    rsa_encryption_time = time.time() - start_time

    # Decrypt
    start_time = time.time()
    decrypted_msg_rsa = rsa_decrypt(encrypted_msg_rsa, rsa_private_key)
    rsa_decryption_time = time.time() - start_time

    # Entropy
    rsa_entropy = calculate_entropy(encrypted_msg_rsa)

    # Avalanche Effect
    def rsa_measure_avalanche_effect(plaintext1, plaintext2, public_key):
        ciphertext1 = rsa_encrypt(plaintext1, public_key)
        ciphertext2 = rsa_encrypt(plaintext2, public_key)
        bits1 = ''.join(format(byte, '08b') for byte in ciphertext1)
        bits2 = ''.join(format(byte, '08b') for byte in ciphertext2)
        max_len = max(len(bits1), len(bits2))
        bits1 = bits1.zfill(max_len)
        bits2 = bits2.zfill(max_len)
        differences = sum(b1 != b2 for b1, b2 in zip(bits1, bits2))
        avalanche = (differences / max_len) * 100
        return avalanche

    rsa_avalanche = rsa_measure_avalanche_effect(message, altered_message, rsa_public_key)

    # Security Bits
    rsa_security_bits = rsa_key_size

    # Ciphertext Size
    rsa_ciphertext_size = sys.getsizeof(encrypted_msg_rsa)

    # Verify decryption
    rsa_decryption_success = decrypted_msg_rsa == message

    print(f"RSA Encryption Time: {rsa_encryption_time:.6f} seconds")
    print(f"RSA Decryption Time: {rsa_decryption_time:.6f} seconds")
    print(f"RSA Ciphertext Entropy: {rsa_entropy:.6f} bits per symbol")
    print(f"RSA Avalanche Effect: {rsa_avalanche:.2f}%")
    print(f"RSA Security Bits: {rsa_security_bits}")
    print(f"RSA Ciphertext Size: {rsa_ciphertext_size} bytes")
    print(f"RSA Decryption Successful: {rsa_decryption_success}")

    # --- Comparison ---
    print("\n=== Comparison Summary ===")
    print(f"Encryption Time - KHAN: {khan_encryption_time:.6f}s, RSA: {rsa_encryption_time:.6f}s")
    print(f"Decryption Time - KHAN: {khan_decryption_time:.6f}s, RSA: {rsa_decryption_time:.6f}s")
    print(f"Ciphertext Entropy - KHAN: {khan_entropy:.6f}, RSA: {rsa_entropy:.6f}")
    print(f"Avalanche Effect - KHAN: {khan_avalanche:.2f}%, RSA: {rsa_avalanche:.2f}%")
    print(f"Security Bits - KHAN: {khan_security_bits:.2f}, RSA: {rsa_security_bits}")
    print(f"Ciphertext Size - KHAN: {khan_ciphertext_size} bytes, RSA: {rsa_ciphertext_size} bytes")
    print(f"Decryption Successful - KHAN: {khan_decryption_success}, RSA: {rsa_decryption_success}")

if __name__ == "__main__":
    compare_algorithms()
