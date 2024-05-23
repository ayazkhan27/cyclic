import time
import string
import random

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
    all_chars = ''.join(chr(i) for i in range(128))  # All ASCII characters
    char_to_movement = {}
    movement_to_char = {}
    for i, movement in enumerate(movements):
        char = all_chars[i % len(all_chars)]
        char_to_movement[char] = movement
        movement_to_char[movement] = char
    return char_to_movement, movement_to_char

def generate_superposition_sequence(prime):
    sequence_length = prime - 1
    while True:
        left_right_sequence = [random.choice([-1, 1]) for _ in range(sequence_length)]
        if sum(left_right_sequence) == 0:
            return left_right_sequence

def calculate_z_value(superposition_sequence):
    return sum(1 for i in range(1, len(superposition_sequence)) if superposition_sequence[i] == superposition_sequence[i - 1])

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

# Example usage with cyclic prime 131 and its first 130 digits
cyclic_prime = 131
cyclic_sequence = '007633587786259541984732824427480916030534351145038167938931297709923664122137404580152671755725190839694656488549618320610687022900763358778625954198473282442748091603053435114503816793893129770992366412213740458015267175572519083969465648854961832061068702290076335877862595419847328244274809160305343511450381679389313'  # First 130 digits

char_to_movement, movement_to_char = generate_keys(cyclic_prime, cyclic_sequence)

plaintext = "User123! Please update your password to something more secure."

superposition_sequence = generate_superposition_sequence(cyclic_prime)
z_value = calculate_z_value(superposition_sequence)

cipher_text = encrypt_message(plaintext, char_to_movement, z_value, superposition_sequence)

# Decryption with Key
start_time = time.time()
decrypted_with_key = decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence)
time_with_key = time.time() - start_time

print("Plaintext:", plaintext)
print("Ciphertext:", cipher_text)
print("Decrypted with Key:", decrypted_with_key)
print("Decryption Time with Key:", time_with_key)

# Attempt decryption without z_value and superposition_sequence
def decrypt_without_key(cipher_text, movement_to_char, prime):
    possible_chars = ''.join(chr(i) for i in range(128))
    for z in range(10):  # Assuming a small range for z_value for illustration
        for _ in range(100):  # Trying multiple superposition sequences for illustration
            test_superposition_sequence = generate_superposition_sequence(prime)
            try:
                decrypted_text = decrypt_message(cipher_text, movement_to_char, z, test_superposition_sequence)
                if all(char in possible_chars for char in decrypted_text):
                    return decrypted_text, z, test_superposition_sequence
            except ValueError:
                continue
    return None, None, None

start_time = time.time()
decrypted_without_key, guessed_z_value, guessed_superposition_sequence = decrypt_without_key(cipher_text, movement_to_char, cyclic_prime)
time_without_key = time.time() - start_time

print("Decrypted without Key:", decrypted_without_key)
print("Guessed Z Value:", guessed_z_value)
print("Guessed Superposition Sequence:", guessed_superposition_sequence)
print("Decryption Time without Key:", time_without_key)
