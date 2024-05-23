import time
from itertools import permutations
import string

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

def encrypt_message(plaintext, char_to_movement):
    cipher_text = []
    for char in plaintext:
        movement = char_to_movement.get(char, None)
        if movement is not None:
            cipher_text.append(movement)
        else:
            raise ValueError(f"Character {char} not in dictionary")
    return cipher_text

def brute_force_simple_permutations(cipher_text, possible_movements):
    for perm in permutations(possible_movements, len(cipher_text)):
        plain_text = []
        try:
            for i, c in enumerate(cipher_text):
                if c == perm[i]:
                    plain_text.append(chr(65 + i))  # Assuming uppercase letters for simplicity
                else:
                    raise ValueError
            return ''.join(plain_text)
        except ValueError:
            continue
    return None

def brute_force_frequency_analysis(cipher_text, possible_movements):
    freq_movements = sorted(possible_movements, key=lambda x: cipher_text.count(x), reverse=True)
    possible_chars = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'  # Frequency order of letters in English
    plain_text = []
    for c in cipher_text:
        if c in freq_movements:
            char = possible_chars[freq_movements.index(c) % len(possible_chars)]
            plain_text.append(char)
        else:
            return None
    return ''.join(plain_text)

def brute_force_dictionary_attack(cipher_text, possible_movements, dictionary):
    for word in dictionary:
        if len(word) != len(cipher_text):
            continue
        try:
            plain_text = []
            for i, c in enumerate(cipher_text):
                if c == possible_movements[ord(word[i]) - 65]:  # Assuming uppercase letters for simplicity
                    plain_text.append(word[i])
                else:
                    raise ValueError
            return ''.join(plain_text)
        except ValueError:
            continue
    return None

# Example usage with cyclic prime 131 and its cyclic sequence
cyclic_prime = 131
cyclic_sequence = '007633587786259541984732824427480916030534351145038167938931297709923664122137404580152671755725190839694656488549618320610687022900763358778625954198473282442748091603053435114503816793893129770992366412213740458015267175572519083969465648854961832061068702290076335877862595419847328244274809160305343511450381679389313'  # First 130 digits
possible_movements = analyze_cyclic_prime(cyclic_prime, cyclic_sequence)

# Assuming cipher_text is generated by some encryption process
char_to_movement, movement_to_char = generate_keys(cyclic_prime, cyclic_sequence)
cipher_text = encrypt_message("User123! Please update your password to something more secure.", char_to_movement)

# Brute-Force Decryption without Key
start_time = time.time()
decrypted_simple = brute_force_simple_permutations(cipher_text, possible_movements)
time_simple = time.time() - start_time

start_time = time.time()
decrypted_frequency = brute_force_frequency_analysis(cipher_text, possible_movements)
time_frequency = time.time() - start_time

dictionary = ["HELLO", "WORLD", "TEST", "EXAMPLE"]  # Example dictionary for the attack
start_time = time.time()
decrypted_dictionary = brute_force_dictionary_attack(cipher_text, possible_movements, dictionary)
time_dictionary = time.time() - start_time

print("Ciphertext:", cipher_text)
print("Decrypted with Simple Permutations:", decrypted_simple)
print("Decryption Time with Simple Permutations:", time_simple)
print("Decrypted with Frequency Analysis:", decrypted_frequency)
print("Decryption Time with Frequency Analysis:", time_frequency)
print("Decrypted with Dictionary Attack:", decrypted_dictionary)
print("Decryption Time with Dictionary Attack:", time_dictionary)
