import random
import string
from hashlib import sha256
from decimal import Decimal, getcontext
import numpy as np
from collections import Counter
from scipy.stats import entropy as kl_divergence
import matplotlib.pyplot as plt

# Function definitions for KHAN encryption algorithm

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

def assign_z_layer(movement, salt):
    hashed = sha256(f"{movement}{salt}".encode()).hexdigest()
    return (int(hashed, 16) % 10) + 1

def khan_encrypt(plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length):
    char_to_movement, movement_to_char = generate_keys(prime, cyclic_sequence, start_position)
    superposition_sequence = generate_superposition_sequence(superposition_sequence_length)
    z_value = calculate_z_value(superposition_sequence)
    iv = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    combined_text = iv + salt + plaintext
    ciphertext, z_layers = encrypt_message(combined_text, char_to_movement, z_value, superposition_sequence, salt, prime)
    return ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers

def khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence):
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
            cipher_text.append(movement * z_layer + z_value * prime)
        else:
            raise ValueError(f"Character {char} not in dictionary")
    return cipher_text, z_layers

def decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime):
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

# Metric calculation functions

def calculate_entropy(message):
    if not message:
        return 0
    entropy = 0
    char_count = Counter(message)
    for count in char_count.values():
        p_x = count / len(message)
        entropy += -p_x * np.log2(p_x)
    return entropy

def kl_divergence_metric(p, q):
    p_counts = Counter(p)
    q_counts = Counter(q)
    all_chars = set(p + q)
    p_dist = np.array([p_counts[char] / len(p) for char in all_chars])
    q_dist = np.array([q_counts[char] / len(q) for char in all_chars])
    return kl_divergence(p_dist, q_dist)

def coherent_shannon_entropy(message):
    shannon_entropy = calculate_entropy(message)
    coherence = np.correlate([ord(c) for c in message], [ord(c) for c in message], mode='full')
    coherence = coherence[len(coherence) // 2:]  # Take only the second half
    cse = shannon_entropy + 0.5 * sum(coherence) / len(message)  # Adjust coefficient as needed
    return cse

def mutual_information(message1, message2):
    joint_prob = Counter(zip(message1, message2))
    total_pairs = len(message1)
    mi = 0
    for (x, y), count in joint_prob.items():
        p_xy = count / total_pairs
        p_x = message1.count(x) / len(message1)
        p_y = message2.count(y) / len(message2)
        mi += p_xy * np.log2(p_xy / (p_x * p_y))
    return mi

# Simulation and plotting functions

def simulate_entropy_measurements(iterations=100):
    prime = 1051
    start_position = 1
    superposition_sequence_length = 10
    entropy_info, entropy_noise = [], []
    kl_info, kl_noise = [], []
    mi_info, mi_noise = [], []
    cse_info, cse_noise = [], []

    for _ in range(iterations):
        plaintext_info = generate_plaintext(128)
        plaintext_noise = generate_plaintext(128)

        ciphertext_info, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = khan_encrypt(plaintext_info, prime, generate_cyclic_sequence(prime, prime - 1), start_position, superposition_sequence_length)
        decrypted_info = khan_decrypt(ciphertext_info, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, generate_cyclic_sequence(prime, prime - 1))

        ciphertext_noise, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = khan_encrypt(plaintext_noise, prime, generate_cyclic_sequence(prime, prime - 1), start_position, superposition_sequence_length)
        decrypted_noise = khan_decrypt(ciphertext_noise, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, generate_cyclic_sequence(prime, prime - 1))

        entropy_info.append((calculate_entropy(plaintext_info), calculate_entropy(decrypted_info)))
        entropy_noise.append((calculate_entropy(plaintext_noise), calculate_entropy(decrypted_noise)))

        kl_info.append(kl_divergence_metric(plaintext_info, decrypted_info))
        kl_noise.append(kl_divergence_metric(plaintext_noise, decrypted_noise))

        mi_info.append(mutual_information(plaintext_info, decrypted_info))
        mi_noise.append(mutual_information(plaintext_noise, decrypted_noise))

        cse_info.append((coherent_shannon_entropy(plaintext_info), coherent_shannon_entropy(decrypted_info)))
        cse_noise.append((coherent_shannon_entropy(plaintext_noise), coherent_shannon_entropy(decrypted_noise)))

    return entropy_info, entropy_noise, kl_info, kl_noise, mi_info, mi_noise, cse_info, cse_noise

def plot_results(entropy_info, entropy_noise, kl_info, kl_noise, mi_info, mi_noise, cse_info, cse_noise):
    # Plotting entropy difference
    info_diffs = [x[1] - x[0] for x in entropy_info]
    noise_diffs = [x[1] - x[0] for x in entropy_noise]
    plt.figure(figsize=(10, 6))
    plt.boxplot([info_diffs, noise_diffs], labels=['Information-Rich', 'Random Noise'])
    plt.title('Entropy Difference Comparison')
    plt.ylabel('Entropy Difference')
    plt.show()

    # Plotting KL-divergence
    plt.figure(figsize=(10, 6))
    plt.boxplot([kl_info, kl_noise], labels=['Information-Rich', 'Random Noise'])
    plt.title('KL-Divergence Comparison')
    plt.ylabel('KL-Divergence')
    plt.show()

    # Plotting mutual information
    plt.figure(figsize=(10, 6))
    plt.plot(mi_info, label='Information-Rich')
    plt.plot(mi_noise, label='Random Noise')
    plt.title('Mutual Information over Iterations')
    plt.xlabel('Iteration')
    plt.ylabel('Mutual Information')
    plt.legend()
    plt.show()

    # Plotting CSE difference
    info_diffs = [x[1] - x[0] for x in cse_info]
    noise_diffs = [x[1] - x[0] for x in cse_noise]
    plt.figure(figsize=(10, 6))
    plt.boxplot([info_diffs, noise_diffs], labels=['Information-Rich', 'Random Noise'])
    plt.title('Coherent Shannon Entropy (CSE) Difference Comparison')
    plt.ylabel('CSE Difference')
    plt.show()

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

def main():
    iterations = 100
    entropy_info, entropy_noise, kl_info, kl_noise, mi_info, mi_noise, cse_info, cse_noise = simulate_entropy_measurements(iterations)

    avg_entropy_info = np.mean([x[1] - x[0] for x in entropy_info])
    avg_entropy_noise = np.mean([x[1] - x[0] for x in entropy_noise])
    avg_kl_info = np.mean(kl_info)
    avg_kl_noise = np.mean(kl_noise)
    avg_mi_info = np.mean(mi_info)
    avg_mi_noise = np.mean(mi_noise)
    avg_cse_info = np.mean([x[1] - x[0] for x in cse_info])
    avg_cse_noise = np.mean([x[1] - x[0] for x in cse_noise])

    print("Average Entropy Difference (Information-Rich):", avg_entropy_info)
    print("Average Entropy Difference (Random Noise):", avg_entropy_noise)
    print("Average KL-Divergence (Information-Rich):", avg_kl_info)
    print("Average KL-Divergence (Random Noise):", avg_kl_noise)
    print("Average Mutual Information (Information-Rich):", avg_mi_info)
    print("Average Mutual Information (Random Noise):", avg_mi_noise)
    print("Average CSE Difference (Information-Rich):", avg_cse_info)
    print("Average CSE Difference (Random Noise):", avg_cse_noise)

    # Plotting the results
    plot_results(entropy_info, entropy_noise, kl_info, kl_noise, mi_info, mi_noise, cse_info, cse_noise)

if __name__ == "__main__":
    main()
