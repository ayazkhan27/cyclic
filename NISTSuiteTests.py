import numpy as np
import importlib.util
import sys
from decimal import Decimal, getcontext
import random
from nistrng import pack_sequence, unpack_sequence, check_eligibility_all_battery, run_all_battery, SP800_22R1A_BATTERY
import string

# Import the khan_encryption2 module
module_name = "khan_encryption2.0"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption_2.py"
spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

# Helper functions
def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

def save_ciphertext_to_file(ciphertext, filename="ciphertext.bin"):
    # Convert ciphertext to bytes if it's not already
    if isinstance(ciphertext, str):
        ciphertext = bytes(ciphertext, 'utf-8')
    elif isinstance(ciphertext, list):
        ciphertext = bytes([b % 256 for b in ciphertext])
    
    # Save ciphertext to file
    with open(filename, 'wb') as f:
        f.write(ciphertext)
    print(f"Ciphertext saved to {filename}")

def run_nist_tests(ciphertext):
    # Convert ciphertext to a binary sequence
    binary_sequence = ''.join(format(byte, '08b') for byte in ciphertext)

    # Convert the binary sequence to numpy array of 8-bit signed integers
    sequence = np.array([int(binary_sequence[i:i+8], 2) for i in range(0, len(binary_sequence), 8)], dtype=int)
    binary_sequence_packed = pack_sequence(sequence)

    # Print sequence details
    print("Binary sequence packed for NIST tests:")
    print(binary_sequence_packed)
    print("Original sequence taken back by unpacking:")
    print(unpack_sequence(binary_sequence_packed))

    # Check the eligibility of the test and generate an eligible battery from the default NIST-sp800-22r1a battery
    eligible_battery = check_eligibility_all_battery(binary_sequence_packed, SP800_22R1A_BATTERY)
    print("Eligible test from NIST-SP800-22r1a:")
    for name in eligible_battery.keys():
        print("- " + name)

    # Test the sequence on the eligible tests
    results = run_all_battery(binary_sequence_packed, eligible_battery, False)
    # Print results one by one
    print("Test results:")
    for result, elapsed_time in results:
        if result.passed:
            print(f"- PASSED - score: {np.round(result.score, 3)} - {result.name} - elapsed time: {elapsed_time} ms")
        else:
            print(f"- FAILED - score: {np.round(result.score, 3)} - {result.name} - elapsed time: {elapsed_time} ms")

# Example use
cyclic_prime = 1051
start_position = 751
superposition_sequence_length = 78662

# Generate cyclic sequence
cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

# Generate plaintexts
plaintexts = [generate_plaintext(128) for _ in range(10)]

# Encrypt plaintexts
ciphertexts = [ke.khan_encrypt(pt, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)[0] for pt in plaintexts]

# Convert ciphertext to bytes for NIST tests
def convert_to_bytes(ciphertext):
    if isinstance(ciphertext, list):
        return bytes([b % 256 for b in ciphertext])
    return bytes(ciphertext)

# Select a ciphertext and convert it to bytes
ciphertext_bytes = convert_to_bytes(ciphertexts[0])

# Run NIST tests on the saved ciphertext
run_nist_tests(ciphertext_bytes)
