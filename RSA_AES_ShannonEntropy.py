import numpy as np
import random
import string
from collections import Counter
from scipy.stats import entropy as kl_divergence
import matplotlib.pyplot as plt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Helper functions
def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

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

# AES encryption
def aes_encrypt(plaintext, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return cipher.iv + ciphertext

def aes_decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext[AES.block_size:]), AES.block_size)
    return plaintext.decode()

# RSA encryption
def rsa_encrypt(plaintext, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(plaintext.encode())

def rsa_decrypt(ciphertext, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(ciphertext).decode()

def simulate_entropy_measurements_rsa_aes(iterations=100):
    entropy_info_rsa, entropy_noise_rsa = [], []
    kl_info_rsa, kl_noise_rsa = [], []
    mi_info_rsa, mi_noise_rsa = [], []
    cse_info_rsa, cse_noise_rsa = [], []

    entropy_info_aes, entropy_noise_aes = [], []
    kl_info_aes, kl_noise_aes = [], []
    mi_info_aes, mi_noise_aes = [], []
    cse_info_aes, cse_noise_aes = [], []

    # RSA key generation
    rsa_key = RSA.generate(2048)
    rsa_public_key = rsa_key.publickey()
    rsa_private_key = rsa_key

    # AES key generation
    aes_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32)).encode()

    for _ in range(iterations):
        plaintext_info = generate_random_string(128)
        plaintext_noise = generate_random_string(128)

        # RSA encryption and decryption
        encrypted_info_rsa = rsa_encrypt(plaintext_info, rsa_public_key)
        encrypted_noise_rsa = rsa_encrypt(plaintext_noise, rsa_public_key)

        decrypted_info_rsa = rsa_decrypt(encrypted_info_rsa, rsa_private_key)
        decrypted_noise_rsa = rsa_decrypt(encrypted_noise_rsa, rsa_private_key)

        entropy_info_rsa.append((calculate_entropy(plaintext_info), calculate_entropy(decrypted_info_rsa)))
        entropy_noise_rsa.append((calculate_entropy(plaintext_noise), calculate_entropy(decrypted_noise_rsa)))

        kl_info_rsa.append(kl_divergence_metric(plaintext_info, decrypted_info_rsa))
        kl_noise_rsa.append(kl_divergence_metric(plaintext_noise, decrypted_noise_rsa))

        mi_info_rsa.append(mutual_information(plaintext_info, decrypted_info_rsa))
        mi_noise_rsa.append(mutual_information(plaintext_noise, decrypted_noise_rsa))

        cse_info_rsa.append((coherent_shannon_entropy(plaintext_info), coherent_shannon_entropy(decrypted_info_rsa)))
        cse_noise_rsa.append((coherent_shannon_entropy(plaintext_noise), coherent_shannon_entropy(decrypted_noise_rsa)))

        # AES encryption and decryption
        encrypted_info_aes = aes_encrypt(plaintext_info, aes_key)
        encrypted_noise_aes = aes_encrypt(plaintext_noise, aes_key)

        decrypted_info_aes = aes_decrypt(encrypted_info_aes, aes_key)
        decrypted_noise_aes = aes_decrypt(encrypted_noise_aes, aes_key)

        entropy_info_aes.append((calculate_entropy(plaintext_info), calculate_entropy(decrypted_info_aes)))
        entropy_noise_aes.append((calculate_entropy(plaintext_noise), calculate_entropy(decrypted_noise_aes)))

        kl_info_aes.append(kl_divergence_metric(plaintext_info, decrypted_info_aes))
        kl_noise_aes.append(kl_divergence_metric(plaintext_noise, decrypted_noise_aes))

        mi_info_aes.append(mutual_information(plaintext_info, decrypted_info_aes))
        mi_noise_aes.append(mutual_information(plaintext_noise, decrypted_noise_aes))

        cse_info_aes.append((coherent_shannon_entropy(plaintext_info), coherent_shannon_entropy(decrypted_info_aes)))
        cse_noise_aes.append((coherent_shannon_entropy(plaintext_noise), coherent_shannon_entropy(decrypted_noise_aes)))

    return (entropy_info_rsa, entropy_noise_rsa, kl_info_rsa, kl_noise_rsa, mi_info_rsa, mi_noise_rsa, cse_info_rsa, cse_noise_rsa,
            entropy_info_aes, entropy_noise_aes, kl_info_aes, kl_noise_aes, mi_info_aes, mi_noise_aes, cse_info_aes, cse_noise_aes)

