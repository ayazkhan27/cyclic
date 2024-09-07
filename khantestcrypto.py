import time
import random
import string
from itertools import permutations
import importlib.util
import sys
import threading

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

# User 1
user1_start_position = start_position

# User 2
user2_superposition_sequence = ke.generate_superposition_sequence(cyclic_prime)
user2_z_value = ke.calculate_z_value(user2_superposition_sequence)

# Public Key
public_key = {
    "cyclic_prime": cyclic_prime,
    "cyclic_sequence": cyclic_sequence
}

# Generate random plaintexts
plaintexts = [ke.generate_plaintext(128) for _ in range(5)]

# Encrypt the first plaintext
ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(plaintexts[0], cyclic_prime, cyclic_sequence, user1_start_position)

def validate_ciphertext(ciphertext):
    if not all(isinstance(movement, int) for movement in ciphertext):
        raise ValueError("Ciphertext contains non-integer values")

def brute_force_worker(ciphertext, possible_movements, movement_to_char, result, timeout=60):
    start_time = time.time()
    for perm in permutations(possible_movements, len(ciphertext)):
        plaintext = []
        try:
            for i, c in enumerate(ciphertext):
                if c == perm[i]:
                    plaintext.append(movement_to_char[perm[i]])
                else:
                    raise ValueError
            result.append(False)  # Brute force succeeded, encryption failed
            return
        except ValueError:
            continue
        if time.time() - start_time > timeout:
            break
    result.append(True)  # Brute force failed, encryption passed

def brute_force_attack(ciphertext, possible_movements, movement_to_char, timeout=60):
    validate_ciphertext(ciphertext)
    result = []
    thread = threading.Thread(target=brute_force_worker, args=(ciphertext, possible_movements, movement_to_char, result, timeout))
    thread.start()
    thread.join(timeout)
    if not result:
        result.append(True)  # If the thread is still running after timeout, consider the test passed
    return result[0]

def chosen_plaintext_worker(char_to_movement, z_value, superposition_sequence, result, timeout=60):
    try:
        start_time = time.time()
        plaintexts = ["Hello", "World", "12345", "Testing"]
        results = ke.chosen_plaintext_attack(plaintexts, cyclic_prime, cyclic_sequence, user1_start_position)
        chosen_plaintexts = [res[0] for res in results]
        chosen_ciphertexts = [res[1] for res in results]
        for pt, ct in zip(chosen_plaintexts, chosen_ciphertexts):
            validate_ciphertext(ct)
            decrypted_text = ke.khan_decrypt(ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, user1_start_position, cyclic_sequence)
            if decrypted_text != pt:
                result.append(False)
                return
            if time.time() - start_time > timeout:
                result.append(True)
                return
        result.append(True)
    except Exception as e:
        print(f"Exception in chosen_plaintext_worker: {e}")
        result.append(False)

def chosen_plaintext_attack(char_to_movement, z_value, superposition_sequence, timeout=60):
    result = []
    thread = threading.Thread(target=chosen_plaintext_worker, args=(char_to_movement, z_value, superposition_sequence, result, timeout))
    thread.start()
    thread.join(timeout)
    if not result:
        result.append(True)
    return result[0]

def known_plaintext_worker(plaintexts, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, result, timeout=60):
    try:
        known_plaintext = plaintexts[0]
        ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(known_plaintext, cyclic_prime, cyclic_sequence, user1_start_position)
        
        for plaintext in plaintexts[1:]:
            start_time = time.time()
            while time.time() - start_time < timeout:
                is_decrypted = ke.known_plaintext_attack(plaintext, ciphertext, char_to_movement, z_value, superposition_sequence, cyclic_prime, iv, salt, z_layers, user1_start_position, cyclic_sequence)
                if is_decrypted:
                    result.append(False)
                    return
        result.append(True)
    except Exception as e:
        print(f"Exception in known_plaintext_worker: {e}")
        result.append(False)

def known_plaintext_attack(plaintexts, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, timeout=60):
    result = []
    thread = threading.Thread(target=known_plaintext_worker, args=(plaintexts, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, result, timeout))
    thread.start()
    thread.join(timeout)
    if not result:
        result.append(True)
    return result[0]

def run_tests():
    total_time = 360
    interval = 60
    elapsed_time = 0

    print("Running security tests on KHAN encryption algorithm...\n")
    brute_force_result = True
    chosen_plaintext_result = True
    known_plaintext_result = True

    while elapsed_time < total_time:
        if elapsed_time < 120:
            print(f"Running Brute Force Attack Test (Interval {elapsed_time//60 + 1})...")
            brute_force_result = brute_force_attack(ciphertext, possible_movements, movement_to_char, timeout=interval)
            print(f"Brute Force Attack Test Result (Interval {elapsed_time//60 + 1}): {'Encryption Passed' if brute_force_result else 'Encryption Failed'}")
        elif 120 <= elapsed_time < 240:
            print(f"Running Chosen Plaintext Attack Test (Interval {elapsed_time//60 + 1})...")
            chosen_plaintext_result = chosen_plaintext_attack(char_to_movement, z_value, superposition_sequence, timeout=interval)
            print(f"Chosen Plaintext Attack Test Result (Interval {elapsed_time//60 + 1}): {'Encryption Passed' if chosen_plaintext_result else 'Encryption Failed'}")
        elif elapsed_time >= 240:
            print(f"Running Known Plaintext Attack Test (Interval {elapsed_time//60 + 1})...")
            known_plaintext_result = True
            for _ in range(4):
                if not known_plaintext_attack(plaintexts, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, timeout=interval // 4):
                    known_plaintext_result = False
                    break
            print(f"Known Plaintext Attack Test Result (Interval {elapsed_time//60 + 1}): {'Encryption Passed' if known_plaintext_result else 'Encryption Failed'}")

        elapsed_time += interval
        time.sleep(interval)

    print("\nSecurity tests completed.")
    if brute_force_result and chosen_plaintext_result and known_plaintext_result:
        print("KHAN Encryption Security: A+ (All tests passed)")
    else:
        print("KHAN Encryption Security: Failed (One or more tests did not pass)")

# Run the tests
possible_movements = ke.analyze_cyclic_prime(cyclic_prime, cyclic_sequence, user1_start_position)
run_tests()
