import time
import importlib.util
import sys
from decimal import Decimal, getcontext

# Import the asymmetric_khan module from a specific path
module_name = "asymmetric_khan"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/asymmetricKHAN.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ak = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ak
spec.loader.exec_module(ak)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10  # Set precision to required length + buffer
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion[:length]

def get_user_input():
    # User 1 input for starting dial position
    start_position = int(input(f"User 1: Enter the starting dial position (integer between 1 and {cyclic_prime - 1}): "))

    # User 2 input for superposition sequence length (must be an even integer)
    while True:
        superposition_sequence_length = int(input("User 2: Enter the superposition sequence length (even integer): "))
        if superposition_sequence_length % 2 == 0:
            break
        else:
            print("Superposition sequence length must be an even integer. Please try again.")

    return start_position, superposition_sequence_length

def main():
    global cyclic_prime
    cyclic_prime = 1051  # Set the cyclic prime to 1051

    # Generate cyclic sequence
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Get user input for private keys
    start_position, superposition_sequence_length = get_user_input()

    # Generate public key
    public_key = (cyclic_prime, cyclic_sequence)

    # Generate random plaintext
    plaintext = ak.generate_plaintext(128)

    # Measure encryption
    start_time = time.time()
    ciphertext, iv, salt, z_layers = ak.khan_encrypt(plaintext, public_key)
    encryption_time = time.time() - start_time

    # Measure decryption
    start_time = time.time()
    decrypted_text = ak.khan_decrypt(ciphertext, public_key, (superposition_sequence_length, start_position), iv, salt, z_layers)
    decryption_time = time.time() - start_time

    # Display results
    print("\nEncryption and Decryption Results:")
    print("Original Plaintext:", plaintext)
    print("Decrypted Plaintext:", decrypted_text)
    print(f"Encryption Time: {encryption_time} seconds")
    print(f"Decryption Time: {decryption_time} seconds")
    print("Decryption Successful" if plaintext == decrypted_text else "Decryption Failed")

if __name__ == "__main__":
    main()