def plot_results(entropy_info_rsa, entropy_noise_rsa, kl_info_rsa, kl_noise_rsa, mi_info_rsa, mi_noise_rsa, cse_info_rsa, cse_noise_rsa,
                 entropy_info_aes, entropy_noise_aes, kl_info_aes, kl_noise_aes, mi_info_aes, mi_noise_aes, cse_info_aes, cse_noise_aes):
    # Plotting entropy difference for RSA
    info_diffs_rsa = [x[1] - x[0] for x in entropy_info_rsa]
    noise_diffs_rsa = [x[1] - x[0] for x in entropy_noise_rsa]
    plt.figure(figsize=(10, 6))
    plt.boxplot([info_diffs_rsa, noise_diffs_rsa], tick_labels=['Information-Rich', 'Random Noise'])
    plt.title('Entropy Difference Comparison (RSA)')
    plt.ylabel('Entropy Difference')
    plt.show()

    # Plotting KL-divergence for RSA
    plt.figure(figsize=(10, 6))
    plt.boxplot([kl_info_rsa, kl_noise_rsa], tick_labels=['Information-Rich', 'Random Noise'])
    plt.title('KL-Divergence Comparison (RSA)')
    plt.ylabel('KL-Divergence')
    plt.show()

    # Plotting mutual information for RSA
    plt.figure(figsize=(10, 6))
    plt.plot(mi_info_rsa, label='Information-Rich')
    plt.plot(mi_noise_rsa, label='Random Noise')
    plt.title('Mutual Information over Iterations (RSA)')
    plt.xlabel('Iteration')
    plt.ylabel('Mutual Information')
    plt.legend()
    plt.show()

    # Plotting CSE difference for RSA
    info_diffs_rsa_cse = [x[1] - x[0] for x in cse_info_rsa]
    noise_diffs_rsa_cse = [x[1] - x[0] for x in cse_noise_rsa]
    plt.figure(figsize=(10, 6))
    plt.boxplot([info_diffs_rsa_cse, noise_diffs_rsa_cse], tick_labels=['Information-Rich', 'Random Noise'])
    plt.title('Coherent Shannon Entropy (CSE) Difference Comparison (RSA)')
    plt.ylabel('CSE Difference')
    plt.show()

    # Plotting entropy difference for AES
    info_diffs_aes = [x[1] - x[0] for x in entropy_info_aes]
    noise_diffs_aes = [x[1] - x[0] for x in entropy_noise_aes]
    plt.figure(figsize=(10, 6))
    plt.boxplot([info_diffs_aes, noise_diffs_aes], tick_labels=['Information-Rich', 'Random Noise'])
    plt.title('Entropy Difference Comparison (AES)')
    plt.ylabel('Entropy Difference')
    plt.show()

    # Plotting KL-divergence for AES
    plt.figure(figsize=(10, 6))
    plt.boxplot([kl_info_aes, kl_noise_aes], tick_labels=['Information-Rich', 'Random Noise'])
    plt.title('KL-Divergence Comparison (AES)')
    plt.ylabel('KL-Divergence')
    plt.show()

    # Plotting mutual information for AES
    plt.figure(figsize=(10, 6))
    plt.plot(mi_info_aes, label='Information-Rich')
    plt.plot(mi_noise_aes, label='Random Noise')
    plt.title('Mutual Information over Iterations (AES)')
    plt.xlabel('Iteration')
    plt.ylabel('Mutual Information')
    plt.legend()
    plt.show()

    # Plotting CSE difference for AES
    info_diffs_aes_cse = [x[1] - x[0] for x in cse_info_aes]
    noise_diffs_aes_cse = [x[1] - x[0] for x in cse_noise_aes]
    plt.figure(figsize=(10, 6))
    plt.boxplot([info_diffs_aes_cse, noise_diffs_aes_cse], tick_labels=['Information-Rich', 'Random Noise'])
    plt.title('Coherent Shannon Entropy (CSE) Difference Comparison (AES)')
    plt.ylabel('CSE Difference')
    plt.show()

