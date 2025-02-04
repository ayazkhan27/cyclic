import numpy as np
import importlib.util
import sys
import random
import string
from nistrng import (
    pack_sequence,
    unpack_sequence,
    check_eligibility_all_battery,
    run_all_battery,
    SP800_22R1A_BATTERY,
)
import time

# Import the GPTOriginalAlgo module (assumed to be in the same directory)
module_name = "GPTOriginalAlgo"
file_path = "./GPTOriginalAlgo.py"  # Adjust the path if necessary
spec = importlib.util.spec_from_file_location(module_name, file_path)
gpt_algo = importlib.util.module_from_spec(spec)
sys.modules[module_name] = gpt_algo
spec.loader.exec_module(gpt_algo)

# Helper functions
def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def save_ciphertext_to_file(ciphertext, filename="ciphertext.bin"):
    # Convert ciphertext to bytes
    ciphertext_bytes = convert_ciphertext_to_bytes(ciphertext)
    
    # Save ciphertext to file
    with open(filename, 'wb') as f:
        f.write(ciphertext_bytes)
    print(f"Ciphertext saved to {filename}")

def run_nist_tests(ciphertext_bytes):
    # Convert ciphertext bytes to a binary sequence
    binary_sequence = ''.join(format(byte, '08b') for byte in ciphertext_bytes)

    # Convert the binary sequence to numpy array of 0s and 1s
    sequence = np.array([int(bit) for bit in binary_sequence], dtype=int)
    binary_sequence_packed = pack_sequence(sequence)

    # Print sequence details
    print("Binary sequence packed for NIST tests.")
    print("Original sequence length:", len(sequence))

    # Check the eligibility of the test and generate an eligible battery from the default NIST-SP800-22R1A battery
    eligible_battery = check_eligibility_all_battery(binary_sequence_packed, SP800_22R1A_BATTERY)
    print("Eligible tests from NIST-SP800-22R1A:")
    for name in eligible_battery.keys():
        print("- " + name)

    # Test the sequence on the eligible tests
    results = run_all_battery(binary_sequence_packed, eligible_battery, False)
    # Print results one by one
    print("Test results:")
    for result, elapsed_time in results:
        if result.passed:
            print(f"- PASSED - score: {np.round(result.score, 3)} - {result.name} - elapsed time: {elapsed_time:.2f} ms")
        else:
            print(f"- FAILED - score: {np.round(result.score, 3)} - {result.name} - elapsed time: {elapsed_time:.2f} ms")

def convert_ciphertext_to_bytes(ciphertext):
    ciphertext_bytes = b''
    for c1, c2 in ciphertext:
        # Determine the number of bytes needed for c1 and c2
        c1_bytes_length = (c1.bit_length() + 7) // 8
        c2_bytes_length = (c2.bit_length() + 7) // 8
        # Convert c1 and c2 to bytes
        c1_bytes = c1.to_bytes(c1_bytes_length, byteorder='big')
        c2_bytes = c2.to_bytes(c2_bytes_length, byteorder='big')
        # For consistent length, you might pad the bytes to a fixed length
        ciphertext_bytes += c1_bytes + c2_bytes
    return ciphertext_bytes

# Example use
cyclic_prime = 1051  # Full reptend prime
start_position = 751  # Not used in this algorithm
superposition_sequence_length = 9866  # Not used in this algorithm

# Create an instance of the encryption class
cipher = gpt_algo.FullReptendElGamal()

# Modify the generate_keys method to accept a specified prime
def generate_keys_with_prime(self, p, g):
    """Generate public and private keys with specified p and g."""
    x = random.randint(2, p - 2)
    h = pow(g, x, p)
    self.public_key = (p, g, h)
    self.private_key = x

# Replace the generate_keys method with the modified one
import types
cipher.generate_keys = types.MethodType(generate_keys_with_prime, cipher)

# Ensure g is a primitive root modulo p
from sympy.ntheory import is_primitive_root

# Find a primitive root modulo cyclic_prime
for candidate_g in range(2, cyclic_prime):
    if is_primitive_root(candidate_g, cyclic_prime):
        g = candidate_g
        break

# Generate keys with the specified prime and primitive root
cipher.generate_keys(cyclic_prime, g)

print("Public Key:", cipher.public_key)
print("Private Key:", cipher.private_key)

# Generate plaintexts
plaintexts = [generate_plaintext(128) for _ in range(10)]

# Encrypt plaintexts
ciphertexts = []
encryption_times = []
for plaintext in plaintexts:
    start_time = time.time()
    ciphertext = cipher.encrypt(plaintext)
    encryption_time = time.time() - start_time
    encryption_times.append(encryption_time)
    ciphertexts.append(ciphertext)

print("\nAverage Encryption Time: {:.6f} seconds".format(sum(encryption_times) / len(encryption_times)))

# Select a ciphertext and convert it to bytes
ciphertext_bytes = convert_ciphertext_to_bytes(ciphertexts[0])

# Run NIST tests on the ciphertext
run_nist_tests(ciphertext_bytes)
