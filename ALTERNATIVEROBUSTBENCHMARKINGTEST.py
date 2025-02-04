import numpy as np
import matplotlib.pyplot as plt
import math
import time
from scipy.fft import fft
from scipy.stats import entropy

#####################################################
# PART 1: FRP-BASED PSEUDO-RANDOM NUMBER GENERATOR (PRNG)
#####################################################

def get_cyclic_sequence(p, max_digits=None):
    """
    Compute the repeating decimal (cyclic sequence) of 1/p for a full reptend prime.
    For a full reptend prime, the repeating sequence has length p-1.
    However, for very large primes (e.g. 64-bit primes), p-1 digits can be enormous.
    Therefore, if max_digits is provided, only compute the first max_digits digits.
    
    Parameters:
      p         : full reptend prime (e.g., 7, 17, or a 64-bit prime)
      max_digits: (optional) maximum number of digits to compute
     
    Returns:
      A string representing the repeating decimal for 1/p (padded to length p-1 or max_digits).
    """
    remainder = 1
    seen = {}
    sequence = ""
    # Standard long-division algorithm until a remainder repeats.
    while remainder and remainder not in seen and (max_digits is None or len(sequence) < max_digits):
        seen[remainder] = len(sequence)
        remainder *= 10
        sequence += str(remainder // p)
        remainder %= p
    # If a cycle is detected, we take the cycle portion.
    if remainder and max_digits is None:
        start = seen[remainder]
        sequence = sequence[start:]
    # If max_digits is provided, truncate (or pad) to that length.
    if max_digits is not None:
        sequence = sequence[:max_digits]
        sequence = sequence.zfill(max_digits)
    else:
        sequence = sequence.zfill(p - 1)
    return sequence

def generate_rotations(cyclic_seq):
    """
    Generate all cyclic rotations (permutations) of the given cyclic sequence.
    Each rotation corresponds to the repeating decimal for some fraction n/p.
    
    For example, for "142857", returns:
      ["142857", "428571", "285714", "857142", "571428", "714285"]
    """
    n = len(cyclic_seq)
    rotations = []
    for i in range(n):
        rotations.append(cyclic_seq[i:] + cyclic_seq[:i])
    return rotations

def frp_prng_generator(p, max_digits=None):
    """
    Given a full reptend prime p, generate pseudo-random numbers using its cyclic sequence.
    The cyclic sequence (of 1/p) is used as the base pattern.
    
    The function generates all cyclic rotations (each corresponding to n/p) and
    then cycles through them, converting each rotation to an integer and scaling it to [0,1).
    
    Parameters:
      p         : full reptend prime
      max_digits: limit on the number of digits to use for the cyclic sequence (useful for large p)
    """
    cyclic_seq = get_cyclic_sequence(p, max_digits)
    rotations = generate_rotations(cyclic_seq)
    period = len(rotations)
    i = 0
    while True:
        rot = rotations[i % period]
        # Interpret the rotation as an integer, then scale to [0, 1)
        num = int(rot) / (10**len(rot))
        yield num
        i += 1

def benchmark_prng(p, num_samples=10000, max_digits=None):
    """
    Benchmark the FRP-based PRNG.
    
    Measures the time to generate num_samples pseudo-random numbers and computes
    a simple Shannon entropy estimate on a 50-bin histogram of the output distribution.
    """
    prng = frp_prng_generator(p, max_digits)
    samples = []
    start_time = time.time()
    for _ in range(num_samples):
        samples.append(next(prng))
    elapsed = time.time() - start_time
    samples = np.array(samples)
    hist, _ = np.histogram(samples, bins=50, density=True)
    sample_entropy = entropy(hist + 1e-12)  # small offset to avoid log(0)
    
    print(f"FRP-based PRNG Benchmark for p={p}:")
    print(f"  Samples generated: {num_samples}")
    print(f"  Time taken: {elapsed:.6f} seconds")
    print(f"  Average time per sample: {elapsed/num_samples:.8f} seconds")
    print(f"  Empirical entropy (50-bin histogram): {sample_entropy:.4f}")
    print("  Sample output (first 10 numbers):", samples[:10])
    print("-" * 60)
    return samples

#####################################################
# PART 2: FRP-INSPIRED CYCLIC DATA STRUCTURE FOR PERIODIC DATA COMPRESSION
#####################################################

def simulate_data_file(p, num_blocks=1000, max_digits=None):
    """
    Simulate a data file that consists of num_blocks, where each block is a cyclic rotation
    of the cyclic sequence of 1/p. In our idealized model, the entire file is just multiple
    rotations of the base pattern.
    
    Parameters:
      p         : full reptend prime
      num_blocks: total number of blocks to generate
      max_digits: limit on the number of digits of the cyclic sequence (for large p)
    """
    cyclic_seq = get_cyclic_sequence(p, max_digits)
    rotations = generate_rotations(cyclic_seq)
    period = len(rotations)
    data_file = []
    for i in range(num_blocks):
        block = rotations[i % period]
        data_file.append(block)
    return data_file

def compress_data_file(data_file, base_pattern):
    """
    "Compress" the data file by storing:
      - The base pattern (the cyclic sequence for 1/p).
      - The rotation indices for each block, indicating which cyclic permutation it is.
      
    This is lossless since the original file can be reconstructed exactly from the base pattern and indices.
    """
    rotations = generate_rotations(base_pattern)
    rotation_to_index = {rot: idx for idx, rot in enumerate(rotations)}
    indices = []
    for block in data_file:
        indices.append(rotation_to_index[block])
    return base_pattern, indices

def decompress_data_file(compressed_data):
    """
    Reconstruct the original data file from the base pattern and rotation indices.
    """
    base_pattern, indices = compressed_data
    rotations = generate_rotations(base_pattern)
    data_file = [rotations[i] for i in indices]
    return data_file

def benchmark_data_structure(p, num_blocks=10000, max_digits=None):
    """
    Benchmark the cyclic data structure approach for compression.
    
    Generates a synthetic data file, compresses it (by storing the base pattern and rotation indices),
    decompresses it, verifies correctness, and computes a compression ratio.
    
    Assumes each digit is stored as 1 byte and each index as 4 bytes.
    """
    data_file = simulate_data_file(p, num_blocks, max_digits)
    base_pattern = get_cyclic_sequence(p, max_digits)
    block_length = len(base_pattern)
    original_size = num_blocks * block_length  # total bytes if each digit is 1 byte
    start_time = time.time()
    compressed_data = compress_data_file(data_file, base_pattern)
    compress_time = time.time() - start_time
    start_time = time.time()
    reconstructed = decompress_data_file(compressed_data)
    decompress_time = time.time() - start_time
    correct = (data_file == reconstructed)
    
    compressed_size = block_length + num_blocks * 4  # base pattern + indices
    compression_ratio = compressed_size / original_size

    print(f"FRP-inspired Data Structure Benchmark for p={p}:")
    print(f"  Number of Blocks: {num_blocks}")
    print(f"  Block Length (digits): {block_length}")
    print(f"  Original Size: {original_size} bytes")
    print(f"  Compressed Size: {compressed_size} bytes")
    print(f"  Compression Ratio: {compression_ratio:.4f} (lower is better)")
    print(f"  Compression Time: {compress_time:.6f} seconds")
    print(f"  Decompression Time: {decompress_time:.6f} seconds")
    print(f"  Reconstruction Correct: {correct}")
    print("-" * 60)
    return compression_ratio

#####################################################
# MAIN FUNCTION: Run Benchmarks
#####################################################
def main():
    # For demonstration, we will use a 64-bit full reptend prime.
    # Note: In practice, a 64-bit prime p can have up to (p-1) digits in its repeating decimal.
    # To keep computation reasonable, we limit the number of digits computed with max_digits.
    # Here, max_digits=1000 is arbitrary; you can adjust based on your needs.
    
    # Example: choose a 64-bit prime (this is a 19-digit prime, which is in the 64-bit range).
    # (In a real scenario, you would verify that p is full reptend, i.e. ord_p(10)=p-1.)
    large_frp = 8388617  # Example candidate (you need to ensure it meets FRP criteria)
    max_digits = 1000  # Limit the cyclic sequence to 1000 digits for demonstration purposes

    print("=== FRP-Based Pseudo-Random Number Generator Benchmark ===")
    # Benchmark the PRNG for the 64-bit FRP.
    benchmark_prng(large_frp, num_samples=10000, max_digits=max_digits)
    
    print("\n=== FRP-Inspired Cyclic Data Structure (Compression) Benchmark ===")
    # Benchmark the cyclic data structure for compression.
    benchmark_data_structure(large_frp, num_blocks=10000, max_digits=max_digits)

if __name__ == "__main__":
    main()
