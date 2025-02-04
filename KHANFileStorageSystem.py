# KHANFileStorageSystem.py

import os
import secrets
import string
import hashlib
from decimal import Decimal, getcontext
from tkinter import Tk, filedialog
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import json

# Your encryption algorithm functions

def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]

    min_movement = sequence_length

    for start_pos in start_positions:
        for target_pos in target_positions:
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length

            if clockwise_movement <= anticlockwise_movement:
                movement = clockwise_movement
            else:
                movement = -anticlockwise_movement

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
        digit_positions = {digit: [idx for idx, d in enumerate(cyclic_sequence) if d == digit] for digit in set(cyclic_sequence)}
    else:
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
    hashed = hashlib.sha256(f"{movement}{salt}".encode()).hexdigest()
    return (int(hashed, 16) % 10) + 1

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
    assert len(cipher_text) == len(z_layers), "Ciphertext and z_layers length mismatch"

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

# Asymmetric key encryption functions

def encrypt_symmetric_key(sym_key, recipient_public_key):
    """Encrypt the symmetric key using RSA public key."""
    encrypted_key = recipient_public_key.encrypt(
        sym_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_key

def decrypt_symmetric_key(encrypted_key, recipient_private_key):
    """Decrypt the symmetric key using RSA private key."""
    sym_key = recipient_private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return sym_key

# Update the encryption and decryption functions

def encrypt_file(file_path, recipient_public_key):
    """Encrypt the file using your encryption algorithm and secure key exchange."""
    # Read the file content
    with open(file_path, 'rb') as f:
        file_content = f.read()

    # Generate cryptographically secure random values
    symmetric_key = secrets.token_bytes(32)  # 256-bit key

    # Derive salt and IV from the symmetric key using a KDF or directly
    salt = secrets.token_hex(16)  # 16 bytes hex
    iv = secrets.token_hex(16)    # 16 bytes hex

    # Parameters for your encryption algorithm
    prime = 1051  # Use the same prime as before
    getcontext().prec = prime + 10
    cyclic_sequence = str(Decimal(1) / Decimal(prime))[2:]
    start_position = secrets.randbelow(len(cyclic_sequence))
    superposition_sequence_length = 100  # Adjust as needed

    # Now, encrypt the file content
    encryption_result = khan_encrypt(
        file_content,
        prime,
        cyclic_sequence,
        start_position,
        superposition_sequence_length,
        salt,
        iv
    )

    # Package sensitive parameters to be encrypted with the symmetric key
    sensitive_data = {
        'salt': salt,
        'iv': iv,
        'start_position': start_position,
        'prime': prime,
        'cyclic_sequence': cyclic_sequence,
        'superposition_sequence_length': superposition_sequence_length,
        'z_value': encryption_result['z_value'],
        'superposition_sequence': encryption_result['superposition_sequence'],
    }

    # Serialize and encrypt the sensitive data with the symmetric key
    sensitive_data_json = json.dumps(sensitive_data).encode('utf-8')

    # Encrypt sensitive data using symmetric key (AES encryption)
    nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
    cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    encrypted_sensitive_data = encryptor.update(sensitive_data_json) + encryptor.finalize()
    tag = encryptor.tag

    # Save the encrypted sensitive data to a file
    encrypted_file = file_path + '.enc'
    encrypted_sensitive_data_file = encrypted_file + '.sensitive'
    with open(encrypted_sensitive_data_file, 'wb') as f:
        f.write(encrypted_sensitive_data)

    # Encrypt the symmetric key using RSA
    encrypted_symmetric_key = encrypt_symmetric_key(symmetric_key, recipient_public_key)

    # Save the encrypted symmetric key to a file
    encrypted_key_file = file_path + '.key'
    with open(encrypted_key_file, 'wb') as f:
        f.write(encrypted_symmetric_key)

    # Save the encryption result without sensitive parameters
    encryption_output = {
        'ciphertext': encryption_result['ciphertext'],
        'z_layers': encryption_result['z_layers'],
        'tag': tag.hex(),
        'nonce': nonce.hex()
    }

    # Save encryption_output as JSON
    with open(encrypted_file, 'w') as f:
        json.dump(encryption_output, f)

    print(f"File encrypted and saved as {encrypted_file}")
    print(f"Encrypted symmetric key saved as {encrypted_key_file}")

def decrypt_file(encrypted_file_path, encrypted_key_file_path, recipient_private_key):
    """Decrypt the file using your encryption algorithm and secure key exchange."""
    # Read the encrypted symmetric key
    with open(encrypted_key_file_path, 'rb') as f:
        encrypted_symmetric_key = f.read()

    # Decrypt the symmetric key
    symmetric_key = decrypt_symmetric_key(encrypted_symmetric_key, recipient_private_key)

    # Read the encrypted file content
    with open(encrypted_file_path, 'r') as f:
        encryption_output = json.load(f)

    # Extract components
    ciphertext = encryption_output['ciphertext']
    z_layers = encryption_output['z_layers']
    tag = bytes.fromhex(encryption_output['tag'])
    nonce = bytes.fromhex(encryption_output['nonce'])

    # Read the encrypted sensitive data
    encrypted_sensitive_data_file = encrypted_file_path + '.sensitive'
    with open(encrypted_sensitive_data_file, 'rb') as f:
        encrypted_sensitive_data = f.read()

    # Decrypt the sensitive data
    cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    sensitive_data_json = decryptor.update(encrypted_sensitive_data) + decryptor.finalize()

    sensitive_data = json.loads(sensitive_data_json.decode('utf-8'))

    # Retrieve sensitive parameters
    salt = sensitive_data['salt']
    iv = sensitive_data['iv']
    start_position = sensitive_data['start_position']
    prime = sensitive_data['prime']
    cyclic_sequence = sensitive_data['cyclic_sequence']
    superposition_sequence_length = sensitive_data['superposition_sequence_length']
    z_value = sensitive_data['z_value']
    superposition_sequence = sensitive_data['superposition_sequence']

    # Generate movement_to_char mapping
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)

    # Reconstruct the encryption result
    encryption_result = {
        'ciphertext': ciphertext,
        'z_layers': z_layers,
        'z_value': z_value,
        'superposition_sequence': superposition_sequence,
        'salt': salt,
        'iv': iv,
        'prime': prime  # Include prime here
    }

    # Decrypt the file content
    plaintext_bytes = khan_decrypt(encryption_result, movement_to_char)

    # Save the decrypted file
    decrypted_file_path = encrypted_file_path.replace('.enc', '.dec')
    with open(decrypted_file_path, 'wb') as f:
        f.write(plaintext_bytes)

    print(f"File decrypted and saved as {decrypted_file_path}")

    return plaintext_bytes

