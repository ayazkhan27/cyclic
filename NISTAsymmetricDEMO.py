import numpy as np
import importlib.util
import sys
from decimal import Decimal, getcontext
import random
from nistrng import pack_sequence, unpack_sequence, check_eligibility_all_battery, run_all_battery, SP800_22R1A_BATTERY
import string

# Import the asymmetricdemo module
module_name = "asymmetricdemo"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/asymmetricdemo.py"  # Update this path to the location of asymmetricdemo.py
spec = importlib.util.spec_from_file_location(module_name, file_path)
ad = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ad
spec.loader.exec_module(ad)

# Helper functions
def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_cyclic_sequence(prime):
    getcontext().prec = prime + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    if len(decimal_expansion) < prime - 1:
        decimal_expansion += '0' * (prime - 1 - len(decimal_expansion))
    return decimal_expansion[:prime - 1]

def save_ciphertext_to_file(ciphertext, filename="ciphertext.bin"):
    # Convert ciphertext to bytes if it's not already
    if isinstance(ciphertext, str):
        ciphertext = bytes(ciphertext, 'utf-8')
    elif isinstance(ciphertext, list):
        ciphertext = bytes([abs(b) % 256 for b in ciphertext])
    
    # Save ciphertext to file
    with open(filename, 'wb') as f:
        f.write(ciphertext)
    print(f"Ciphertext saved to {filename}")

def run_nist_tests(ciphertext):
    # Convert ciphertext to a binary sequence
    binary_sequence = ''.join(format(byte, '08b') for byte in ciphertext)

    # Convert the binary sequence to numpy array of bits
    sequence = np.array([int(bit) for bit in binary_sequence], dtype=int)
    binary_sequence_packed = pack_sequence(sequence)

    # Print sequence details
    print("Binary sequence packed for NIST tests:")
    print(binary_sequence_packed)
    print("Original sequence taken back by unpacking:")
    print(unpack_sequence(binary_sequence_packed))

    # Check the eligibility of the test and generate an eligible battery from the default NIST SP800-22r1a battery
    eligible_battery = check_eligibility_all_battery(binary_sequence_packed, SP800_22R1A_BATTERY)
    print("Eligible tests from NIST SP800-22r1a:")
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

# Example use
cyclic_prime = 1051  # You can choose any full reptend prime
cyclic_sequence = generate_cyclic_sequence(cyclic_prime)

# Generate plaintexts
plaintexts = [generate_plaintext(128) for _ in range(10)]

# Encrypt plaintexts using asymmetricdemo.py
ciphertexts = []
for pt in plaintexts:
    # Generate keys for each encryption (or generate once and reuse)
    public_key, private_key = ad.generate_keypair(cyclic_prime, cyclic_sequence)
    # Encrypt the plaintext
    encrypted_msg, temp_start, superposition_points = ad.encrypt(pt, public_key)
    # Collect ciphertext
    ciphertexts.append((encrypted_msg, public_key, private_key, temp_start, superposition_points))

# Convert ciphertext to bytes for NIST tests
def convert_to_bytes(ciphertext):
    if isinstance(ciphertext, list):
        # Since movements can be negative, take absolute value and modulo 256
        return bytes([abs(b) % 256 for b in ciphertext])
    return bytes(ciphertext)

# Select a ciphertext and convert it to bytes
encrypted_msg, public_key, private_key, temp_start, superposition_points = ciphertexts[0]
ciphertext_bytes = convert_to_bytes(encrypted_msg)

# Run NIST tests on the ciphertext
run_nist_tests(ciphertext_bytes)
