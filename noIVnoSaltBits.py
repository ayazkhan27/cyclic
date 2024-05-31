import random
import string
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

def assign_z_layer(movement):
    return (abs(movement) % 10) + 1

def initialize_dictionaries():
    all_chars = string.ascii_letters + string.digits + string.punctuation + ' '
    prime = 1051  # Adjust according to your requirements
    char_to_movement = {char: (i % prime) for i, char in enumerate(all_chars)}
    movement_to_char = {(i % prime): char for i, char in enumerate(all_chars)}
    return char_to_movement, movement_to_char

def khan_encrypt(plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length):
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    superposition_sequence = generate_superposition_sequence(superposition_sequence_length)
    z_value = calculate_z_value(superposition_sequence)
    
    ciphertext, z_layers = encrypt_message(plaintext, char_to_movement, z_value, superposition_sequence, prime)
    return ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, z_layers

def khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, z_layers, prime, start_position, cyclic_sequence):
    cyclic_sequence = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]
    
    plaintext = decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence, z_layers, prime)
    return plaintext

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
    return ''.join(plain_text)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def calculate_entropy(ciphertext):
    total_chars = len(ciphertext)
    frequency_dict = {char: ciphertext.count(char) for char in set(ciphertext)}
    entropy = Decimal(0)
    for char, frequency in frequency_dict.items():
        probability = Decimal(frequency) / total_chars
        entropy -= probability * probability.ln() / Decimal(2).ln()  # Convert to base 2
    return entropy

def calculate_security_bits(prime, plaintext_length, start_position_range, superposition_length_range):
    key_space = prime * (superposition_length_range // 2)  # key space size
    security_bits = np.log2(key_space) * plaintext_length  # estimate security in bits
    return security_bits - plaintext_length  # adjust by plaintext length

def main():
    global cyclic_prime
    cyclic_prime = 1051  # Set the cyclic prime to 1051

    # User input for private keys
    start_position = int(input(f"User 1: Enter the starting dial position (integer between 1 and {cyclic_prime - 1}): "))
    superposition_sequence_length = int(input("User 2: Enter the superposition sequence length (even integer): "))

    # Generate random plaintext
    plaintext = generate_plaintext(128)

    # Generate the cyclic sequence
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Measure encryption and decryption
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, z_layers = khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)
    decrypted_text = khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, z_layers, cyclic_prime, start_position, cyclic_sequence)

    # Calculate entropy
    entropy_value = calculate_entropy(ciphertext)

    # Calculate security bits
    security_bits = calculate_security_bits(cyclic_prime, len(plaintext), cyclic_prime - 1, 100)

    # Display results
    print("\nEncryption and Decryption Results:")
    print("Original Plaintext:", plaintext)
    print("Decrypted Plaintext:", decrypted_text)
    print("Entropy of Ciphertext:", entropy_value)
    print("Estimated Security Bits:", security_bits)
    print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")

if __name__ == "__main__":
    main()