def khan_encrypt(plaintext_bytes, prime, cyclic_sequence, start_position, superposition_sequence_length, salt, iv):
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    superposition_sequence = generate_superposition_sequence(superposition_sequence_length)
    z_value = calculate_z_value(superposition_sequence)

    # Combine IV and salt with the plaintext
    combined_bytes = iv.encode('utf-8') + salt.encode('utf-8') + plaintext_bytes
    ciphertext, z_layers = encrypt_message(combined_bytes, char_to_movement, z_value, superposition_sequence, salt, prime)
    assert len(ciphertext) == len(z_layers), "Ciphertext and z_layers length mismatch during encryption"

    # Return only the necessary data
    encryption_result = {
        'ciphertext': ciphertext,
        'z_layers': z_layers,
        'z_value': z_value,
        'superposition_sequence': superposition_sequence,
    }

    return encryption_result

def khan_decrypt(encryption_package, movement_to_char):
    ciphertext = encryption_package['ciphertext']
    z_layers = encryption_package['z_layers']
    iv = encryption_package['iv']
    salt = encryption_package['salt']
    z_value = encryption_package['z_value']
    superposition_sequence = encryption_package['superposition_sequence']
    prime = encryption_package['prime']  # Retrieve prime

    # Decrypt the message
    combined_bytes = decrypt_message(ciphertext, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime)
    plaintext_bytes = combined_bytes[len(iv) + len(salt):]
    return plaintext_bytes

# Main script execution

if __name__ == '__main__':
    # Assume that the recipient's public key is provided in 'public_key.pem'
    # and the recipient's private key is provided in 'private_key.pem'

    # Load the public key (sender's side)
    with open('public_key.pem', 'rb') as f:
        public_key_pem = f.read()
    recipient_public_key = serialization.load_pem_public_key(public_key_pem)

    # Select a file to encrypt
    print("Please select a file to encrypt.")
    Tk().withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename()

    if not file_path:
        print("No file selected.")
        exit()

    print(f"File selected: {file_path}")

    # Encrypt the file
    encrypt_file(file_path, recipient_public_key)

    # Simulate sending the encrypted files and keys to the recipient...

    # Recipient decrypts the file
    encrypted_file = file_path + '.enc'
    encrypted_key_file = file_path + '.key'

    # Load the private key (recipient's side)
    with open('private_key.pem', 'rb') as f:
        private_key_pem = f.read()
    recipient_private_key = serialization.load_pem_private_key(private_key_pem, password=None)

    decrypted_content = decrypt_file(encrypted_file, encrypted_key_file, recipient_private_key)

    # Verify that the decrypted content matches the original file content
    with open(file_path, 'rb') as f:
        original_content = f.read()

    if decrypted_content == original_content:
        print("Decryption successful. The decrypted content matches the original file.")
    else:
        print("Decryption failed. The decrypted content does not match the original file.")
