import time

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
    char_to_movement = {}
    movement_to_char = {}
    for i, movement in enumerate(movements):
        char = chr(65 + i) if i < 26 else chr(97 + i - 26)  # A-Z and a-z
        char_to_movement[char] = movement
        movement_to_char[movement] = char
    return char_to_movement, movement_to_char

def encrypt_message(plaintext, char_to_movement):
    cipher_text = []
    for char in plaintext:
        movement = char_to_movement.get(char, None)
        if movement is not None:
            cipher_text.append(movement)
        else:
            raise ValueError(f"Character {char} not in dictionary")
    return cipher_text

def decrypt_message(cipher_text, movement_to_char):
    plain_text = []
    for movement in cipher_text:
        char = movement_to_char.get(movement, None)
        if char is not None:
            plain_text.append(char)
        else:
            raise ValueError(f"Movement {movement} not in dictionary")
    return ''.join(plain_text)

# Example usage with cyclic prime 59 and its cyclic sequence
cyclic_prime = 59
cyclic_sequence = '016949152542372881355932203389830508474576271186440677966'

char_to_movement, movement_to_char = generate_keys(cyclic_prime, cyclic_sequence)

plaintext = "HELLO"
cipher_text = encrypt_message(plaintext, char_to_movement)

# Decryption with Key
start_time = time.time()
decrypted_with_key = decrypt_message(cipher_text, movement_to_char)
time_with_key = time.time() - start_time

print("Plaintext:", plaintext)
print("Ciphertext:", cipher_text)
print("Decrypted with Key:", decrypted_with_key)
print("Decryption Time with Key:", time_with_key)
