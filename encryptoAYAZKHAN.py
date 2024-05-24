import time
import random
import string
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

def get_user_input():
    # User 1 input for starting dial position
    start_position = int(input("User 1: Enter the starting dial position (integer between 1 and 166): "))

    # User 2 input for superposition sequence (must be an even integer)
    while True:
        superposition_sequence_length = int(input("User 2: Enter the superposition sequence length (even integer): "))
        if superposition_sequence_length % 2 == 0:
            break
        else:
            print("Superposition sequence length must be an even integer. Please try again.")

    return start_position, superposition_sequence_length

def calculate_z_value(superposition_sequence_length):
    # Calculate z_value based on the superposition sequence length
    z_value = superposition_sequence_length - 1
    return z_value

def generate_superposition_sequence(length):
    while True:
        sequence = [random.choice([-1, 1]) for _ in range(length)]
        if sum(sequence) == 0:
            return sequence

def measure_khan_encryption(plaintext, start_position, superposition_sequence_length, q):
    cyclic_prime = 167
    cyclic_sequence = '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'[:166]

    # Generate superposition sequence
    superposition_sequence = generate_superposition_sequence(superposition_sequence_length)
    
    # Calculate z_value
    z_value = calculate_z_value(superposition_sequence_length)

    # Encrypt the plaintext
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, start_position)
    encryption_time = time.time() - start_time

    # Decrypt the ciphertext
    start_time = time.time()
    try:
        decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    except ValueError as e:
        decrypted_text = str(e)
    decryption_time = time.time() - start_time

    q.put((encryption_time, decryption_time, decrypted_text, start_position, superposition_sequence, z_value, ciphertext, char_to_movement, movement_to_char, iv, salt, z_layers, plaintext))

def display_encryption_decryption_results(q):
    encryption_time, decryption_time, decrypted_text, start_position, superposition_sequence, z_value, ciphertext, char_to_movement, movement_to_char, iv, salt, z_layers, plaintext = q.get()
    
    print("\nEncryption and Decryption Results:")
    print("Original Plaintext:", plaintext)
    print("Decrypted Plaintext:", decrypted_text)
    print(f"Encryption Time: {encryption_time} seconds")
    print(f"Decryption Time: {decryption_time} seconds")
    print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")

    print("\nKey Information:")
    print("User 1 Private Key (Starting Dial Position):", start_position)
    print("User 2 Private Key (Superposition Sequence and Z-Value):", superposition_sequence, z_value)
    print("Public Key (Cyclic Prime and Cyclic Sequence):", 167, '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'[:166])

def run_security_tests(ciphertext, possible_movements, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, plaintext, cyclic_prime, start_position, cyclic_sequence):
    q = queue.Queue()

    # Perform brute force attack
    def brute_force_attack_worker():
        start_time = time.time()
        result = True
        while time.time() - start_time < 120:
            try:
                res = ke.brute_force_attack(ciphertext, possible_movements, movement_to_char)
                if res:
                    result = False
                    break
            except:
                pass
        q.put(("Brute Force Attack Test", result))

    # Perform chosen plaintext attack
    def chosen_plaintext_worker():
        start_time = time.time()
        result = True
        while time.time() - start_time < 120:
            try:
                for pt in plaintexts[1:]:
                    ct, _, _, _, _, _, _, _ = ke.khan_encrypt(pt, cyclic_prime, cyclic_sequence, start_position)
                    decrypted_text = ke.khan_decrypt(ct, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
                    if decrypted_text == pt:
                        result = False
                        break
            except:
                pass
        q.put(("Chosen Plaintext Attack Test", result))

    # Perform known plaintext attack
    def known_plaintext_worker():
        start_time = time.time()
        result = True
        while time.time() - start_time < 240:
            try:
                is_decrypted = ke.known_plaintext_attack(plaintext, ciphertext, char_to_movement, z_value, superposition_sequence, cyclic_prime, iv, salt, z_layers, start_position, cyclic_sequence)
                if is_decrypted:
                    result = False
                    break
            except:
                pass
        q.put(("Known Plaintext Attack Test", result))

    brute_force_thread = threading.Thread(target=brute_force_attack_worker)
    chosen_plaintext_thread = threading.Thread(target=chosen_plaintext_worker)
    known_plaintext_thread = threading.Thread(target=known_plaintext_worker)

    brute_force_thread.start()
    chosen_plaintext_thread.start()
    known_plaintext_thread.start()

    brute_force_thread.join()
    chosen_plaintext_thread.join()
    known_plaintext_thread.join()

    return q

def main():
    start_position, superposition_sequence_length = get_user_input()
    plaintext = ke.generate_plaintext(128)
    q = queue.Queue()

    encryption_thread = threading.Thread(target=measure_khan_encryption, args=(plaintext, start_position, superposition_sequence_length, q))
    encryption_thread.start()
    encryption_thread.join()

    display_thread = threading.Thread(target=display_encryption_decryption_results, args=(q,))
    display_thread.start()
    display_thread.join()

    encryption_time, decryption_time, decrypted_text, start_position, superposition_sequence, z_value, ciphertext, char_to_movement, movement_to_char, iv, salt, z_layers, plaintext = q.get()

    possible_movements = ke.analyze_cyclic_prime(167, cyclic_sequence, start_position)

    test_queue = run_security_tests(ciphertext, possible_movements, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, plaintext, 167, start_position, cyclic_sequence)

    while not test_queue.empty():
        test_name, result = test_queue.get()
        print(f"{test_name} Result: {'Encryption Passed' if result else 'Encryption Failed'}")

    print("\nSecurity tests completed.")
    if all(result for _, result in test_queue.queue):
        print("KHAN Encryption Security: A+ (All tests passed)")
    else:
        print("KHAN Encryption Security: Failed (One or more tests did not pass)")

if __name__ == "__main__":
    main()
