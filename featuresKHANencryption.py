import time
import random
import string
import math
import numpy as np
from sympy import isprime
import khan_encryption as ke
import DEMOFileMasterpiece as dfm

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def measure_khan_encryption(plaintext, start_position, superposition_sequence_length, cyclic_prime, cyclic_sequence):
    max_attempts = 5  # Maximum number of attempts before giving up

    for _ in range(max_attempts):
        try:
            start_time = time.time()
            ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
                plaintext, cyclic_prime, cyclic_sequence, start_position)
            encryption_time = time.time() - start_time

            start_time = time.time()
            decrypted_text = ke.khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)
            decryption_time = time.time() - start_time

            return encryption_time, decryption_time, ciphertext, decrypted_text == plaintext
        except ValueError:
            # If a ValueError occurs, generate new random parameters and try again
            start_position = random.randint(1, cyclic_prime - 1)
            superposition_sequence_length = random.randint(2, cyclic_prime - 1)
            if superposition_sequence_length % 2 != 0:
                superposition_sequence_length += 1

    # If all attempts fail, return None values
    return None, None, None, False

def estimate_security_bits(cyclic_prime):
    return math.log2(cyclic_prime)

def analyze_avalanche_effect(plaintext, cyclic_prime, cyclic_sequence, start_position):
    try:
        original_ciphertext, *_ = ke.khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, start_position)
        
        different_bits = 0
        total_bits = 0
        
        for i in range(len(plaintext)):
            modified_plaintext = plaintext[:i] + chr((ord(plaintext[i]) + 1) % 256) + plaintext[i+1:]
            modified_ciphertext, *_ = ke.khan_encrypt(modified_plaintext, cyclic_prime, cyclic_sequence, start_position)
            
            for j in range(min(len(original_ciphertext), len(modified_ciphertext))):
                xor_result = original_ciphertext[j] ^ modified_ciphertext[j]
                different_bits += bin(xor_result).count('1')
                total_bits += xor_result.bit_length()
        
        return different_bits / total_bits if total_bits > 0 else 0
    except ValueError:
        return None

def test_khan_properties(num_tests=100, plaintext_lengths=[64, 128, 256, 512, 1024]):
    cyclic_prime = 1051  # You can adjust this value
    cyclic_sequence = dfm.generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)
    
    print(f"KHAN Encryption Properties (Cyclic Prime: {cyclic_prime})")
    print(f"Estimated Security Bits: {estimate_security_bits(cyclic_prime):.2f}")
    
    for length in plaintext_lengths:
        print(f"\nTesting with plaintext length: {length}")
        
        enc_times = []
        dec_times = []
        avalanche_effects = []
        successful_tests = 0
        failed_tests = 0
        
        for _ in range(num_tests):
            plaintext = generate_random_string(length)
            start_position = random.randint(1, cyclic_prime - 1)
            superposition_sequence_length = random.randint(2, cyclic_prime - 1)
            if superposition_sequence_length % 2 != 0:
                superposition_sequence_length += 1
            
            enc_time, dec_time, _, decryption_successful = measure_khan_encryption(
                plaintext, start_position, superposition_sequence_length, cyclic_prime, cyclic_sequence)
            
            if enc_time is not None and dec_time is not None:
                enc_times.append(enc_time)
                dec_times.append(dec_time)
                successful_tests += 1
                if decryption_successful:
                    avalanche_effect = analyze_avalanche_effect(plaintext, cyclic_prime, cyclic_sequence, start_position)
                    if avalanche_effect is not None:
                        avalanche_effects.append(avalanche_effect)
            else:
                failed_tests += 1
        
        print(f"Successful tests: {successful_tests}/{num_tests}")
        print(f"Failed tests: {failed_tests}/{num_tests}")
        
        if successful_tests > 0:
            print(f"Average Encryption Time: {np.mean(enc_times):.6f} seconds")
            print(f"Average Decryption Time: {np.mean(dec_times):.6f} seconds")
        
        if avalanche_effects:
            print(f"Average Avalanche Effect: {np.mean(avalanche_effects):.4f}")

if __name__ == "__main__":
    test_khan_properties()