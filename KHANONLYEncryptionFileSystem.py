import secrets
import string
from hashlib import sha256
from decimal import Decimal, getcontext
import os

# Set precision for Decimal operations
getcontext().prec = 2000  # Adjust as needed for sufficient precision

def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]

    min_movement = sequence_length

    for start_pos in start_positions:
        for target_pos in target_positions:
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length

            movement = clockwise_movement if clockwise_movement <= anticlockwise_movement else -anticlockwise_movement

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
                wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
                cyclic_groups.append(wrap_around_group)

        cyclic_groups = sorted(set(cyclic_groups))
        return cyclic_groups[:prime - 1]

def analyze_cyclic_prime(prime, cyclic_sequence, start_position):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}

    cyclic_sequence = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]

    if prime < 10:
        digits = set(cyclic_sequence)
        for digit in digits:
            digit_positions[digit] = [idx for idx, d in enumerate(cyclic_sequence) if d == digit]
    else:
        group_length = len(str(prime))
        for i in range(sequence_length):
            group = cyclic_sequence[i:i+group_length]
            if len(group) < group_length:
                group += cyclic_sequence[:group_length - len(group)]
            if group in digit_positions:
                digit_positions[group].append(i)
            else:
                digit_positions[group] = [i]

    target_sequences = generate_target_sequences(prime, cyclic_sequence)

    movements = []
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)
        movements.append(movement)

    return movements

def generate_keys(prime, cyclic_sequence, start_position):
    movements = analyze_cyclic_prime(prime, cyclic_sequence, start_position)

    all_chars = ''.join(chr(i) for i in range(256))  # Include all possible byte values

    char_to_movement = {}
    movement_to_char = {}

    for i, char in enumerate(all_chars):
        movement = movements[i % len(movements)]
        char_to_movement[char] = movement
        movement_to_char[movement] = char

    # Ensure all possible movement values are covered
    for movement in range(-prime, prime):
        if movement not in movement_to_char:
            char = chr((movement + 256) % 256)
            movement_to_char[movement] = char
            char_to_movement[char] = movement

    return char_to_movement, movement_to_char

def generate_superposition_sequence(sequence_length):
    while True:
        left_right_sequence = [secrets.choice([-1, 1]) for _ in range(sequence_length)]
        if sum(left_right_sequence) == 0:
            return left_right_sequence

def calculate_z_value(superposition_sequence):
    return sum(1 for i in range(1, len(superposition_sequence)) if superposition_sequence[i] == superposition_sequence[i - 1])

def assign_z_layer(movement, salt):
    hashed = sha256(f"{movement}{salt}".encode()).hexdigest()
    return (int(hashed, 16) % 10) + 1

def khan_encrypt(plaintext_bytes, prime, cyclic_sequence, start_position, superposition_sequence_length):
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    superposition_sequence = generate_superposition_sequence(superposition_sequence_length)
    z_value = calculate_z_value(superposition_sequence)

    iv = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))  # Generate 8-byte IV
    salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))  # 8-byte salt

    # Combine IV and salt with the plaintext
    combined_bytes = iv.encode('utf-8') + salt.encode('utf-8') + plaintext_bytes
    ciphertext, z_layers = encrypt_message(combined_bytes, char_to_movement, z_value, superposition_sequence, salt, prime)

    return {
        'ciphertext': ciphertext,
        'char_to_movement': char_to_movement,
        'movement_to_char': movement_to_char,
        'z_value': z_value,
        'superposition_sequence': superposition_sequence,
        'iv': iv,
        'salt': salt,
        'z_layers': z_layers,
        'prime': prime,
        'start_position': start_position,
        'cyclic_sequence': cyclic_sequence
    }

def khan_decrypt(encryption_data):
    ciphertext = encryption_data['ciphertext']
    movement_to_char = encryption_data['movement_to_char']
    z_value = encryption_data['z_value']
    superposition_sequence = encryption_data['superposition_sequence']
    iv = encryption_data['iv']
    salt = encryption_data['salt']
    z_layers = encryption_data['z_layers']
    prime = encryption_data['prime']
    start_position = encryption_data['start_position']
    cyclic_sequence = encryption_data['cyclic_sequence']

    plaintext_bytes = decrypt_message(ciphertext, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime)

    # Remove IV and salt
    plaintext_bytes = plaintext_bytes[len(iv) + len(salt):]

    return plaintext_bytes

