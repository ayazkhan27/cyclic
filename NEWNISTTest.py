import numpy as np
import importlib.util
import sys
import random
import string
from decimal import Decimal, getcontext
from nistrng import pack_sequence, unpack_sequence, check_eligibility_all_battery, run_all_battery, SP800_22R1A_BATTERY

# =====================
# Import the GPTO1KHANDemo module
# =====================
module_name = "GPTO1KHANDemo"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/GPTO1KHANDemo.py"
spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

# =====================
# Helper Functions
# =====================

def generate_plaintext(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def convert_to_bytes(ciphertext):
    # Convert the ciphertext (list of ints) to bytes
    if isinstance(ciphertext, list):
        return bytes([b % 256 for b in ciphertext])
    elif isinstance(ciphertext, str):
        return ciphertext.encode('utf-8')
    return bytes(ciphertext)

def run_nist_tests(ciphertext_bytes):
    # Convert ciphertext bytes to a binary string
    binary_sequence = ''.join(format(byte, '08b') for byte in ciphertext_bytes)

    # Convert the binary sequence to an array of bytes
    sequence = np.array([int(binary_sequence[i:i+8], 2) 
                         for i in range(0, len(binary_sequence), 8)], dtype=int)

    # Pack sequence for NIST tests
    binary_sequence_packed = pack_sequence(sequence)

    print("Binary sequence packed for NIST tests.")
    # Check eligibility for NIST tests
    eligible_battery = check_eligibility_all_battery(binary_sequence_packed, SP800_22R1A_BATTERY)
    print("Eligible tests from NIST SP800-22r1a:")
    for name in eligible_battery.keys():
        print("- " + name)

    # Run all eligible tests
    results = run_all_battery(binary_sequence_packed, eligible_battery)
    print("Test results:")
    for result, elapsed_time in results:
        status = "PASSED" if result.passed else "FAILED"
        print(f"- {status} - score: {np.round(result.score, 3)} - {result.name} - elapsed time: {elapsed_time} ms")


# =====================
# Main Execution
# =====================

if __name__ == "__main__":
    # Choose a full reptend prime for demonstration
    # Make sure it's a full reptend prime. For example, 337 is known to be full reptend.
    prime = 1051
    if not ke.is_full_reptend_prime(prime):
        raise ValueError("Not a full reptend prime. Choose another prime.")

    # Get the cyclic sequence associated with the chosen prime
    cyclic_sequence = ke.get_cyclic_sequence_for_prime(prime)

    # Diffie-Hellman-like key setup to derive the start position
    (p, g, h), x = ke.dh_keygen(prime)
    y = random.randint(2, p-2)
    other_component = pow(g, y, p)
    K_enc = pow(h, y, p)
    K_dec = ke.dh_compute_shared_secret(p, g, h, x, other_component)
    assert K_enc == K_dec, "Key exchange failed!"

    # Derive start position from the shared secret
    start_position = ke.key_derivation(p, K_enc)

    # Generate a random salt
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

    # Generate multiple plaintexts to produce a large ciphertext sample
    # Increase the number and length of plaintexts to get more data for NIST tests
    plaintexts = [generate_plaintext(2048) for _ in range(5)]

    # Encrypt all plaintexts and collect their ciphertext
    # encrypt_message returns:
    # (ciphertext_ints, z_layers, z_value, superposition_sequence, char_to_movement, movement_to_char)
    combined_ciphertext = []
    for pt in plaintexts:
        ciphertext_ints, z_layers, z_value, superposition_sequence, c2m, m2c = ke.encrypt_message(pt, p, cyclic_sequence, start_position, salt)
        combined_ciphertext.extend(ciphertext_ints)

    # Convert combined ciphertext to bytes
    ciphertext_bytes = convert_to_bytes(combined_ciphertext)

    # Run NIST statistical tests on the combined ciphertext bytes
    run_nist_tests(ciphertext_bytes)
