import random
import string
from decimal import Decimal, getcontext

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

def generate_target_sequences(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    group_length = len(str(prime))
    cyclic_groups = []
    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) == group_length:
            cyclic_groups.append(group)
        else:
            wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
            cyclic_groups.append(wrap_around_group)
    return sorted(set(cyclic_groups))[:prime - 1]

def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]
    min_movements = []
    min_movement_value = sequence_length

    for start_pos in start_positions:
        for target_pos in target_positions:
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length
            
            if clockwise_movement < min_movement_value:
                min_movements = [clockwise_movement]
                min_movement_value = clockwise_movement
            elif clockwise_movement == min_movement_value:
                min_movements.append(clockwise_movement)
            
            if anticlockwise_movement < min_movement_value:
                min_movements = [-anticlockwise_movement]
                min_movement_value = anticlockwise_movement
            elif anticlockwise_movement == min_movement_value:
                min_movements.append(-anticlockwise_movement)

    return min_movements

def analyze_cyclic_prime(prime, cyclic_sequence, start_position):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    cyclic_sequence = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]
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
    superposition_points = []
    start_sequence = cyclic_sequence[:group_length]
    
    #print(f"Analyzing cyclic prime {prime} with start position {start_position}")
    #print(f"Cyclic sequence: {cyclic_sequence[:50]}...")
    
    for i, target_sequence in enumerate(target_sequences):
        min_movements = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)
        
        if len(min_movements) > 1:
            #print(f"Superposition point found at fraction {i+1}/{prime}")
            superposition_points.append(i)
            movements.append(min_movements[0])  # Choose one arbitrarily for now
        else:
            movements.append(min_movements[0])
        
        #print(f"Fraction {i+1}/{prime}: Movement {movements[-1]}")
    
    #print(f"Total movements: {len(movements)}")
    #print(f"Superposition points: {superposition_points}")
    #print(f"Net movement: {sum(movements)}")
    
    return movements, superposition_points

def generate_keypair(prime, cyclic_sequence):
    start_position = random.randint(1, prime - 1)
    superposition_sequence_length = random.randint(1000, 40000) // 2 * 2  # Ensure even length
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    
    public_key = (prime, cyclic_sequence)
    private_key = (start_position, superposition_sequence)
    
    return public_key, private_key

def encrypt(plaintext, public_key):
    prime, cyclic_sequence = public_key
    start_position = random.randint(1, prime - 1)
    movements, superposition_points = analyze_cyclic_prime(prime, cyclic_sequence, start_position)
    
    ciphertext = []
    for char in plaintext:
        movement = movements[ord(char) % len(movements)]
        ciphertext.append(movement)
    
    return ciphertext, start_position, superposition_points

def decrypt(ciphertext, public_key, private_key, encryption_start_position, superposition_points):
    prime, cyclic_sequence = public_key
    start_position, superposition_sequence = private_key
    
    movements, _ = analyze_cyclic_prime(prime, cyclic_sequence, encryption_start_position)
    movement_to_char = {m: chr(i % 256) for i, m in enumerate(movements)}
    
    plaintext = []
    superposition_index = 0
    
    for i, movement in enumerate(ciphertext):
        if i in superposition_points:
            # This is a superposition point
            direction = superposition_sequence[superposition_index % len(superposition_sequence)]
            movement *= direction
            superposition_index += 1
        
        char = movement_to_char.get(movement, chr(abs(movement) % 256))
        plaintext.append(char)
    
    return ''.join(plaintext)

# Driver program
if __name__ == "__main__":
    print("Running KHAN encryption...")
    
    prime = 1051  # Full reptend prime
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    
    print("Generating public/private keypair...")
    public_key, private_key = generate_keypair(prime, cyclic_sequence)
    
    print("Public Key (prime):", public_key[0])
    print("Private Key (start_position, superposition_sequence length):", private_key[0], len(private_key[1]))
    
    msg = input("Write msg: ")
    print("Original message:", msg)
    
    encrypted_msg, temp_start, superposition_points = encrypt(msg, public_key)
    print("Encrypted msg:")
    print(' '.join(map(str, encrypted_msg)))
    print("Temporary start position used for encryption:", temp_start)
    print("Superposition points:", superposition_points)
    
    decrypted_msg = decrypt(encrypted_msg, public_key, private_key, temp_start, superposition_points)
    print("Decrypted msg:")
    print(decrypted_msg)