def main():
    iterations = 100
    (entropy_info_rsa, entropy_noise_rsa, kl_info_rsa, kl_noise_rsa, mi_info_rsa, mi_noise_rsa, cse_info_rsa, cse_noise_rsa,
     entropy_info_aes, entropy_noise_aes, kl_info_aes, kl_noise_aes, mi_info_aes, mi_noise_aes, cse_info_aes, cse_noise_aes) = simulate_entropy_measurements_rsa_aes(iterations)

    avg_entropy_info_rsa = np.mean([x[1] - x[0] for x in entropy_info_rsa])
    avg_entropy_noise_rsa = np.mean([x[1] - x[0] for x in entropy_noise_rsa])
    avg_kl_info_rsa = np.mean(kl_info_rsa)
    avg_kl_noise_rsa = np.mean(kl_noise_rsa)
    avg_mi_info_rsa = np.mean(mi_info_rsa)
    avg_mi_noise_rsa = np.mean(mi_noise_rsa)
    avg_cse_info_rsa = np.mean([x[1] - x[0] for x in cse_info_rsa])
    avg_cse_noise_rsa = np.mean([x[1] - x[0] for x in cse_noise_rsa])

    avg_entropy_info_aes = np.mean([x[1] - x[0] for x in entropy_info_aes])
    avg_entropy_noise_aes = np.mean([x[1] - x[0] for x in entropy_noise_aes])
    avg_kl_info_aes = np.mean(kl_info_aes)
    avg_kl_noise_aes = np.mean(kl_noise_aes)
    avg_mi_info_aes = np.mean(mi_info_aes)
    avg_mi_noise_aes = np.mean(mi_noise_aes)
    avg_cse_info_aes = np.mean([x[1] - x[0] for x in cse_info_aes])
    avg_cse_noise_aes = np.mean([x[1] - x[0] for x in cse_noise_aes])

    print("RSA Encryption Results:")
    print("Average Entropy Difference (Information-Rich):", avg_entropy_info_rsa)
    print("Average Entropy Difference (Random Noise):", avg_entropy_noise_rsa)
    print("Average KL-Divergence (Information-Rich):", avg_kl_info_rsa)
    print("Average KL-Divergence (Random Noise):", avg_kl_noise_rsa)
    print("Average Mutual Information (Information-Rich):", avg_mi_info_rsa)
    print("Average Mutual Information (Random Noise):", avg_mi_noise_rsa)
    print("Average CSE Difference (Information-Rich):", avg_cse_info_rsa)
    print("Average CSE Difference (Random Noise):", avg_cse_noise_rsa)

    print("\nAES Encryption Results:")
    print("Average Entropy Difference (Information-Rich):", avg_entropy_info_aes)
    print("Average Entropy Difference (Random Noise):", avg_entropy_noise_aes)
    print("Average KL-Divergence (Information-Rich):", avg_kl_info_aes)
    print("Average KL-Divergence (Random Noise):", avg_kl_noise_aes)
    print("Average Mutual Information (Information-Rich):", avg_mi_info_aes)
    print("Average Mutual Information (Random Noise):", avg_mi_noise_aes)
    print("Average CSE Difference (Information-Rich):", avg_cse_info_aes)
    print("Average CSE Difference (Random Noise):", avg_cse_noise_aes)

    # Plotting the results
    plot_results(entropy_info_rsa, entropy_noise_rsa, kl_info_rsa, kl_noise_rsa, mi_info_rsa, mi_noise_rsa, cse_info_rsa, cse_noise_rsa,
                 entropy_info_aes, entropy_noise_aes, kl_info_aes, kl_noise_aes, mi_info_aes, mi_noise_aes, cse_info_aes, cse_noise_aes)

if __name__ == "__main__":
    main()
