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

# Hardcoded full reptend primes by bit size
full_reptend_primes = {
    5: 17, 6: 47, 7: 97, 8: 131, 9: 257, 10: 541, 11: 1033, 12: 2063,
    13: 4099, 14: 8219, 15: 16411, 16: 32779, 17: 65537, 18: 131149,
    19: 262153, 20: 524309, 21: 1048583, 22: 2097211, 23: 4194353,
    24: 8388617, 25: 16777259, 26: 33554467
}

def generate_cyclic_sequence(prime):
    # Generate the repeating decimal sequence of 1/prime
    getcontext().prec = prime * 2  # Set precision high enough to get full reptend
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    # Ensure the sequence has length prime - 1
    cyclic_sequence = decimal_expansion[:prime - 1]
    return cyclic_sequence

def get_minimal_movements(cyclic_sequence, group_length, prime):
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

    superposition_magnitude = (prime - 1) // 2

    for i, target_sequence in enumerate(groups):
        start_positions = digit_positions[start_sequence]
        target_positions = digit_positions[target_sequence]

        min_movement_value = sequence_length
        min_movements = []

        for start_pos in start_positions:
            for target_pos in target_positions:
                clockwise_movement = (target_pos - start_pos) % sequence_length
                anticlockwise_movement = (start_pos - target_pos) % sequence_length

                # Check for minimal movement
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

        # Identify superposition points
        if abs(min_movement_value) == superposition_magnitude:
            superposition_points.append(i)
            # At superposition points, both directions are possible
            min_movements = [-superposition_magnitude, superposition_magnitude]

        movements.append(min_movements)

    return movements, superposition_points

def generate_keypair(prime):
    cyclic_sequence = generate_cyclic_sequence(prime)
    group_length = len(str(prime))
    start_position = random.randint(0, prime - 2)  # Starting position in the cyclic sequence

    # Generate superposition sequence (private key)
    # Determine movements and superposition points
    movements, superposition_points = get_minimal_movements(
        cyclic_sequence[start_position:] + cyclic_sequence[:start_position],
        group_length,
        prime
    )

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

def encrypt(plaintext, public_key):
    prime = public_key['prime']
    cyclic_sequence = public_key['cyclic_sequence']
    start_position = public_key['start_position']

    group_length = len(str(prime))
    movements, superposition_points = get_minimal_movements(
        cyclic_sequence[start_position:] + cyclic_sequence[:start_position],
        group_length,
        prime
    )

    padded_plaintext = pad(plaintext.encode(), BLOCK_SIZE)
    ciphertext = []

    for idx, byte in enumerate(padded_plaintext):
        movement_options = movements[idx % len(movements)]
        # For encryption, choose any movement (since the private key is not known)
        movement = movement_options[0]
        encrypted_byte = (byte + movement) % 256
        ciphertext.append(encrypted_byte)

    return ciphertext, superposition_points

def decrypt(ciphertext, public_key, private_key):
    prime = public_key['prime']
    cyclic_sequence = public_key['cyclic_sequence']
    start_position = public_key['start_position']

    group_length = len(str(prime))
    movements, superposition_points = get_minimal_movements(
        cyclic_sequence[start_position:] + cyclic_sequence[:start_position],
        group_length,
        prime
    )
    superposition_sequence = private_key['superposition_sequence']

    plaintext = []
    superposition_index = 0

    for idx, encrypted_byte in enumerate(ciphertext):
        movement_options = movements[idx % len(movements)]

        if idx in superposition_points:
            # Apply correct movement based on the superposition direction from the private key
            direction = superposition_sequence[superposition_index % len(superposition_sequence)]
            # Movement options at superposition points are [-M, +M]
            movement = direction * abs(movement_options[0])  # Choose the movement based on direction
            superposition_index += 1
        else:
            # Only one movement option
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
    bit_size = 16
    prime = full_reptend_primes[bit_size]

    print(f"Using full reptend prime: {prime}")
    public_key, private_key = generate_keypair(prime)

    print("Public Key:", public_key)
    print("Private Key length:", len(private_key['superposition_sequence']))

    # Generate a random message
    msg = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))
    print("Original Message:", msg)

    start_time = time.time()
    encrypted_msg, superposition_points = encrypt(msg, public_key)
    encryption_time = time.time() - start_time

    print("Encrypted Message:", encrypted_msg)
    print(f"Encryption Time: {encryption_time:.6f} seconds")

    # Generate a random superposition sequence that sums to zero
    original_superposition_sequence = private_key['superposition_sequence']
    length = len(original_superposition_sequence)
    random_superposition_sequence = [random.choice([-1, 1]) for _ in range(length - 1)]
    sum_so_far = sum(random_superposition_sequence)
    # Adjust the last element to make the sum zero
    if sum_so_far % 2 == 0:
        random_superposition_sequence.append(-sum_so_far)
    else:
        random_superposition_sequence.append(-sum_so_far)

    # Replace the private key's superposition sequence with the random one
    modified_private_key = {
        'superposition_sequence': random_superposition_sequence
    }

    start_time = time.time()
    # Attempt to decrypt using the modified private key
    decrypted_msg = decrypt(encrypted_msg, public_key, modified_private_key)
    decryption_time = time.time() - start_time

    print("Attempted Decryption with Random Superposition Sequence:")
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
