import random
import string
import time
import math
from hashlib import sha256
from decimal import Decimal, getcontext

# ============================================================
# Utility Functions and Full Reptend Prime Handling
# ============================================================

def factorize(n):
    # Naive factorization for demonstration
    factors = []
    d = 2
    temp = n
    while d*d <= temp:
        while temp != 0 and temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors

def is_full_reptend_prime(p):
    # Check if 10 is a primitive root mod p (naive method)
    if p == 2 or p == 5:
        return False
    factors = factorize(p - 1)
    for factor in factors:
        if pow(10, (p - 1) // factor, p) == 1:
            return False
    return True

def get_cyclic_sequence_for_prime(p):
    # Compute the repeating decimal of 1/p
    # For demonstration purposes only.
    getcontext().prec = p + 10
    frac = Decimal(1) / Decimal(p)
    frac_str = str(frac)[2:]  # remove "0."
    return frac_str[:p-1]

def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]
    min_movement = sequence_length

    for start_pos in start_positions:
        for target_pos in target_positions:
            cw = (target_pos - start_pos) % sequence_length
            ccw = (start_pos - target_pos) % sequence_length
            movement = cw if cw <= ccw else -ccw
            if abs(movement) < abs(min_movement):
                min_movement = movement
    return min_movement

def generate_target_sequences(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    group_length = len(str(prime))
    if prime < 10:
        return sorted(set(cyclic_sequence))
    else:
        cyclic_groups = []
        for i in range(sequence_length):
            group = cyclic_sequence[i:i+group_length]
            if len(group) == group_length:
                cyclic_groups.append(group)
            else:
                wrap_around = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
                cyclic_groups.append(wrap_around)
        cyclic_groups = sorted(set(cyclic_groups))
        return cyclic_groups[:prime - 1]

def analyze_cyclic_prime(prime, cyclic_sequence, start_position):
    sequence_length = len(cyclic_sequence)
    # Rotate the sequence
    rotated_seq = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]

    digit_positions = {}
    if prime < 10:
        # Single digit mapping
        for idx, d in enumerate(rotated_seq):
            digit_positions.setdefault(d, []).append(idx)
    else:
        group_length = len(str(prime))
        for i in range(sequence_length):
            group = rotated_seq[i:i+group_length]
            if len(group) == group_length:
                digit_positions.setdefault(group, []).append(i)
            else:
                wrap_around = rotated_seq[i:] + rotated_seq[:group_length - len(group)]
                digit_positions.setdefault(wrap_around, []).append(i)
    
    target_sequences = generate_target_sequences(prime, rotated_seq)
    movements = []
    start_sequence = rotated_seq[:len(target_sequences[0])]
    for target in target_sequences:
        m = minimal_movement(start_sequence, target, digit_positions, sequence_length)
        movements.append(m)
    return movements

def generate_keys(prime, cyclic_sequence, start_position):
    movements = analyze_cyclic_prime(prime, cyclic_sequence, start_position)
    all_chars = ''.join(chr(i) for i in range(256))
    char_to_movement = {}
    movement_to_char = {}

    for i, char in enumerate(all_chars):
        movement = movements[i % len(movements)]
        char_to_movement[char] = movement
        movement_to_char[movement] = char

    # Ensure coverage for all movement values
    for movement in range(-prime, prime):
        if movement not in movement_to_char:
            char = chr((movement + 256) % 256)
            movement_to_char[movement] = char
            char_to_movement[char] = movement
    return char_to_movement, movement_to_char

def generate_superposition_sequence(sequence_length):
    while True:
        seq = [random.choice([-1, 1]) for _ in range(sequence_length)]
        if sum(seq) == 0:
            return seq

def calculate_z_value(superposition_sequence):
    return sum(1 for i in range(1, len(superposition_sequence)) if superposition_sequence[i] == superposition_sequence[i-1])

def assign_z_layer(movement, salt):
    h = sha256(f"{movement}{salt}".encode()).hexdigest()
    return (int(h, 16) % 10) + 1

# ============================================================
# Diffie-Hellman-like Key Setup
# ============================================================

def dh_keygen(prime):
    g = 10
    x = random.randint(2, prime-2)
    h = pow(g, x, prime)
    return (prime, g, h), x

def dh_compute_shared_secret(prime, g, h, x, other_component):
    return pow(other_component, x, prime)

# ============================================================
# Key Derivation and Block Operations
# ============================================================

def key_derivation(prime, K):
    hashed = sha256(str(K).encode()).digest()
    return int.from_bytes(hashed, 'big') % (prime - 1)

def encrypt_block(block, char_to_movement, z_value, superposition_sequence, salt, prime):
    cipher_ints = []
    z_layers = []
    sseq_copy = superposition_sequence.copy()
    for char in block:
        movement = char_to_movement.get(char, 0)
        z_layer = assign_z_layer(movement, salt)
        z_layers.append(z_layer)
        if abs(movement) == (prime - 1)//2:
            movement = sseq_copy.pop(0)
            sseq_copy.append(-movement)
        cipher_val = movement * z_layer + z_value * prime
        cipher_ints.append(cipher_val)
    return cipher_ints, z_layers

