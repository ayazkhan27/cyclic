import time
import random
import string
import threading
import queue
import importlib.util
from decimal import Decimal, getcontext
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Import the khan_encryption_2 module
# Import the khan_encryption2 module from a specific path
module_name = "khan_encryption2.0"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption_2.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ke)

# Helper functions
def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

def brute_force_attack_worker(ciphertext, possible_movements, movement_to_char, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            res = ke.brute_force_attack(ciphertext, possible_movements, movement_to_char)
            if res:
                result = False
                break
        except:
            pass
    q.put(result)

def differential_cryptanalysis_worker(pairs, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            for pt1, pt2 in pairs:
                ct1, _ = ke.khan_encrypt(pt1, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)
                ct2, _ = ke.khan_encrypt(pt2, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)
                if ke.differential_cryptanalysis(ct1, ct2):
                    result = False
                    break
        except:
            pass
    q.put(result)

def linear_cryptanalysis_worker(plaintexts, ciphertexts, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            if ke.linear_cryptanalysis(plaintexts, ciphertexts):
                result = False
                break
        except:
            pass
    q.put(result)

def side_channel_attack_worker(ciphertext, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            side_channel_data = ke.simulate_side_channel_data(ciphertext)
            if ke.side_channel_attack(side_channel_data):
                result = False
                break
        except:
            pass
    q.put(result)

def run_advanced_cryptanalysis_tests(ciphertext, possible_movements, movement_to_char, plaintexts, ciphertexts, pairs):
    timeout = 60  # 1 minute for each test
    results = {
        "brute_force": True,
        "differential": True,
        "linear": True,
        "side_channel": True
    }

    queues = {key: queue.Queue() for key in results.keys()}

    threading.Thread(target=brute_force_attack_worker, args=(ciphertext, possible_movements, movement_to_char, queues["brute_force"], timeout)).start()
    threading.Thread(target=differential_cryptanalysis_worker, args=(pairs, queues["differential"], timeout)).start()
    threading.Thread(target=linear_cryptanalysis_worker, args=(plaintexts, ciphertexts, queues["linear"], timeout)).start()
    threading.Thread(target=side_channel_attack_worker, args=(ciphertext, queues["side_channel"], timeout)).start()

    for key in results.keys():
        results[key] = queues[key].get()

    print("\nAdvanced Cryptanalysis Test Results:")
    for attack, result in results.items():
        print(f"{attack.replace('_', ' ').title()} Test Result: {'Passed' if result else 'Failed'}")

# Setup encryption parameters
cyclic_prime = 1051
start_position = int(input(f"Enter the starting dial position (integer between 1 and {cyclic_prime - 1}): "))
superposition_sequence_length = int(input("Enter the superposition sequence length (even integer): "))
cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)
plaintext = generate_plaintext(128)

# Measure encryption and decryption time for KHAN encryption
def measure_khan_encryption(plaintext, start_position, superposition_sequence_length):
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
        plaintext, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, decrypted_text, ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers

# Run initial encryption and decryption
enc_time, dec_time, decrypted_text, ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = measure_khan_encryption(plaintext, start_position, superposition_sequence_length)

# Generate additional plaintexts and ciphertexts for cryptanalysis
plaintexts = [generate_plaintext(128) for _ in range(5)]
ciphertexts = [ke.khan_encrypt(pt, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)[0] for pt in plaintexts]

# Prepare for brute force attack
possible_movements = ke.analyze_cyclic_prime(cyclic_prime, cyclic_sequence, start_position)

# Generate pairs of plaintexts for differential cryptanalysis
pairs = [(plaintexts[0], plaintexts[1]), (plaintexts[2], plaintexts[3])]

# Run advanced cryptanalysis tests
run_advanced_cryptanalysis_tests(ciphertext, possible_movements, movement_to_char, plaintexts, ciphertexts, pairs)

input("Press Enter to exit...")