def encrypt_message(plaintext_bytes, char_to_movement, z_value, superposition_sequence, salt, prime):
    cipher_text = []
    z_layers = []
    superposition_sequence_copy = superposition_sequence.copy()
    for byte in plaintext_bytes:
        char = chr(byte)
        movement = char_to_movement.get(char, 0)  # Default to 0 if char not found
        z_layer = assign_z_layer(movement, salt)
        z_layers.append(z_layer)
        if abs(movement) == (prime - 1) // 2:
            movement = superposition_sequence_copy.pop(0)
            superposition_sequence_copy.append(-movement)
        cipher_text.append(movement * z_layer + z_value * prime)

    return cipher_text, z_layers

def decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime):
    plain_bytes = []
    superposition_sequence_copy = superposition_sequence.copy()
    for i, movement in enumerate(cipher_text):
        z_layer = z_layers[i]
        original_movement = (movement - z_value * prime) // z_layer
        if abs(original_movement) == (prime - 1) // 2:
            original_movement = superposition_sequence_copy.pop(0)
            superposition_sequence_copy.append(-original_movement)
        char = movement_to_char.get(original_movement, chr(original_movement % 256))  # Default to ASCII value if not found
        plain_bytes.append(ord(char))
    return bytes(plain_bytes)

# Functions to encrypt and decrypt files

def encrypt_file(input_file_path, output_file_path):
    # Read plaintext from file
    with open(input_file_path, 'rb') as f:
        plaintext_bytes = f.read()

    # Encryption parameters
    prime = 1051  # Example of a full reptend prime
    getcontext().prec = prime + 10  # Set precision for Decimal calculations
    cyclic_sequence = str(Decimal(1) / Decimal(prime))[2:]  # Remove '0.'
    start_position = secrets.randbelow(len(cyclic_sequence))
    superposition_sequence_length = 100  # Can be adjusted as needed

    # Encrypt the plaintext
    encryption_data = khan_encrypt(
        plaintext_bytes,
        prime,
        cyclic_sequence,
        start_position,
        superposition_sequence_length
    )

    # Save the encrypted data and necessary parameters to a file
    with open(output_file_path, 'w') as f:
        # Serialize the encryption_data dictionary securely
        import json

        # Remove non-serializable parts or sensitive data
        encryption_data_serializable = encryption_data.copy()
        encryption_data_serializable['char_to_movement'] = None  # Do not include in output
        encryption_data_serializable['movement_to_char'] = None  # Do not include in output

        # Save as JSON
        json.dump(encryption_data_serializable, f)

    # Save sensitive data separately (e.g., keys)
    with open(output_file_path + '.key', 'wb') as f:
        import pickle
        # Save the movement mappings securely
        pickle.dump({
            'char_to_movement': encryption_data['char_to_movement'],
            'movement_to_char': encryption_data['movement_to_char']
        }, f)

    print(f"File encrypted and saved as {output_file_path}")

def decrypt_file(encrypted_file_path, key_file_path, output_file_path):
    # Load the encrypted data and parameters from the file
    with open(encrypted_file_path, 'r') as f:
        import json
        encryption_data_serializable = json.load(f)

    with open(key_file_path, 'rb') as f:
        import pickle
        key_data = pickle.load(f)

    # Reconstruct the encryption_data dictionary
    encryption_data = encryption_data_serializable.copy()
    encryption_data['char_to_movement'] = key_data['char_to_movement']
    encryption_data['movement_to_char'] = key_data['movement_to_char']

    # Decrypt the ciphertext
    plaintext_bytes = khan_decrypt(encryption_data)

    # Save the decrypted plaintext to a file
    with open(output_file_path, 'wb') as f:
        f.write(plaintext_bytes)

    print(f"File decrypted and saved as {output_file_path}")

# Example usage
if __name__ == "__main__":
    # Paths to input and output files
    input_file = "plain_text.txt"
    encrypted_file = "encrypted_data.json"
    key_file = "encrypted_data.json.key"
    decrypted_file = "decrypted_text.txt"

    # Ensure the input file exists
    if not os.path.exists(input_file):
        # Create a sample plaintext file if it doesn't exist
        sample_text = "This is a sample text to demonstrate the encryption and decryption process using the custom encryption algorithm."
        with open(input_file, 'w') as f:
            f.write(sample_text)

    # Encrypt the file
    encrypt_file(input_file, encrypted_file)

    # Decrypt the file
    decrypt_file(encrypted_file, key_file, decrypted_file)

    # Verify that the decrypted file matches the original plaintext
    with open(input_file, 'rb') as f:
        original_plaintext = f.read()

    with open(decrypted_file, 'rb') as f:
        decrypted_plaintext = f.read()

    if original_plaintext == decrypted_plaintext:
        print("Success: Decrypted plaintext matches the original plaintext.")
    else:
        print("Error: Decrypted plaintext does not match the original plaintext.")
