import numpy as np
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from nistrng import pack_sequence, unpack_sequence, check_eligibility_all_battery, run_all_battery, SP800_22R1A_BATTERY

# Generate RSA key pair
key = RSA.generate(2048)
public_key = key.publickey()
cipher_rsa = PKCS1_OAEP.new(public_key)

# Helper function to generate random plaintext
def generate_plaintext(length):
    return get_random_bytes(length)

# Encrypt the plaintext using RSA
plaintext = generate_plaintext(128)  # 128 bytes of random data
ciphertext = cipher_rsa.encrypt(plaintext)

# Function to convert ciphertext to a format suitable for NIST tests
def convert_to_bytes(ciphertext):
    return bytes(ciphertext)

# Run NIST tests on the ciphertext
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

# Convert the RSA ciphertext to bytes for NIST tests
ciphertext_bytes = convert_to_bytes(ciphertext)

# Run NIST tests on the ciphertext
run_nist_tests(ciphertext_bytes)
