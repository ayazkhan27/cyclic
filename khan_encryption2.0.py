import random
import string
from hashlib import sha256
from decimal import Decimal, getcontext

def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

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
    
    all_chars = ''.join(chr(i) for i in range(32, 127))
    
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
    
    return char_to_movement, movement_to_char

def generate_superposition_sequence(sequence_length):
    while True:
        left_right_sequence = [random.choice([-1, 1]) for _ in range(sequence_length)]
        if sum(left_right_sequence) == 0:
            return left_right_sequence

def calculate_z_value(superposition_sequence):
    return sum(1 for i in range(1, len(superposition_sequence)) if superposition_sequence[i] == superposition_sequence[i - 1])

def assign_z_layer(movement, salt):
    hashed = sha256(f"{movement}{salt}".encode()).hexdigest()
    return (int(hashed, 16) % 10) + 1

def khan_encrypt(plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length):
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    superposition_sequence = generate_superposition_sequence(superposition_sequence_length)
    z_value = calculate_z_value(superposition_sequence)
    
    iv = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    combined_text = iv + salt + plaintext
    ciphertext, z_layers = encrypt_message(combined_text, char_to_movement, z_value, superposition_sequence, salt, prime)
    return ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers

def khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence):
    cyclic_sequence = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]
    
    combined_text = decrypt_message(ciphertext, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime)
    plaintext = combined_text[len(iv) + len(salt):]
    return plaintext

def encrypt_message(plaintext, char_to_movement, z_value, superposition_sequence, salt, prime):
    cipher_text = []
    z_layers = []
    superposition_sequence_copy = superposition_sequence.copy()
    for char in plaintext:
        movement = char_to_movement.get(char, None)
        if movement is not None:
            z_layer = assign_z_layer(movement, salt)
            z_layers.append(z_layer)
            if abs(movement) == (prime - 1) // 2:
                movement = superposition_sequence_copy.pop(0)
                superposition_sequence_copy.append(-movement)
            cipher_text.append(movement * z_layer + z_value * prime)
        else:
            raise ValueError(f"Character {char} not in dictionary")
    
    return cipher_text, z_layers

def decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime):
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
    return ''.join(plain_text)

def brute_force_attack(ciphertext, possible_movements, movement_to_char):
    for perm in permutations(possible_movements, len(ciphertext)):
        plaintext = []
        try:
            for i, c in enumerate(ciphertext):
                if c == perm[i]:
                    plaintext.append(movement_to_char[perm[i]])
                else:
                    raise ValueError
            return ''.join(plaintext)
        except ValueError:
            continue
    return None

def chosen_plaintext_attack(plaintexts, prime, cyclic_sequence, start_position):
    results = []
    for pt in plaintexts:
        result = khan_encrypt(pt, prime, cyclic_sequence, start_position)
        results.append(result)
    return results

def known_plaintext_attack(plaintext, ciphertext, char_to_movement, z_value, superposition_sequence, prime, iv, salt, z_layers, start_position, cyclic_sequence):
    decrypted_text = khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence)
    return decrypted_text == plaintext
