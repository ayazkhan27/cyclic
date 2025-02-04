import random
import string
import time
from decimal import Decimal, getcontext
import numpy as np
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import matplotlib.pyplot as plt

# Constants
BLOCK_SIZE = 16
IV_SIZE = 16

# Full reptend primes (primes for which 1/p has a repeating decimal expansion of length p-1)
full_reptend_primes = {
    5: 17, 6: 19, 7: 23, 8: 29, 9: 47, 10: 59, 11: 61, 12: 97, 13: 109,
    14: 113, 15: 131, 16: 149, 17: 167, 18: 179, 19: 181, 20: 191,
    21: 193, 22: 223, 23: 229, 24: 233, 25: 239, 26: 241, 27: 251,
    28: 257, 29: 263, 30: 269, 31: 271, 32: 277
}

def generate_cyclic_sequence(prime):
    # Generate the repeating decimal sequence of 1/prime
    getcontext().prec = prime * 2  # Set precision high enough to get full reptend
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    # Ensure the sequence has length prime - 1
    cyclic_sequence = decimal_expansion[:prime - 1]
    return cyclic_sequence

def get_minimal_movements(cyclic_sequence, group_length):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}

    # Map each group in the sequence to its positions
    for i in range(sequence_length):
        group = cyclic_sequence[i:i + group_length]
        if len(group) == group_length:
            digit_positions.setdefault(group, []).append(i)
        else:
            wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length - len(group)]
            digit_positions.setdefault(wrap_around_group, []).append(i)

    # Generate minimal movements between sequences
    movements = []
    superposition_points = []

    groups = list(digit_positions.keys())
    start_sequence = groups[0]

    for i, target_sequence in enumerate(groups):
        start_positions = digit_positions[start_sequence]
        target_positions = digit_positions[target_sequence]

        min_movement_value = sequence_length
        min_movements = []

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

        if len(min_movements) > 1:
            superposition_points.append(i)
        movements.append(min_movements)

    return movements, superposition_points

def generate_keypair(prime):
    cyclic_sequence = generate_cyclic_sequence(prime)
    group_length = len(str(prime))
    start_position = random.randint(0, prime - 2)  # Starting position in the cyclic sequence
    movements, superposition_points = get_minimal_movements(cyclic_sequence[start_position:] + cyclic_sequence[:start_position], group_length)

    # Generate superposition sequence (private key)
    superposition_sequence_length = len(superposition_points)
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]

    public_key = {
        'prime': prime,
        'cyclic_sequence': cyclic_sequence,
        'start_position': start_position
    }

    private_key = {
        'superposition_sequence': superposition_sequence
    }

    return public_key, private_key

def map_movements_to_torus(movements, prime):
    torus_coordinates = []
    for movement_options in movements:
        movement = movement_options[0]  # For encryption, choose any movement
        theta = (movement % prime) * (2 * np.pi / prime)
        phi = (movement % prime) * (2 * np.pi / prime)
        x = (2 + np.cos(theta)) * np.cos(phi)
        y = (2 + np.cos(theta)) * np.sin(phi)
        z = np.sin(theta)
        torus_coordinates.append((x, y, z))
    return torus_coordinates

def encrypt(plaintext, public_key):
    prime = public_key['prime']
    cyclic_sequence = public_key['cyclic_sequence']
    start_position = public_key['start_position']

    group_length = len(str(prime))
    movements, superposition_points = get_minimal_movements(cyclic_sequence[start_position:] + cyclic_sequence[:start_position], group_length)

    padded_plaintext = pad(plaintext.encode(), BLOCK_SIZE)
    ciphertext = []
    superposition_index = 0

    for idx, byte in enumerate(padded_plaintext):
        movement_options = movements[idx % len(movements)]

        movement = movement_options[0]  # For encryption, we can choose any movement
        # Incorporate movement into the message
        encrypted_byte = (byte + movement) % 256
        ciphertext.append(encrypted_byte)

    return ciphertext, superposition_points

