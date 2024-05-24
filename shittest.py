import time
import random
import string
import importlib.util
import sys

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

def measure_khan_encryption(plaintext, start_position, superposition_sequence_length):
    cyclic_prime = 167
    cyclic_sequence = '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'[:166]

    # Generate superposition sequence
    superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]
    while sum(superposition_sequence) != 0:
        superposition_sequence = [random.choice([-1, 1]) for _ in range(superposition_sequence_length)]

    # Calculate z_value
    z_value = calculate_z_value(superposition_sequence_length)

    # Encrypt the plaintext
    start_time = time.time()
    ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, start_position)
    encryption_time = time.time() - start_time

    # Decrypt the ciphertext
    start_time = time.time()
    decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time, decrypted_text, start_position, superposition_sequence, z_value

def main():
    # Get user input for private keys
    start_position, superposition_sequence_length = get_user_input()

    # Generate random plaintext
    plaintext = ke.generate_plaintext(128)

    # Measure encryption and decryption
    encryption_time, decryption_time, decrypted_text, start_position, superposition_sequence, z_value = measure_khan_encryption(plaintext, start_position, superposition_sequence_length)

    # Display results
    print("\nEncryption and Decryption Results:")
    print("Original Plaintext:", plaintext)
    print("Decrypted Plaintext:", decrypted_text)
    print(f"Encryption Time: {encryption_time} seconds")
    print(f"Decryption Time: {decryption_time} seconds")
    print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")

    # Display private and public key information
    print("\nKey Information:")
    print("User 1 Private Key (Starting Dial Position):", start_position)
    print("User 2 Private Key (Superposition Sequence and Z-Value):", superposition_sequence, z_value)
    print("Public Key (Cyclic Prime and Cyclic Sequence):", 167, '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'[:166])

if __name__ == "__main__":
    main()
