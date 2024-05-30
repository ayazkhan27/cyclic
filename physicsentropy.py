import random
import string
import math
from collections import Counter
from decimal import Decimal, getcontext
import numpy as np
from scipy.stats import entropy as kl_divergence

# Import the khan_encryption_2 module from the specific path
import importlib.util
import sys

# Import the khan_encryption2 module from a specific path
module_name = "khan_encryption2.0"
file_path = "C:/Users/admin/Documents/GitHub/cyclic/khan_encryption_2.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

def generate_message(length, random_noise=False):
    if random_noise:
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    else:
        message = "This is an example of an information-rich message. " * (length // 50)
        return message[:length]

def calculate_entropy(message):
    if not message:
        return 0
    entropy = 0
    char_count = Counter(message)
    for count in char_count.values():
        p_x = count / len(message)
        entropy += - p_x * math.log2(p_x)
    return entropy

def mutual_information(message1, message2):
    joint_prob = Counter(zip(message1, message2))
    total_pairs = len(message1)
    mi = 0
    for (x, y), count in joint_prob.items():
        p_xy = count / total_pairs
        p_x = message1.count(x) / len(message1)
        p_y = message2.count(y) / len(message2)
        mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi

def measure_khan_encryption(plaintext, prime, start_position, superposition_sequence_length):
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    while sum(superposition_sequence) != 0:
        superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    z_value = superposition_sequence_length - 1
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
        plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length)
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence)
    return decrypted_text

def kl_divergence_metric(p, q):
    p_counts = Counter(p)
    q_counts = Counter(q)
    p_dist = np.array([p_counts[char] / len(p) for char in set(p + q)])
    q_dist = np.array([q_counts[char] / len(q) for char in set(p + q)])
    return kl_divergence(p_dist, q_dist)

def simulate_entropy_measurements(iterations=100):
    cyclic_prime = 1051
    start_position = 1
    superposition_sequence_length = 10
    entropy_info, entropy_noise = [], []
    kl_info, kl_noise = [], []
    mi_info, mi_noise = [], []

    for _ in range(iterations):
        plaintext_info = generate_message(128)
        plaintext_noise = generate_message(128, random_noise=True)

        decrypted_info = measure_khan_encryption(plaintext_info, cyclic_prime, start_position, superposition_sequence_length)
        decrypted_noise = measure_khan_encryption(plaintext_noise, cyclic_prime, start_position, superposition_sequence_length)

        entropy_info.append((calculate_entropy(plaintext_info), calculate_entropy(decrypted_info)))
        entropy_noise.append((calculate_entropy(plaintext_noise), calculate_entropy(decrypted_noise)))

        kl_info.append(kl_divergence_metric(plaintext_info, decrypted_info))
        kl_noise.append(kl_divergence_metric(plaintext_noise, decrypted_noise))

        mi_info.append(mutual_information(plaintext_info, decrypted_info))
        mi_noise.append(mutual_information(plaintext_noise, decrypted_noise))

    return entropy_info, entropy_noise, kl_info, kl_noise, mi_info, mi_noise

def main():
    iterations = 100
    entropy_info, entropy_noise, kl_info, kl_noise, mi_info, mi_noise = simulate_entropy_measurements(iterations)

    avg_entropy_info = np.mean([x[1] - x[0] for x in entropy_info])
    avg_entropy_noise = np.mean([x[1] - x[0] for x in entropy_noise])
    avg_kl_info = np.mean(kl_info)
    avg_kl_noise = np.mean(kl_noise)
    avg_mi_info = np.mean(mi_info)
    avg_mi_noise = np.mean(mi_noise)

    print("Average Entropy Difference (Information-Rich):", avg_entropy_info)
    print("Average Entropy Difference (Random Noise):", avg_entropy_noise)
    print("Average KL-Divergence (Information-Rich):", avg_kl_info)
    print("Average KL-Divergence (Random Noise):", avg_kl_noise)
    print("Average Mutual Information (Information-Rich):", avg_mi_info)
    print("Average Mutual Information (Random Noise):", avg_mi_noise)

if __name__ == "__main__":
    main()