def decrypt(ciphertext, public_key, private_key):
    prime = public_key['prime']
    cyclic_sequence = public_key['cyclic_sequence']
    start_position = public_key['start_position']

    group_length = len(str(prime))
    movements, superposition_points = get_minimal_movements(cyclic_sequence[start_position:] + cyclic_sequence[:start_position], group_length)
    superposition_sequence = private_key['superposition_sequence']

    plaintext = []
    superposition_index = 0

    for idx, encrypted_byte in enumerate(ciphertext):
        movement_options = movements[idx % len(movements)]

        if idx in superposition_points:
            # Apply correct movement based on the superposition direction from the private key
            direction = superposition_sequence[superposition_index % len(superposition_sequence)]
            movement = next(m for m in movement_options if (m > 0 and direction > 0) or (m < 0 and direction < 0))
            superposition_index += 1
        else:
            movement = movement_options[0]

        decrypted_byte = (encrypted_byte - movement) % 256
        plaintext.append(decrypted_byte)

    decrypted_plaintext = bytes(plaintext)

    try:
        return unpad(decrypted_plaintext, BLOCK_SIZE).decode()
    except ValueError as e:
        print(f"Unpadding error: {e}")
        return decrypted_plaintext.decode(errors='ignore')

def measure_entropy(data):
    from collections import Counter
    frequency = Counter(data)
    probabilities = [freq / len(data) for freq in frequency.values()]
    entropy = -sum(p * np.log2(p) for p in probabilities)
    return entropy

def measure_avalanche_effect(ciphertext1, ciphertext2):
    bits1 = ''.join(f'{byte:08b}' for byte in ciphertext1)
    bits2 = ''.join(f'{byte:08b}' for byte in ciphertext2)
    diff_bits = sum(b1 != b2 for b1, b2 in zip(bits1, bits2))
    total_bits = len(bits1)
    avalanche = diff_bits / total_bits
    return avalanche

def plot_ciphertext_distribution(ciphertext):
    plt.hist(ciphertext, bins=range(256), edgecolor='black')
    plt.title('Ciphertext Byte Distribution')
    plt.xlabel('Byte Value')
    plt.ylabel('Frequency')
    plt.show()

if __name__ == "__main__":
    print("Running KHAN Encryption Algorithm...")

    # Select a prime number for the algorithm
    bit_size = 8
    prime = full_reptend_primes[bit_size]

    print(f"Using full reptend prime: {prime}")
    public_key, private_key = generate_keypair(prime)

    print("Public Key:", public_key)
    print("Private Key length:", len(private_key['superposition_sequence']))

    # Generate a random message
    msg = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    print("Original Message:", msg)

    start_time = time.time()
    encrypted_msg, superposition_points = encrypt(msg, public_key)
    encryption_time = time.time() - start_time

    print("Encrypted Message:", encrypted_msg)
    print(f"Encryption Time: {encryption_time:.6f} seconds")

    start_time = time.time()
    decrypted_msg = decrypt(encrypted_msg, public_key, private_key)
    decryption_time = time.time() - start_time

    print("Decrypted Message:", decrypted_msg)
    print(f"Decryption Time: {decryption_time:.6f} seconds")

    decryption_success = (msg == decrypted_msg)
    print(f"Decryption Successful: {decryption_success}")

    # Security Metrics
    entropy = measure_entropy(encrypted_msg)
    print(f"Entropy of Ciphertext: {entropy:.4f} bits per byte")

    # Avalanche Effect
    modified_msg = msg[:-1] + chr((ord(msg[-1]) + 1) % 256)
    encrypted_modified_msg, _ = encrypt(modified_msg, public_key)

    avalanche = measure_avalanche_effect(encrypted_msg, encrypted_modified_msg)
    print(f"Avalanche Effect: {avalanche * 100:.2f}% difference")

    # Plotting Ciphertext Distribution
    plot_ciphertext_distribution(encrypted_msg)
