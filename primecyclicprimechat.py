import time
from itertools import permutations
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

def chat_simulation(num_messages):
    # Generate keys and superposition sequence
    char_to_movement, movement_to_char = generate_keys(cyclic_prime, cyclic_sequence)
    superposition_sequence = generate_superposition_sequence(cyclic_prime)
    z_value = calculate_z_value(superposition_sequence)

    messages = []
    cipher_texts = []

    for i in range(num_messages):
        user = "User 1" if i % 2 == 0 else "User 2"
        plaintext = input(f"{user}, enter your message: ")
        messages.append(plaintext)
        cipher_text = encrypt_message(plaintext, char_to_movement, z_value, superposition_sequence)
        cipher_texts.append(cipher_text)
        
        # Decryption with Key
        decrypted_with_key = decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence)

        print(f"\nMessage {i + 1} ({user}):")
        print("Original Message:", plaintext)
        print("Ciphertext:", cipher_text)
        print("Decrypted with Key:", decrypted_with_key)
        print("\n")

    print("\n--- Attempting to decrypt without the private key ---\n")
    for i in range(num_messages):
        cipher_text = cipher_texts[i]
        decrypted_simple = brute_force_simple_permutations(cipher_text, possible_movements)
        decrypted_frequency = brute_force_frequency_analysis(cipher_text, possible_movements)
        decrypted_dictionary = brute_force_dictionary_attack(cipher_text, possible_movements, messages)

        print(f"\nMessage {i + 1} Attempt:")
        print("Ciphertext:", cipher_text)
        print("Decrypted with Simple Permutations:", decrypted_simple)
        print("Decrypted with Frequency Analysis:", decrypted_frequency)
        print("Decrypted with Dictionary Attack:", decrypted_dictionary)
        print("\n")

# Example usage with cyclic prime 167 and its cyclic sequence
cyclic_prime = 167
cyclic_sequence = '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'  # First 166 digits
possible_movements = analyze_cyclic_prime(cyclic_prime, cyclic_sequence)

chat_simulation(10)
