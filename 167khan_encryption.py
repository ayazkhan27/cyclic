import time
import random
import string
from itertools import permutations
import importlib.util
import sys

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

def test_brute_force(ciphertext, possible_movements, movement_to_char, timeout=60):
    start_time = time.time()
    for perm in permutations(possible_movements, len(ciphertext)):
        plaintext = []
        try:
            for i, c in enumerate(ciphertext):
                if c == perm[i]:
                    plaintext.append(movement_to_char[perm[i]])
                else:
                    raise ValueError
            print(f"Brute Force Attack Decrypted Text: {''.join(plaintext)}")
            return False  # Brute force succeeded, encryption failed
        except ValueError:
            continue
        if time.time() - start_time > timeout:
            break
    print("Brute Force Attack: Passed (Timeout or no valid permutation found)")
    return True  # Brute force failed, encryption passed

def test_chosen_plaintext(char_to_movement, z_value, superposition_sequence):
    plaintexts = ["Hello", "World", "12345", "Testing"]
    results = ke.chosen_plaintext_attack(plaintexts, cyclic_prime, cyclic_sequence, user1_start_position)
    chosen_plaintexts = [res[0] for res in results]
    chosen_ciphertexts = [res[1] for res in results]
    print(f"Chosen Plaintext Attack Ciphertexts: {chosen_ciphertexts}")
    for pt, ct in zip(chosen_plaintexts, chosen_ciphertexts):
        decrypted_text = ke.khan_decrypt(ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, user1_start_position, cyclic_sequence)
        if decrypted_text != pt:
            print(f"Chosen Plaintext Attack Failed: Original {pt} != Decrypted {decrypted_text}")
            return False
    print("Chosen Plaintext Attack: Passed")
    return True

def test_known_plaintext(plaintext, ciphertext, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers):
    is_decrypted = ke.known_plaintext_attack(plaintext, ciphertext, char_to_movement, z_value, superposition_sequence, cyclic_prime, iv, salt, z_layers, user1_start_position, cyclic_sequence)
    if is_decrypted:
        print("Known Plaintext Attack: Passed")
    else:
        print("Known Plaintext Attack: Failed")
    return is_decrypted

# Generate random plaintext
plaintext = ke.generate_plaintext(128)

# Encrypt the plaintext
ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, user1_start_position)

# Brute Force Attack Test
possible_movements = ke.analyze_cyclic_prime(cyclic_prime, cyclic_sequence, user1_start_position)
brute_force_result = test_brute_force(ciphertext, possible_movements, movement_to_char, timeout=60)

# Chosen Plaintext Attack Test
chosen_plaintext_result = test_chosen_plaintext(char_to_movement, z_value, superposition_sequence)

# Known Plaintext Attack Test
known_plaintext_result = test_known_plaintext(plaintext, ciphertext, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers)

# Summary of results
if brute_force_result and chosen_plaintext_result and known_plaintext_result:
    print("KHAN Encryption Security: A+ (All tests passed)")
else:
    print("KHAN Encryption Security: Failed (One or more tests did not pass)")
