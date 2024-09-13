import random
import string
from decimal import Decimal, getcontext

# Adjusted precision for cyclic sequences
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

# Calculate the minimal movements in the toroidal structure
def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, z_value_length):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]
    
    min_movements = []
    min_movement_value = sequence_length

    for start_pos in start_positions:
        for target_pos in target_positions:
            # Extract X, Y, and Z values
            start_x, start_z = start_pos[0], start_pos[1]
            target_x, target_z = target_pos[0], target_pos[1]

            # Handle X-movement (clockwise/anticlockwise)
            clockwise_movement_x = (target_x - start_x) % sequence_length
            anticlockwise_movement_x = (start_x - target_x) % sequence_length

            # Handle Z-movement (layer wrapping)
            movement_z = abs(target_z - start_z) % z_value_length  # Movement in the Z-dimension

            # Combine the movements across both dimensions
            total_movement = clockwise_movement_x + movement_z

            if total_movement < min_movement_value:
                min_movements = [total_movement]
                min_movement_value = total_movement
            elif total_movement == min_movement_value:
                min_movements.append(total_movement)

    return min_movements

# Modify to use Z-dimension wrapping (torus) in analysis
def analyze_cyclic_prime(prime, cyclic_sequence, start_position, z_value):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    cyclic_sequence = cyclic_sequence[start_position:] + cyclic_sequence[:start_position]
    group_length = len(str(prime))
    
    # Mapping digit positions (including the Z value)
    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) == group_length:
            if group in digit_positions:
                digit_positions[group].append((i, z_value))  # Include z_value in the mapping
            else:
                digit_positions[group] = [(i, z_value)]
        else:
            wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
            if wrap_around_group in digit_positions:
                digit_positions[wrap_around_group].append((i, z_value))
            else:
                digit_positions[wrap_around_group] = [(i, z_value)]
    
    target_sequences = generate_target_sequences(prime, cyclic_sequence)
    movements = []
    superposition_points = []
    start_sequence = cyclic_sequence[:group_length]
    
    # Set z_value_length for toroidal wrapping
    z_value_length = prime  # Adjust this based on your requirements
    
    # Dynamically set the superposition movement
    superposition_movement = (prime - 1) // 2
    
    # Debugging to check fractions with multiple minimal movements
    multiple_choices_fractions = []

    for i, target_sequence in enumerate(target_sequences):
        min_movements = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, z_value_length)
        
        if len(min_movements) > 1:
            multiple_choices_fractions.append(i)  # Keep track of fractions with multiple minimal movements
            superposition_points.append(i)
            # Dynamically adjust the last movement to be the superposition movement
            movements.append(superposition_movement)
        else:
            movements.append(min_movements[0])
    
    print("Fractions with multiple minimal movements:", multiple_choices_fractions)
    print("Superposition Movement Magnitude:", superposition_movement)

    return movements, superposition_points

# Generating a keypair including a Z-dimension for the torus
def generate_keypair(prime, cyclic_sequence):
    start_position = random.randint(1, prime - 1)
    superposition_sequence_length = random.randint(1000, 40000) // 2 * 2
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    
    z_value = random.randint(0, prime - 1)  # Introduce a Z-value for 3D wrapping
    
    public_key = (prime, cyclic_sequence)
    private_key = (start_position, superposition_sequence, z_value)
    
    return public_key, private_key

# Torus-based encryption using Z-layer wrapping
def encrypt(plaintext, public_key):
    prime, cyclic_sequence = public_key
    start_position = random.randint(1, prime - 1)
    z_value = random.randint(0, prime - 1)  # Random Z-value for encryption
    movements, superposition_points = analyze_cyclic_prime(prime, cyclic_sequence, start_position, z_value)
    
    ciphertext = []
    for char in plaintext:
        movement = movements[ord(char) % len(movements)]
        ciphertext.append(movement)
    
    return ciphertext, start_position, superposition_points, z_value

# Decryption now needs the correct Z-value from the private key
def decrypt(ciphertext, public_key, private_key, encryption_start_position, superposition_points, encryption_z_value):
    prime, cyclic_sequence = public_key
    start_position, superposition_sequence, z_value = private_key
    
    movements, _ = analyze_cyclic_prime(prime, cyclic_sequence, encryption_start_position, encryption_z_value)
    movement_to_char = {m: chr(i % 256) for i, m in enumerate(movements)}
    
    plaintext = []
    superposition_index = 0
    
    for i, movement in enumerate(ciphertext):
        if i in superposition_points:
            direction = superposition_sequence[superposition_index % len(superposition_sequence)]
            movement *= direction
            superposition_index += 1
        
        char = movement_to_char.get(movement, chr(abs(movement) % 256))
        plaintext.append(char)
    
    return ''.join(plaintext)

# Main block to test the encryption
if __name__ == "__main__":
    print("Running KHAN Torus encryption...")

    prime = 1051
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    
    print("Generating public/private keypair...")
    public_key, private_key = generate_keypair(prime, cyclic_sequence)
    
    print("Public Key (prime):", public_key[0])
    print("Private Key (start_position, superposition_sequence length, Z-value):", private_key[0], len(private_key[1]), private_key[2])
    
    msg = input("Write msg: ")
    print("Original message:", msg)
    
    encrypted_msg, temp_start, superposition_points, z_value = encrypt(msg, public_key)
    print("Encrypted msg:")
    print(' '.join(map(str, encrypted_msg)))
    print("Temporary start position used for encryption:", temp_start)
    print("Superposition points:", superposition_points)
    print("Encryption Z-value:", z_value)
    
    decrypted_msg = decrypt(encrypted_msg, public_key, private_key, temp_start, superposition_points, z_value)
    print("Decrypted msg:")
    print(decrypted_msg)
