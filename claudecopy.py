def generate_cyclic_sequence(p):
    """
    Generate the cyclic sequence S for a given full reptend prime p.
    """
    seq = []
    x = 1
    for _ in range(p - 1):
        x = (x * 10) % p
        seq.append(x)
    return seq

def calculate_minimal_movements(seq):
    """
    Calculate the minimal movements M for target sequences derived from the cyclic sequence.
    """
    n = len(seq)
    movements = {}
    for i in range(n):
        movements[(seq[i], 0)] = i  # Add movement for (char, 0)
        for j in range(i + 1, n):
            a, b = seq[i], seq[j]
            movement = min((b - a) % n, (a - b) % n)
            movements[(a, b)] = movement
    return movements

def generate_superposition_sequence(p, length):
    """
    Generate a superposition sequence with movements summing to zero.
    """
    seq = []
    total_sum = 0
    for _ in range(length):
        movement = 1 if total_sum < (p - 1) // 2 else -1
        seq.append(movement)
        total_sum = (total_sum + movement) % (p - 1)
    return seq

def calculate_z_value(seq):
    """
    Calculate the Z-value based on consecutive identical directions in the superposition sequence.
    """
    z = 0
    count = 1
    for i in range(1, len(seq)):
        if seq[i] == seq[i - 1]:
            count += 1
        else:
            z = max(z, count)
            count = 1
    z = max(z, count)
    return z

def generate_keys(p, movements, starting_position):
    """
    Generate the encryption and decryption keys based on the cyclic sequence and minimal movements.
    """
    phi = {}
    phi_inv = {}
    for char in range(256):
        movement = movements[(char, 0)]
        movement = (movement + starting_position) % (p - 1)
        phi[char] = movement
        phi_inv[movement] = char
    return phi, phi_inv

def encrypt(plaintext, p, phi, z_value, starting_position):
    """
    Encrypt the plaintext using the KHAN encryption algorithm.
    """
    ciphertext = []
    for char in plaintext:
        movement = phi[char]
        encrypted_movement = (movement + z_value * p + starting_position) % (p - 1)
        ciphertext.append(encrypted_movement)
    return ciphertext

def decrypt(ciphertext, p, phi_inv, z_value, starting_position):
    """
    Decrypt the ciphertext using the KHAN encryption algorithm.
    """
    plaintext = []
    for movement in ciphertext:
        decrypted_movement = (movement - z_value * p - starting_position) % (p - 1)
        char = phi_inv[decrypted_movement]
        plaintext.append(char)
    return bytes(plaintext)

# Choose a full reptend prime p
p = 137

# Generate the cyclic sequence
cyclic_sequence = generate_cyclic_sequence(p)

# Calculate the minimal movements
movements = calculate_minimal_movements(cyclic_sequence)

# Generate the superposition sequence (length must be even)
superposition_sequence = generate_superposition_sequence(p, 8)

# Calculate the Z-value
z_value = calculate_z_value(superposition_sequence)

# Choose a starting position for the dial
starting_position = 42

# Generate the encryption and decryption keys
phi, phi_inv = generate_keys(p, movements, starting_position)

# Sample plaintext
plaintext = b"This is a secret message."

# Encrypt the plaintext
ciphertext = encrypt(plaintext, p, phi, z_value, starting_position)
print("Ciphertext:", ciphertext)

# Decrypt the ciphertext
decrypted_plaintext = decrypt(ciphertext, p, phi_inv, z_value, starting_position)
print("Decrypted plaintext:", decrypted_plaintext)
