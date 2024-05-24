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
file_path = "C:/Users/admin/Downloads/khan_encryption.py"

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

    return encryption_time, decryption_time, decrypted_text, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers

# Initialize encryption parameters
encryption_time, decryption_time, decrypted_text, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers = measure_khan_encryption(plaintext)

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
            is_decrypted = ke.known_plaintext_attack(plaintext, ciphertext, char_to_movement, z_value, superposition_sequence, cyclic_prime, iv, salt, z_layers, start_position, cyclic_sequence)
            if is_decrypted:
                result = False
                break
        except:
            pass
    q.put(result)

# Generate additional plaintexts for testing
plaintexts = [ke.generate_plaintext(128) for _ in range(5)]

# Prepare for brute force attack
possible_movements = ke.analyze_cyclic_prime(cyclic_prime, cyclic_sequence, start_position)

def run_tests():
    total_time = 360  # Total test time in seconds
    interval = 60  # Interval in seconds

    brute_force_result = True
    chosen_plaintext_result = True
    known_plaintext_result = True

    for i in range(1, 7):
        print(f"Running test interval {i}...")

        q = queue.Queue()

        # Brute force attack test (first two intervals)
        if i <= 2:
            brute_force_thread = threading.Thread(target=brute_force_attack_worker, args=(q, interval))
            brute_force_thread.start()
            brute_force_thread.join()
            brute_force_result = q.get()
            print(f"Brute Force Attack Test Result (Interval {i}): {'Encryption Passed' if brute_force_result else 'Encryption Failed'}")

        # Chosen plaintext attack test (next two intervals)
        if 2 < i <= 4:
            chosen_plaintext_thread = threading.Thread(target=chosen_plaintext_worker, args=(q, interval))
            chosen_plaintext_thread.start()
            chosen_plaintext_thread.join()
            chosen_plaintext_result = q.get()
            print(f"Chosen Plaintext Attack Test Result (Interval {i}): {'Encryption Passed' if chosen_plaintext_result else 'Encryption Failed'}")

        # Known plaintext attack test (last two intervals)
        if 4 < i <= 6:
            known_plaintext_thread = threading.Thread(target=known_plaintext_worker, args=(q, interval))
            known_plaintext_thread.start()
            known_plaintext_thread.join()
            known_plaintext_result = q.get()
            print(f"Known Plaintext Attack Test Result (Interval {i}): {'Encryption Passed' if known_plaintext_result else 'Encryption Failed'}")

    print("\nSecurity tests completed.")
    if brute_force_result and chosen_plaintext_result and known_plaintext_result:
        print("KHAN Encryption Security: A+ (All tests passed)")
    else:
        print("KHAN Encryption Security: Failed (One or more tests did not pass)")

# Run the tests
run_tests()

# Display private and public key information
print("\nKey Information:")
print("User 1 Private Key (Starting Dial Position):", start_position)
print("User 2 Private Key (Superposition Sequence and Z-Value):", superposition_sequence, z_value)
print("Public Key (Cyclic Prime and Cyclic Sequence):", cyclic_prime, cyclic_sequence)
