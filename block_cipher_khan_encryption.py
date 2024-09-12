import random
import string
from Crypto.Util.Padding import pad, unpad

BLOCK_SIZE = 16  # Block size for the cipher (128 bits, or 16 characters)

# Generates a random plaintext for testing purposes
def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# Generates minimal movement between sequences
def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]

    min_movement = sequence_length
    for start_pos in start_positions:
        for target_pos in target_positions:
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length
            movement = min(clockwise_movement, -anticlockwise_movement)
            if abs(movement) < abs(min_movement):
                min_movement = movement
    return min_movement

# Generates the target sequence from the reptend prime's decimal expansion
def generate_target_sequences(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    group_length = len(str(prime))

    cyclic_groups = []
    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) == group_length:
            cyclic_groups.append(group)
        else:
            wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
            cyclic_groups.append(wrap_around_group)
    
    cyclic_groups = sorted(set(cyclic_groups))
    return cyclic_groups[:prime - 1]

# Analyze cyclic prime and generate movement patterns
def analyze_cyclic_prime(prime, cyclic_sequence, start_position):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}

    cyclic_sequence = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]
    group_length = len(str(prime))

    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) == group_length:
            if group in digit_positions:
                digit_positions[group].append(i)
            else:
                digit_positions[group] = [i]
        else:
            wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
            if wrap_around_group in digit_positions:
                digit_positions[wrap_around_group].append(i)
            else:
                digit_positions[wrap_around_group] = [i]

    target_sequences = generate_target_sequences(prime, cyclic_sequence)

    movements = []
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)
        movements.append(movement)
    
    return movements

# Generates keys based on the prime and cyclic sequence
def generate_keys(prime, cyclic_sequence, start_position):
    movements = analyze_cyclic_prime(prime, cyclic_sequence, start_position)
    all_chars = ''.join(chr(i) for i in range(256))  # Include all possible byte values
    
    char_to_movement = {}
    movement_to_char = {}
    used_movements = set()

    for i, char in enumerate(all_chars):
        if i < len(movements):
            movement = movements[i]
        else:
            movement = (i - len(movements)) * prime
        if movement not in used_movements:
            char_to_movement[char] = movement
            movement_to_char[movement] = char
            used_movements.add(movement)
    
    # Ensure all characters are mapped
    missing_chars = set(all_chars) - set(char_to_movement.keys())
    if missing_chars:
        raise ValueError(f"Missing mappings for characters: {missing_chars}")
    
    return char_to_movement, movement_to_char


# Generates superposition sequence (used in encryption for randomness)
def generate_superposition_sequence(sequence_length):
    while True:
        left_right_sequence = [random.choice([-1, 1]) for _ in range(sequence_length)]
        if sum(left_right_sequence) == 0:
            return left_right_sequence

# Computes the Z value based on the superposition sequence
def calculate_z_value(superposition_sequence):
    return sum(1 for i in range(1, len(superposition_sequence)) if superposition_sequence[i] == superposition_sequence[i - 1])

# Assigns Z-layer values for extra complexity in encryption
def assign_z_layer(movement):
    return (abs(movement) % 10) + 1

# Khan block encryption function (asymmetric public key encryption)
def khan_block_encrypt(plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length):
    # Generate encryption keys (public: prime, cyclic sequence; private: start_position, superposition_sequence_length)
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    superposition_sequence = generate_superposition_sequence(superposition_sequence_length)
    z_value = calculate_z_value(superposition_sequence)

    # Pad the plaintext to fit block size
    padded_plaintext = pad(plaintext.encode('utf-8'), BLOCK_SIZE)


    # Encrypt the padded plaintext block by block
    ciphertext, z_layers = encrypt_message(padded_plaintext.decode('latin-1'), char_to_movement, z_value, superposition_sequence, prime)
    return ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, z_layers

# Encrypt message in block mode
def encrypt_message(plaintext, char_to_movement, z_value, superposition_sequence, prime):
    cipher_text = []
    z_layers = []
    superposition_sequence_copy = superposition_sequence.copy()

    for char in plaintext:
        movement = char_to_movement.get(char, None)
        if movement is not None:
            z_layer = assign_z_layer(movement)
            z_layers.append(z_layer)
            if abs(movement) == (prime - 1) // 2:
                movement = superposition_sequence_copy.pop(0)
                superposition_sequence_copy.append(-movement)
            cipher_text.append(movement * z_layer + z_value * prime)
        else:
            raise ValueError(f"Character {char} not in dictionary")
    
    return cipher_text, z_layers

# Decrypt a block of ciphertext
def khan_block_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, z_layers, prime, start_position, cyclic_sequence):
    # Adjust cyclic sequence
    cyclic_sequence = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]

    # Decrypt the message
    plaintext = decrypt_message(ciphertext, movement_to_char, z_value, superposition_sequence, z_layers, prime)
    return plaintext

# Decrypt message in block mode
def decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence, z_layers, prime):
    plain_text = []
    superposition_sequence_copy = superposition_sequence.copy()

    for i, movement in enumerate(cipher_text):
        z_layer = z_layers[i]
        original_movement = (movement - z_value * prime) // z_layer
        if abs(original_movement) == (prime - 1) // 2:
            original_movement = superposition_sequence_copy.pop(0)
            superposition_sequence_copy.append(-original_movement)
        char = movement_to_char.get(original_movement, None)
        if char is not None:
            plain_text.append(char)
        else:
            raise ValueError(f"Movement {original_movement} not in dictionary")
    
    # Unpad the plaintext
    padded_plaintext = ''.join(plain_text)
    return unpad(padded_plaintext.encode('utf-8'), BLOCK_SIZE).decode('utf-8')


# Test the block encryption and decryption system
def test_khan_block_cipher():
    prime = 1051  # Public key (reptend prime)
    start_position = random.randint(1, prime - 1)  # Private key
    superposition_sequence_length = random.randint(200, 1000) * 2  # Private key

    # Generate a cyclic sequence (public key)
    cyclic_sequence = ''.join(random.choice(string.digits) for _ in range(prime - 1))

    plaintext = "This is a test message for KHAN block cipher encryption!"
    print(f"Original plaintext: {plaintext}")

    # Encrypt the plaintext
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, z_layers = khan_block_encrypt(
        plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length
    )
    print(f"Ciphertext: {ciphertext}")

    # Decrypt the ciphertext
    decrypted_text = khan_block_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, z_layers, prime, start_position, cyclic_sequence)
    print(f"Decrypted plaintext: {decrypted_text}")

    assert plaintext == decrypted_text, "Decryption failed: plaintext does not match"
    print("Encryption and decryption successful!")

if __name__ == "__main__":
    test_khan_block_cipher()