def decrypt_block(cipher_ints, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime):
    plain_chars = []
    sseq_copy = superposition_sequence.copy()
    for i, val in enumerate(cipher_ints):
        z_layer = z_layers[i]
        original_movement = (val - z_value * prime) // z_layer
        if abs(original_movement) == (prime - 1)//2:
            original_movement = sseq_copy.pop(0)
            sseq_copy.append(-original_movement)
        char = movement_to_char.get(original_movement, chr(original_movement % 256))
        plain_chars.append(char)
    return ''.join(plain_chars)

def pad(plaintext, block_size=16):
    pad_len = block_size - (len(plaintext) % block_size)
    return plaintext + chr(pad_len)*pad_len

def unpad(plaintext):
    pad_len = ord(plaintext[-1])
    return plaintext[:-pad_len]

def encrypt_message(plaintext, prime, cyclic_sequence, start_position, salt):
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    superposition_sequence = generate_superposition_sequence((prime - 1)//2)
    z_value = calculate_z_value(superposition_sequence)

    block_size = 16
    plaintext = pad(plaintext, block_size)
    ciphertext_ints = []
    z_layers_all = []

    # Simple ECB mode
    for i in range(0, len(plaintext), block_size):
        block = plaintext[i:i+block_size]
        cipher_block, z_layers = encrypt_block(block, char_to_movement, z_value, superposition_sequence, salt, prime)
        ciphertext_ints.extend(cipher_block)
        z_layers_all.extend(z_layers)
    return ciphertext_ints, z_layers_all, z_value, superposition_sequence, char_to_movement, movement_to_char

def decrypt_message(ciphertext_ints, prime, cyclic_sequence, start_position, salt, z_value, superposition_sequence, movement_to_char, z_layers_all):
    # Keys are regenerated to ensure consistency
    # In a real system, ensure all parameters are the same as during encryption.
    _, movement_to_char_check = generate_keys(prime, cyclic_sequence, start_position)

    block_size = 16
    plaintext_pieces = []
    for i in range(0, len(ciphertext_ints), block_size):
        block_ints = ciphertext_ints[i:i+block_size]
        z_layers = z_layers_all[i:i+block_size]
        plain_block = decrypt_block(block_ints, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime)
        plaintext_pieces.append(plain_block)
    plaintext = ''.join(plaintext_pieces)
    return unpad(plaintext)

# ============================================================
# Entropy and Security Estimation
# ============================================================

def shannon_entropy(data):
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def estimate_security_bits(prime):
    return math.log2(prime)

# ============================================================
# Main Demonstration
# ============================================================

if __name__ == "__main__":
    # For demonstration, let's pick a smaller prime known to be full reptend, e.g. 17
    prime = 337
    if not is_full_reptend_prime(prime):
        raise ValueError("Not a full reptend prime. Choose another prime.")

    cyclic_sequence = get_cyclic_sequence_for_prime(prime)

    # Diffie-Hellman-like key setup
    (p, g, h), x = dh_keygen(prime)
    y = random.randint(2, p-2)
    other_component = pow(g, y, p)
    K_enc = pow(h, y, p)
    K_dec = dh_compute_shared_secret(p, g, h, x, other_component)
    assert K_enc == K_dec, "Key exchange failed!"

    # Derive start position
    start_position = key_derivation(p, K_enc)

    # Salt for layering
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

    # Encrypt
    plaintext = "Hello, this is a secret message!"
    start_enc = time.perf_counter()
    ciphertext_ints, z_layers, z_value, superposition_sequence, c2m, m2c = encrypt_message(plaintext, p, cyclic_sequence, start_position, salt)
    end_enc = time.perf_counter()

    # Decrypt
    start_dec = time.perf_counter()
    decrypted = decrypt_message(ciphertext_ints, p, cyclic_sequence, start_position, salt, z_value, superposition_sequence, m2c, z_layers)
    end_dec = time.perf_counter()

    # Verify correctness
    assert decrypted == plaintext, "Decryption failed!"

    # Timing and entropy
    enc_time = end_enc - start_enc
    dec_time = end_dec - start_dec

    # Basic entropy measurement
    ciphertext_bytes = bytes([val % 256 for val in ciphertext_ints])
    entropy = shannon_entropy(ciphertext_bytes)
    sec_bits = estimate_security_bits(p)

    print("Encryption-Decryption successful!")
    print(f"Plaintext: {plaintext}")
    print(f"Ciphertext (ints): {ciphertext_ints[:20]}...")
    print(f"Decrypted: {decrypted}")
    print(f"Encryption time: {enc_time:.6f} s")
    print(f"Decryption time: {dec_time:.6f} s")
    print(f"Ciphertext entropy: {entropy:.2f} bits/byte")
    print(f"Estimated security bits (based on prime size): {sec_bits:.2f} bits")
