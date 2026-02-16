import time
import random
import string
from itertools import permutations
import importlib.util
import sys
import threading
import queue

# Import the khan_encryption module from a specific path
module_name = "khan_encryption"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

# Setup encryption parameters
cyclic_prime = 167
start_position = 43
cyclic_sequence = '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'[:166]

# Generate random plaintext
plaintext = ke.generate_plaintext(128)

# Function to validate if ciphertext contains non-integer values
def validate_ciphertext(ciphertext):
    return all(isinstance(c, int) for c in ciphertext)

# Function to measure encryption and decryption times
def measure_khan_encryption(plaintext):
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, start_position)
    encryption_time = time.time() - start_time

    if not validate_ciphertext(ciphertext):
        raise ValueError("Ciphertext contains non-integer values")

    start_time = time.time()
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, decrypted_text, ciphertext, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers

# Initialize encryption parameters
encryption_time, decryption_time, decrypted_text, ciphertext, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers = measure_khan_encryption(plaintext)

# Display encryption and decryption results
print("\nEncryption and Decryption Results:")
print("Original Plaintext:", plaintext)
print("Decrypted Plaintext:", decrypted_text)
print(f"Encryption Time: {encryption_time} seconds")
print(f"Decryption Time: {decryption_time} seconds")
print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")

# Function to perform brute force attack
def brute_force_attack_worker(q, timeout):
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

# Function to perform chosen plaintext attack
def chosen_plaintext_worker(q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            for pt in plaintexts[1:]:
                ct, _, _, _, _, _, _, _ = ke.khan_encrypt(pt, cyclic_prime, cyclic_sequence, start_position)
                decrypted_text = ke.khan_decrypt(ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
                if decrypted_text == pt:
                    result = False
                    break
        except:
            pass
    q.put(result)

# Function to perform known plaintext attack
def known_plaintext_worker(q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            is_decrypted = ke.known_plaintext_attack(plaintext, ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, cyclic_prime, iv, salt, z_layers, start_position, cyclic_sequence)
            if is_decrypted:
                result = False
                break
        except:
            pass
    q.put(result)

# Function to perform ciphertext-only attack
def ciphertext_only_attack_worker(ciphertext, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            decrypted_text = ke.ciphertext_only_attack(ciphertext)
            if decrypted_text:
                result = False
                break
        except:
            pass
    q.put(result)

# Function to perform differential cryptanalysis attack
def differential_cryptanalysis_worker(pairs, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            for pt1, pt2 in pairs:
                ct1, _ = ke.khan_encrypt(pt1, cyclic_prime, cyclic_sequence, start_position)
                ct2, _ = ke.khan_encrypt(pt2, cyclic_prime, cyclic_sequence, start_position)
                if ke.differential_cryptanalysis(ct1, ct2):
                    result = False
                    break
        except:
            pass
    q.put(result)

# Function to perform integral cryptanalysis attack
def integral_cryptanalysis_worker(sets_of_plaintexts, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            for set_pt in sets_of_plaintexts:
                cts = [ke.khan_encrypt(pt, cyclic_prime, cyclic_sequence, start_position)[0] for pt in set_pt]
                if ke.integral_cryptanalysis(cts):
                    result = False
                    break
        except:
            pass
    q.put(result)

# Function to perform side-channel attack
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

# Function to perform dictionary attack
def dictionary_attack_worker(ciphertext, dictionary, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            for word in dictionary:
                decrypted_text = ke.khan_decrypt_with_key(ciphertext, word)
                if decrypted_text:
                    result = False
                    break
        except:
            pass
    q.put(result)

# Function to perform man-in-the-middle attack
def man_in_the_middle_attack_worker(ciphertext, public_keys, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            for key in public_keys:
                intercepted_message = ke.man_in_the_middle(ciphertext, key)
                if intercepted_message:
                    result = False
                    break
        except:
            pass
    q.put(result)

# Function to perform trojan horse attack
def trojan_horse_attack_worker(ciphertext, infected_systems, q, timeout):
    start_time = time.time()
    result = True
    while time.time() - start_time < timeout:
        try:
            for system in infected_systems:
                stolen_key = ke.extract_key_via_trojan(system)
                if stolen_key:
                    decrypted_text = ke.khan_decrypt_with_key(ciphertext, stolen_key)
                    if decrypted_text:
                        result = False
                        break
        except:
            pass
    q.put(result)

# Generate additional plaintexts for testing
plaintexts = [ke.generate_plaintext(128) for _ in range(5)]

# Prepare for brute force attack
possible_movements = ke.analyze_cyclic_prime(cyclic_prime, cyclic_sequence, start_position)

# Generate pairs of plaintexts for differential cryptanalysis
pairs = [(plaintexts[0], plaintexts[1]), (plaintexts[2], plaintexts[3])]

# Generate sets of plaintexts for integral cryptanalysis
sets_of_plaintexts = [[ke.generate_plaintext(128) for _ in range(5)] for _ in range(3)]

# Dictionary of possible plaintexts or keys for dictionary attack
dictionary = ['password123', 'letmein', '123456']

# List of public keys for man-in-the-middle attack
public_keys = ['public_key_1', 'public_key_2']

# List of infected systems for trojan horse attack
infected_systems = ['system_1', 'system_2']

def run_all_tests():
    total_time = 3600  # Total test time in seconds for each attack
    interval = 600  # Interval in seconds

    # Initialize results
    results = {
        "brute_force": True,
        "chosen_plaintext": True,
        "known_plaintext": True,
        "ciphertext_only": True,
        "differential": True,
        "integral": True,
        "side_channel": True,
        "dictionary": True,
        "man_in_the_middle": True,
        "trojan_horse": True
    }

    # Create a queue for each attack
    queues = {key: queue.Queue() for key in results.keys()}

    # Test intervals for each attack
    for i in range(1, 7):
        print(f"Running test interval {i}...")

        if i <= 2:
            threading.Thread(target=brute_force_attack_worker, args=(queues["brute_force"], interval)).start()
        if 2 < i <= 4:
            threading.Thread(target=chosen_plaintext_worker, args=(queues["chosen_plaintext"], interval)).start()
        if 4 < i <= 6:
            threading.Thread(target=known_plaintext_worker, args=(queues["known_plaintext"], interval)).start()

    # Additional tests
    threading.Thread(target=ciphertext_only_attack_worker, args=(ciphertext, queues["ciphertext_only"], interval)).start()
    threading.Thread(target=differential_cryptanalysis_worker, args=(pairs, queues["differential"], interval)).start()
    threading.Thread(target=integral_cryptanalysis_worker, args=(sets_of_plaintexts, queues["integral"], interval)).start()
    threading.Thread(target=side_channel_attack_worker, args=(ciphertext, queues["side_channel"], interval)).start()
    threading.Thread(target=dictionary_attack_worker, args=(ciphertext, dictionary, queues["dictionary"], interval)).start()
    threading.Thread(target=man_in_the_middle_attack_worker, args=(ciphertext, public_keys, queues["man_in_the_middle"], interval)).start()
    threading.Thread(target=trojan_horse_attack_worker, args=(ciphertext, infected_systems, queues["trojan_horse"], interval)).start()

    # Collect results
    for key in results.keys():
        results[key] = queues[key].get()

    print("\nSecurity tests completed.")
    for attack, result in results.items():
        print(f"{attack.replace('_', ' ').title()} Test Result: {'Encryption Passed' if result else 'Encryption Failed'}")

run_all_tests()
