import numpy as np
import matplotlib.pyplot as plt
import math
import time
from scipy.fft import fft
from scipy.stats import entropy

#####################################################
# PART 1: FRP-BASED PSEUDO-RANDOM NUMBER GENERATOR (PRNG)
#####################################################

def get_cyclic_sequence(p):
    """
    Compute the repeating decimal (cyclic sequence) of 1/p for a full reptend prime.
    This sequence (of length p-1) is the unique "signature" or "fingerprint" of p.
    For example, for p = 7, returns "142857".
    """
    remainder = 1
    seen = {}
    sequence = ""
    while remainder and remainder not in seen:
        seen[remainder] = len(sequence)
        remainder *= 10
        sequence += str(remainder // p)
        remainder %= p
    if remainder:
        start = seen[remainder]
        sequence = sequence[start:]
    return sequence.zfill(p - 1)

def generate_rotations(cyclic_seq):
    """
    Generate all cyclic rotations of the given cyclic sequence.
    These rotations correspond to the repeating decimals for n/p.
    """
    n = len(cyclic_seq)
    rotations = []
    for i in range(n):
        rotations.append(cyclic_seq[i:] + cyclic_seq[:i])
    return rotations

def frp_prng_generator(p):
    """
    Given a full reptend prime p, generate pseudo-random numbers from its cyclic sequence.
    The cyclic sequence of 1/p is used as the base pattern.
    Each call to the generator returns a number derived from a cyclic rotation.
    
    Here, we simply interpret the cyclic rotation as an integer and then scale it to [0,1).
    """
    cyclic_seq = get_cyclic_sequence(p)
    rotations = generate_rotations(cyclic_seq)
    period = len(rotations)
    i = 0
    while True:
        # Get the i-th rotation (cyclically)
        rot = rotations[i % period]
        # Convert the rotation to an integer, then to a float in [0, 1)
        num = int(rot) / (10**len(rot))
        yield num
        i += 1

def benchmark_prng(p, num_samples=10000):
    """
    Benchmark the FRP-based PRNG:
      - Measure time to generate num_samples pseudo-random numbers.
      - Compute a simple entropy measure of the distribution.
    """
    prng = frp_prng_generator(p)
    samples = []
    start_time = time.time()
    for _ in range(num_samples):
        samples.append(next(prng))
    elapsed = time.time() - start_time

    samples = np.array(samples)
    # Compute a histogram and then the Shannon entropy of the distribution.
    hist, _ = np.histogram(samples, bins=50, density=True)
    sample_entropy = entropy(hist + 1e-12)  # avoid log(0)

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

def simulate_data_file(p, num_blocks=1000):
    """
    Simulate a data file that consists of num_blocks, each of which is a cyclic rotation
    of the cyclic sequence of 1/p. For instance, if p=7 and the cyclic sequence is "142857",
    then each block is one of the rotations (like "142857", "285714", etc.), chosen in order.
    """
    cyclic_seq = get_cyclic_sequence(p)
    rotations = generate_rotations(cyclic_seq)
    period = len(rotations)
    
    # For simplicity, let’s cycle through the rotations in order.
    data_file = []
    for i in range(num_blocks):
        # Each block is a string of digits
        block = rotations[i % period]
        data_file.append(block)
    return data_file

def compress_data_file(data_file, base_pattern):
    """
    "Compress" the data file by storing:
      - The base pattern (the cyclic sequence of 1/p).
      - The rotation indices that indicate which cyclic rotation each block is.
    In this ideal scenario, the original file can be reconstructed from these two pieces of information.
    """
    # For each block, determine its rotation index relative to the base pattern.
    rotations = generate_rotations(base_pattern)
    rotation_to_index = {rot: idx for idx, rot in enumerate(rotations)}
    indices = []
    for block in data_file:
        # We assume each block is exactly one of the rotations.
        indices.append(rotation_to_index[block])
    return base_pattern, indices

def decompress_data_file(compressed_data):
    """
    Reconstruct the original data file from the base pattern and the rotation indices.
    """
    base_pattern, indices = compressed_data
    rotations = generate_rotations(base_pattern)
    data_file = [rotations[i] for i in indices]
    return data_file

def benchmark_data_structure(p, num_blocks=10000):
    """
    Benchmark the cyclic data structure approach:
      - Generate a synthetic data file of num_blocks.
      - "Compress" the file by storing the base pattern and rotation indices.
      - Decompress the file and verify correctness.
      - Calculate the compression ratio (assuming each block is stored as a string vs. storing a small index).
    """
    # Generate the data file.
    data_file = simulate_data_file(p, num_blocks)
    base_pattern = get_cyclic_sequence(p)
    original_size = sum(len(block) for block in data_file)  # total number of digits
    
    # Compress the data file.
    start_time = time.time()
    compressed_data = compress_data_file(data_file, base_pattern)
    compress_time = time.time() - start_time
    
    # Decompress the data file.
    start_time = time.time()
    reconstructed = decompress_data_file(compressed_data)
    decompress_time = time.time() - start_time
    
    # Verify that the reconstruction is identical.
    correct = (data_file == reconstructed)
    
    # Estimate compression ratio:
    # Suppose each digit is stored as one character (1 byte) and each index is stored as an integer (say 4 bytes).
    # Original: num_blocks * block_length bytes.
    # Compressed: base pattern length + num_blocks * 4 bytes.
    block_length = len(base_pattern)
    original_bytes = num_blocks * block_length
    compressed_bytes = block_length + num_blocks * 4
    compression_ratio = compressed_bytes / original_bytes

    print(f"FRP-inspired Data Structure Benchmark for p={p}:")
    print(f"  Number of Blocks: {num_blocks}")
    print(f"  Block Length (digits): {block_length}")
    print(f"  Original Size: {original_bytes} bytes")
    print(f"  Compressed Size: {compressed_bytes} bytes")
    print(f"  Compression Ratio: {compression_ratio:.4f} (lower is better)")
    print(f"  Compression Time: {compress_time:.6f} seconds")
    print(f"  Decompression Time: {decompress_time:.6f} seconds")
    print(f"  Reconstruction Correct: {correct}")
    print("-" * 60)
    return compression_ratio

#####################################################
# MAIN FUNCTION: Run Benchmarks for Both Approaches
#####################################################
def main():
    # Choose a full reptend prime for testing; you can iterate over several if desired.
    # For demonstration, we'll test for p=7, p=17, and p=19.
    test_primes = [4099]
    
    print("=== FRP-Based Pseudo-Random Number Generator Benchmark ===")
    for p in test_primes:
        benchmark_prng(p, num_samples=10000)
    
    print("\n=== FRP-Inspired Cyclic Data Structure (Compression) Benchmark ===")
    # We'll test with a moderately large number of blocks.
    for p in test_primes:
        benchmark_data_structure(p, num_blocks=10000)

if __name__ == "__main__":
    main()
