KHAN Encryption Algorithm

KHAN (Keyed Hashing and Asymmetric Nonce) encryption is an innovative cryptographic algorithm designed to provide robust security through the use of cyclic prime number sequences. This README provides an overview of the KHAN encryption algorithm, its implementation, usage, and performance comparison with other popular encryption methods like RSA and AES.
Table of Contents

    Introduction
    Features
    Installation
    Usage
        Encryption and Decryption
        Performance Comparison
    Implementation Details
    License

Introduction

KHAN encryption leverages cyclic prime sequences to create a secure and efficient encryption system. By combining the unique properties of prime numbers and advanced encryption techniques, KHAN aims to provide enhanced security for sensitive data transmission.

Features

    Utilizes cyclic prime sequences for encryption and decryption.
    Supports all printable ASCII characters.
    Provides robust security through unique mapping of characters to movements.
    Offers performance comparison with RSA and AES encryption methods.

Installation

To use the KHAN encryption algorithm, you need to install the required Python packages. You can do this using the following command: pip install pycryptodome

Usage
Encryption and Decryption

Here's a basic example of how to use the KHAN encryption algorithm for encrypting and decrypting a message: 
import time
import random
import string
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Function to generate random plaintext of a given length
def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# Function to measure encryption and decryption time for Khan encryption
def measure_khan_encryption(khan_encrypt, khan_decrypt, plaintext):
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence = khan_encrypt(plaintext)
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_text = khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, decrypted_text

# Function to measure encryption and decryption time for RSA
def measure_rsa_encryption(plaintext):
    key = RSA.generate(2048)
    cipher_rsa = PKCS1_OAEP.new(key)
    
    start_time = time.time()
    ciphertext = cipher_rsa.encrypt(plaintext.encode())
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_text = cipher_rsa.decrypt(ciphertext).decode()
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, decrypted_text

# Function to measure encryption and decryption time for AES
def measure_aes_encryption(plaintext):
    key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)).encode()
    cipher_aes = AES.new(key, AES.MODE_CBC)
    iv = cipher_aes.iv

    start_time = time.time()
    ciphertext = cipher_aes.encrypt(pad(plaintext.encode(), AES.block_size))
    encryption_time = time.time() - start_time

    start_time = time.time()
    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
    decrypted_text = unpad(cipher_aes.decrypt(ciphertext), AES.block_size).decode()
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, decrypted_text

def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]

    min_movement = sequence_length  # Initialize with a value larger than any possible movement

    for start_pos in start_positions:
        for target_pos in target_positions:
            # Calculate clockwise and anticlockwise movements
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length
            
            # Find the minimal movement
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
            else:  # Wrap-around case
                wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
                cyclic_groups.append(wrap_around_group)
        
        cyclic_groups = sorted(set(cyclic_groups))
        return cyclic_groups[:prime - 1]

def analyze_cyclic_prime(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    
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
            else:  # Wrap-around case
                wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
                if wrap_around_group in digit_positions:
                    digit_positions[wrap_around_group].append(i)
                else:
                    digit_positions[wrap_around_group] = [i]
    
    target_sequences = generate_target_sequences(prime, cyclic_sequence)

    movements = []
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence)
        movements.append(movement)
    
    return movements

def generate_keys(prime, cyclic_sequence):
    movements = analyze_cyclic_prime(prime, cyclic_sequence)
    all_chars = ''.join(chr(i) for i in range(32, 127))  # Printable ASCII characters
    if len(movements) < len(all_chars):
        raise ValueError("Not enough unique movements to map all characters.")
    
    char_to_movement = {}
    movement_to_char = {}
    used_movements = set()
    
    for i, char in enumerate(all_chars):
        movement = movements[i]
        if movement in used_movements:
            # Find the next available unique movement
            for j in range(len(movements)):
                if movements[j] not in used_movements:
                    movement = movements[j]
                    break
        char_to_movement[char] = movement
        movement_to_char[movement] = char
        used_movements.add(movement)

    return char_to_movement, movement_to_char

def generate_superposition_sequence(prime):
    sequence_length = prime - 1
    while True:
        left_right_sequence = [random.choice([-1, 1]) for _ in range(sequence_length)]
        if sum(left_right_sequence) == 0:
            return left_right_sequence

def calculate_z_value(superposition_sequence):
    return sum(1 for i in range(1, len(superposition_sequence)) if superposition_sequence[i] == superposition_sequence[i - 1])

