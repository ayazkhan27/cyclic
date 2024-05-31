import numpy as np
import importlib.util
import sys
from decimal import Decimal, getcontext
from collections import Counter
import random
import string


# Import the khan_encryption2 module
module_name = "khan_encryption2.0"
file_path = "C:/Users/admin/Documents/GitHub/cyclic/khan_encryption_2.py"
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

def differential_cryptanalysis(ciphertexts, plaintexts):
    differential_pairs = []
    for i in range(len(plaintexts) - 1):
        pt1 = plaintexts[i]
        pt2 = plaintexts[i + 1]
        diff_plaintext = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(pt1, pt2))
        
        ct1 = ciphertexts[i]
        ct2 = ciphertexts[i + 1]
        # Assuming ciphertexts are lists of integers (bytes)
        diff_ciphertext = bytes((a ^ b) % 256 for a, b in zip(ct1, ct2))
        
        differential_pairs.append((diff_plaintext, diff_ciphertext))
    return differential_pairs

def linear_cryptanalysis(plaintexts, ciphertexts):
    linear_approximations = []
    for pt, ct in zip(plaintexts, ciphertexts):
        approximation = [(ord(pt[i]) ^ ct[i]) for i in range(len(pt))]
        linear_approximations.append(approximation)
    # Identify zero-correlation properties
    zero_correlation_properties = [approx for approx in linear_approximations if sum(approx) == 0]
    return zero_correlation_properties

# Example use
cyclic_prime = 1051
start_position = 123
superposition_sequence_length = 232

# Generate cyclic sequence
cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

# Generate plaintexts
plaintexts = [generate_plaintext(128) for _ in range(10)]

# Encrypt plaintexts
ciphertexts = [ke.khan_encrypt(pt, cyclic_prime, cyclic_sequence, start_position, superposition_sequence_length)[0] for pt in plaintexts]

# Perform differential cryptanalysis
differential_pairs = differential_cryptanalysis(ciphertexts, plaintexts)
for pt_diff, ct_diff in differential_pairs:
    print(f"Plaintext Difference: {pt_diff}, Ciphertext Difference: {ct_diff}")

# Perform linear cryptanalysis
zero_corr_properties = linear_cryptanalysis(plaintexts, ciphertexts)
print(f"Zero-Correlation Properties: {zero_corr_properties}")
