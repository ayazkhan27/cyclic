import time
import random
import string
from itertools import permutations
from hashlib import sha256

# Function to generate random plaintext of a given length
def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

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

def analyze_cyclic_prime(prime, cyclic_sequence, start_position):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    
    # Shift cyclic sequence based on start position
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

def generate_keys(prime, cyclic_sequence, start_position):
    movements = analyze_cyclic_prime(prime, cyclic_sequence, start_position)
    
    all_chars = ''.join(chr(i) for i in range(32, 127))  # Printable ASCII characters
    
    char_to_movement = {}
    movement_to_char = {}
    used_movements = set()
    
    for i, char in enumerate(all_chars):
        if i < len(movements):
            movement = movements[i]
        else:
            # Generate additional movements if needed
            movement = (i - len(movements)) * prime  # Ensure new movements are unique
        if movement not in used_movements:
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

def assign_z_layer(movement, salt):
    hashed = sha256(f"{movement}{salt}".encode()).hexdigest()
    return (int(hashed, 16) % 10) + 1  # Ensuring non-zero Z layer

def khan_encrypt(plaintext, prime, cyclic_sequence, start_position):
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    superposition_sequence = generate_superposition_sequence(prime)
    z_value = calculate_z_value(superposition_sequence)
    
    # Generate IV and Salt
    iv = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    # Combine IV, Salt, and Plaintext
    combined_text = iv + salt + plaintext
    ciphertext, z_layers = encrypt_message(combined_text, char_to_movement, z_value, superposition_sequence, salt, prime)
    return ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers

def khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence):
    # Shift cyclic sequence based on start position
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
            cipher_text.append(movement * z_layer + z_value * prime)  # Multiplying with Z layer
        else:
            raise ValueError(f"Character {char} not in dictionary")
    
    return cipher_text, z_layers

def decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime):
    plain_text = []
    superposition_sequence_copy = superposition_sequence.copy()
    for i, movement in enumerate(cipher_text):
        z_layer = z_layers[i]
        original_movement = (movement - z_value * prime) // z_layer  # Adjusting decryption for Z layer multiplication
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

def known_plaintext_attack(plaintext, ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, prime, iv, salt, z_layers, start_position, cyclic_sequence):
    decrypted_text = khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence)
    return decrypted_text == plaintext

# Setup encryption parameters
cyclic_prime = 167
start_position = 43  # Example starting position
cyclic_sequence = '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'[:166]

# Generate random plaintext
plaintext = generate_plaintext(128)

# Measure encryption and decryption time for Khan encryption
khan_encrypt_func = lambda pt: khan_encrypt(pt, cyclic_prime, cyclic_sequence, start_position)
khan_decrypt_func = lambda ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers: khan_decrypt(ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)

def measure_khan_encryption(plaintext):
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = khan_encrypt_func(plaintext)
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_text = khan_decrypt_func(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers)
    decryption_time = time.time() - start_time


    # Compare original plaintext with decrypted plaintext
    if decrypted_text == plaintext:
        print("All characters match between the original and decrypted text.")
    else:
        print("Mismatch between original and decrypted text.")
        for i, (orig_char, decr_char) in enumerate(zip(plaintext, decrypted_text)):
            if orig_char != decr_char:
                print(f"Character mismatch at position {i}: original '{orig_char}', decrypted '{decr_char}'")
    
    return encryption_time, decryption_time, decrypted_text, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers

khan_enc_time, khan_dec_time, khan_decrypted, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers = measure_khan_encryption(plaintext)

print(f"Khan Encryption Time: {khan_enc_time}, Decryption Time: {khan_dec_time}")
print(f"Original Text: {plaintext}")
print(f"Khan Decrypted Text: {khan_decrypted}")

# Generate keys and capture return values
char_to_movement, movement_to_char = generate_keys(cyclic_prime, cyclic_sequence, start_position)

# Simulate chosen plaintext attack
plaintexts = ["Hello", "World", "12345", "Testing"]
chosen_attack_results = chosen_plaintext_attack(plaintexts, cyclic_prime, cyclic_sequence, start_position)
chosen_plaintexts = [res[0] for res in chosen_attack_results]
chosen_ciphertexts = [res[1] for res in chosen_attack_results]
print(f"Chosen Plaintext Attack Ciphertexts: {chosen_ciphertexts}")

# Simulate known plaintext attack
plaintext = "KnownPlaintext"
ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = khan_encrypt_func(plaintext)
is_decrypted = known_plaintext_attack(plaintext, ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, cyclic_prime, iv, salt, z_layers, start_position, cyclic_sequence)
print(f"Known Plaintext Attack Successful: {is_decrypted}")

# Simulate brute force attack
possible_movements = analyze_cyclic_prime(cyclic_prime, cyclic_sequence, start_position)
decrypted_brute_force = brute_force_attack(ciphertext, possible_movements, movement_to_char)
print(f"Brute Force Attack Decrypted Text: {decrypted_brute_force}")
