import time
import random
import string
import threading
import queue
from itertools import permutations  # Import permutations
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Import custom KHAN encryption module from the GitHub repo
import importlib.util
import sys
# Load the KHAN encryption module
module_name = "khan_encryption"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption.py"
spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

# Setup encryption parameters
cyclic_prime = 1051
start_position = random.randint(1, cyclic_prime - 1)
cyclic_sequence = ke.generate_plaintext(cyclic_prime - 1)  # Assuming you use plaintext as cyclic sequence

# Function to generate random plaintext
def generate_plaintext(length=128):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# Function to validate if ciphertext contains non-integer values
def validate_ciphertext(ciphertext):
    return all(isinstance(c, int) for c in ciphertext)

# Function to measure encryption and decryption times
def measure_khan_encryption(plaintext):
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
        plaintext, cyclic_prime, cyclic_sequence, start_position)
    encryption_time = time.time() - start_time

    if not validate_ciphertext(ciphertext):
        raise ValueError("Ciphertext contains non-integer values")

    start_time = time.time()
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, decrypted_text, ciphertext, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers

# Perform various cryptanalytic attacks
def perform_cryptanalysis_tests(plaintext, ciphertext, char_to_movement, z_value, superposition_sequence, iv, salt, z_layers):
    results = {
        "brute_force": True,
        "chosen_plaintext": True,
        "known_plaintext": True,
    }

    def brute_force_attack_worker(q, timeout):
        start_time = time.time()
        result = True
        while time.time() - start_time < timeout:
            try:
                possible_movements = ke.analyze_cyclic_prime(cyclic_prime, cyclic_sequence, start_position)
                res = ke.brute_force_attack(ciphertext, possible_movements, char_to_movement)
                if res:
                    result = False
                    break
            except Exception as e:
                print(f"Brute force attack error: {e}")
        q.put(result)

    def chosen_plaintext_worker(q, timeout):
        start_time = time.time()
        result = True
        while time.time() - start_time < timeout:
            try:
                for pt in [generate_plaintext() for _ in range(5)]:
                    ct, _, _, _, _, _, _, _ = ke.khan_encrypt(pt, cyclic_prime, cyclic_sequence, start_position)
                    decrypted_text = ke.khan_decrypt(ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
                    if decrypted_text == pt:
                        result = False
                        break
            except Exception as e:
                print(f"Chosen plaintext attack error: {e}")
        q.put(result)

    def known_plaintext_worker(q, timeout):
        start_time = time.time()
        result = True
        while time.time() - start_time < timeout:
            try:
                is_decrypted = ke.known_plaintext_attack(plaintext, ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, cyclic_prime, iv, salt, z_layers, start_position, cyclic_sequence)
                if is_decrypted:
                    result = False
                    break
            except Exception as e:
                print(f"Known plaintext attack error: {e}")
        q.put(result)

    # Initialize queues for threads
    attack_threads = {
        "brute_force": (threading.Thread(target=brute_force_attack_worker, args=(queue.Queue(), 60)), queue.Queue()),
        "chosen_plaintext": (threading.Thread(target=chosen_plaintext_worker, args=(queue.Queue(), 60)), queue.Queue()),
        "known_plaintext": (threading.Thread(target=known_plaintext_worker, args=(queue.Queue(), 60)), queue.Queue()),
    }

    # Start and join all threads
    for key, (thread, q) in attack_threads.items():
        thread.start()
        thread.join()
        results[key] = q.get()

    return results

# RSA Encryption Algorithm for comparison
def rsa_encrypt_decrypt():
    key = RSA.generate(2048)
    public_key = key.publickey()
    private_key = key

    cipher_rsa = PKCS1_OAEP.new(public_key)
    plaintext = generate_plaintext()
    start_time = time.time()
    ciphertext = cipher_rsa.encrypt(plaintext.encode())
    encryption_time = time.time() - start_time

    cipher_rsa = PKCS1_OAEP.new(private_key)
    start_time = time.time()
    decrypted_text = cipher_rsa.decrypt(ciphertext).decode()
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, len(ciphertext), plaintext == decrypted_text

# AES Encryption Algorithm for comparison
def aes_encrypt_decrypt():
    key = get_random_bytes(16)
    cipher_aes = AES.new(key, AES.MODE_CBC)
    iv = cipher_aes.iv

    plaintext = generate_plaintext()
    start_time = time.time()
    ciphertext = cipher_aes.encrypt(pad(plaintext.encode(), AES.block_size))
    encryption_time = time.time() - start_time

    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
    start_time = time.time()
    decrypted_text = unpad(cipher_aes.decrypt(ciphertext), AES.block_size).decode()
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, len(ciphertext), plaintext == decrypted_text

# Run tests and compare KHAN with other algorithms
def run_tests_and_compare():
    print("Starting KHAN Encryption Tests...")
    plaintext = generate_plaintext()
    khan_results = measure_khan_encryption(plaintext)
    cryptanalysis_results = perform_cryptanalysis_tests(plaintext, khan_results[3], khan_results[4], khan_results[5], khan_results[6], khan_results[7], khan_results[8], khan_results[9])

    # Check if KHAN passed all cryptanalysis tests
    if all(cryptanalysis_results.values()):
        print("KHAN Encryption passed all cryptanalysis tests. Ready for deployment.")
    else:
        print("KHAN Encryption failed one or more cryptanalysis tests. Not ready for deployment.")
        return

    # Compare with RSA, AES, etc.
    rsa_results = rsa_encrypt_decrypt()
    aes_results = aes_encrypt_decrypt()

    # Display results for comparison
    print("\nKHAN Encryption Results:")
    print(f"Encryption Time: {khan_results[0]:.6f} seconds, Decryption Time: {khan_results[1]:.6f} seconds")
    print(f"Ciphertext Length: {len(khan_results[3])}, Decryption Successful: {khan_results[2] == plaintext}")

    print("\nRSA Encryption Results:")
    print(f"Encryption Time: {rsa_results[0]:.6f} seconds, Decryption Time: {rsa_results[1]:.6f} seconds")
    print(f"Ciphertext Length: {rsa_results[2]}, Decryption Successful: {rsa_results[3]}")

    print("\nAES Encryption Results:")
    print(f"Encryption Time: {aes_results[0]:.6f} seconds, Decryption Time: {aes_results[1]:.6f} seconds")
    print(f"Ciphertext Length: {aes_results[2]}, Decryption Successful: {aes_results[3]}")

    # Final decision for deployment
    if khan_results[2] == plaintext and all(cryptanalysis_results.values()):
        print("\nAll tests passed successfully. KHAN Encryption is ready for deployment.")
    else:
        print("\nSome tests failed. Further review and improvements are needed before deployment.")

if __name__ == "__main__":
    run_tests_and_compare()