def khan_encrypt(plaintext):
    char_to_movement, movement_to_char = generate_keys(cyclic_prime, cyclic_sequence)
    superposition_sequence = generate_superposition_sequence(cyclic_prime)
    z_value = calculate_z_value(superposition_sequence)
    ciphertext = encrypt_message(plaintext, char_to_movement, z_value, superposition_sequence)
    return ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence

def khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence):
    return decrypt_message(ciphertext, movement_to_char, z_value, superposition_sequence)

def encrypt_message(plaintext, char_to_movement, z_value, superposition_sequence):
    cipher_text = []
    superposition_sequence_copy = superposition_sequence.copy()
    for char in plaintext:
        movement = char_to_movement.get(char, None)
        if movement is not None:
            if abs(movement) == (cyclic_prime - 1) // 2:
                movement = superposition_sequence_copy.pop(0)
                superposition_sequence_copy.append(-movement)
            cipher_text.append(movement + z_value * cyclic_prime)
        else:
            raise ValueError(f"Character {char} not in dictionary")
    return cipher_text

def decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence):
    plain_text = []
    superposition_sequence_copy = superposition_sequence.copy()
    for movement in cipher_text:
        original_movement = movement - z_value * cyclic_prime
        if abs(original_movement) == (cyclic_prime - 1) // 2:
            original_movement = superposition_sequence_copy.pop(0)
            superposition_sequence_copy.append(-original_movement)
        char = movement_to_char.get(original_movement, None)
        if char is not None:
            plain_text.append(char)
        else:
            raise ValueError(f"Movement {original_movement} not in dictionary")
    return ''.join(plain_text)

cyclic_prime = 167
cyclic_sequence = '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'[:166]

plaintext = generate_plaintext(128)

khan_enc_time, khan_dec_time, khan_decrypted = measure_khan_encryption(khan_encrypt, khan_decrypt, plaintext)
rsa_enc_time, rsa_dec_time, rsa_decrypted = measure_rsa_encryption(plaintext)
aes_enc_time, aes_dec_time, aes_decrypted = measure_aes_encryption(plaintext)

print(f"Khan Encryption Time: {khan_enc_time}, Decryption Time: {khan_dec_time}")
print(f"RSA Encryption Time: {rsa_enc_time}, Decryption Time: {rsa_dec_time}")
print(f"AES Encryption Time: {aes_enc_time}, Decryption Time: {aes_dec_time}")

print(f"Original Text: {plaintext}")
print(f"Khan Decrypted Text: {khan_decrypted}")
print(f"RSA Decrypted Text: {rsa_decrypted}")
print(f"AES Decrypted Text: {aes_decrypted}")

Performance Comparison

To compare the performance of KHAN encryption with RSA and AES encryption methods, the provided script measures the encryption and decryption times for each algorithm. Below is a sample output of the performance comparison:

Khan Encryption Time: 0.0, Decryption Time: 0.0
RSA Encryption Time: 0.0030107498168945312, Decryption Time: 0.0029990673065185547
AES Encryption Time: 0.0, Decryption Time: 0.0
Original Text: AMCN5ftvKtmBvF0AUH7J9YWe80IvygivCdX5aYfRBqE0qR7gWguCtPdZIRUub3GJSrS44QZOSxPrJIaTsyGwrTHAqdNWD1LCfNUIsPRnghey6XEB3kyC6ctpqXAqKp27
Khan Decrypted Text: AMCN5ftvKtmBvF0AUH7J9YWe80IvygivCdX5aYfRBqE0qR7gWguCtPdZIRUub3GJSrS44QZOSxPrJIaTsyGwrTHAqdNWD1LCfNUIsPRnghey6XEB3kyC6ctpqXAqKp27
RSA Decrypted Text: AMCN5ftvKtmBvF0AUH7J9YWe80IvygivCdX5aYfRBqE0qR7gWguCtPdZIRUub3GJSrS44QZOSxPrJIaTsyGwrTHAqdNWD1LCfNUIsPRnghey6XEB3kyC6ctpqXAqKp27
AES Decrypted Text: AMCN5ftvKtmBvF0AUH7J9YWe80IvygivCdX5aYfRBqE0qR7gWguCtPdZIRUub3GJSrS44QZOSxPrJIaTsyGwrTHAqdNWD1LCfNUIsPRnghey6XEB3kyC6ctpqXAqKp27

Implementation Details

The KHAN encryption algorithm uses the following key components:

    Cyclic Prime Sequence: A sequence generated from a prime number.
    Minimal Movement Calculation: Determines the minimal movement between sequences.
    Superposition Sequence: A sequence of movements ensuring zero net movement.
    Encryption and Decryption Functions: Uses character-to-movement mapping for encryption and decryption.
