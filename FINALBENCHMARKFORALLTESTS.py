#!/usr/bin/env python3
"""
ROBUST BENCHMARK TESTING FOR FRP-BASED PRNG AND CYCLIC DATA COMPRESSION

This script demonstrates two approaches inspired by the unique cyclic properties of
full reptend primes (FRPs):

1. FRP-Based Pseudo-Random Number Generator (PRNG):
   - Uses the repeating decimal of 1/p (for a full reptend prime p) as a "signature".
   - Cyclic rotations of that signature yield the repeating decimals for n/p.
   - A generator cycles through these rotations, converts them to numbers in [0,1), 
     and benchmarks the speed and entropy of the generated random stream.

2. Synthetic Periodic Data Compression:
   - Generates synthetic periodic (cyclic) data using a sine wave that mimics natural cycles.
   - Each cycle is generated as a rotation (shift) of a base cycle with a small random phase shift.
   - The data is "compressed" by storing the base cycle and, for each cycle, the rotation index.
   - The script benchmarks the compression ratio and the speed of compression/decompression.

Both sections are fully self-contained and include detailed comments explaining each step.
"""

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
    
    For a full reptend prime, the period is p-1 digits. However, for large primes (e.g. 64-bit),
    p-1 may be enormous. max_digits limits the number of digits computed for testing.
    
    Parameters:
      p         : Full reptend prime.
      max_digits: (Optional) Maximum number of digits to compute.
      
    Returns:
      A string representing the repeating decimal of 1/p.
    """
    remainder = 1
    seen = {}
    sequence = ""
    while remainder and remainder not in seen and (max_digits is None or len(sequence) < max_digits):
        seen[remainder] = len(sequence)
        remainder *= 10
        sequence += str(remainder // p)
        remainder %= p
    if remainder and max_digits is None:
        start = seen[remainder]
        sequence = sequence[start:]
    if max_digits is not None:
        sequence = sequence[:max_digits]
        sequence = sequence.zfill(max_digits)
    else:
        sequence = sequence.zfill(p - 1)
    return sequence

def generate_rotations(cyclic_seq):
    """
    Generate all cyclic rotations (i.e. all cyclic permutations) of the base cyclic sequence.
    Each rotation corresponds to a repeating decimal for some fraction n/p.
    
    Parameters:
      cyclic_seq : The base cyclic sequence (string).
      
    Returns:
      A list of cyclic rotations (strings).
    """
    n = len(cyclic_seq)
    rotations = []
    for i in range(n):
        rotations.append(cyclic_seq[i:] + cyclic_seq[:i])
    return rotations

def frp_prng_generator(p, max_digits=None):
    """
    FRP-based PRNG generator.
    
    Uses the cyclic sequence of 1/p as a base pattern and cycles through its rotations.
    Each rotation is converted to an integer and normalized to yield a number in [0,1).
    
    Parameters:
      p         : Full reptend prime.
      max_digits: (Optional) Limit on digits for the cyclic sequence.
      
    Yields:
      A pseudo-random float in [0, 1).
    """
    cyclic_seq = get_cyclic_sequence(p, max_digits)
    rotations = generate_rotations(cyclic_seq)
    period = len(rotations)
    i = 0
    while True:
        # Cycle through rotations in order.
        rot = rotations[i % period]
        # Convert the string to an integer and scale to [0,1)
        num = int(rot) / (10**len(rot))
        yield num
        i += 1

def benchmark_prng(p, num_samples=10000, max_digits=None):
    """
    Benchmark the FRP-based PRNG by generating a stream of random numbers.
    
    Measures:
      - Total time to generate num_samples numbers.
      - Average time per sample.
      - Empirical entropy of the generated numbers (using a 50-bin histogram).
    
    Parameters:
      p         : Full reptend prime.
      num_samples: Number of random samples to generate.
      max_digits: (Optional) Maximum number of digits to use for the cyclic sequence.
      
    Returns:
      The generated samples as a NumPy array.
    """
    prng = frp_prng_generator(p, max_digits)
    samples = []
    start_time = time.time()
    for _ in range(num_samples):
        samples.append(next(prng))
    elapsed = time.time() - start_time
    samples = np.array(samples)
    hist, _ = np.histogram(samples, bins=50, density=True)
    sample_entropy = entropy(hist + 1e-12)  # Avoid log(0)
    
    print(f"FRP-based PRNG Benchmark for p={p}:")
    print(f"  Samples generated: {num_samples}")
    print(f"  Total time taken: {elapsed:.6f} seconds")
    print(f"  Average time per sample: {elapsed/num_samples:.8f} seconds")
    print(f"  Empirical entropy (50-bin histogram): {sample_entropy:.4f}")
    print("  Sample output (first 10 numbers):", samples[:10])
    print("-" * 60)
    return samples

#####################################################
# PART 2: SYNTHETIC PERIODIC DATA COMPRESSION
#####################################################

def simulate_sine_wave(period=2*math.pi, num_points=100, num_cycles=1000, noise_level=0.01):
    """
    Generate synthetic periodic (cyclic) data using a sine wave.
    
    Parameters:
      period     : The period of the sine wave.
      num_points : Number of data points per cycle.
      num_cycles : Total number of cycles to generate.
      noise_level: Standard deviation of Gaussian noise added to each cycle.
      
    Returns:
      A 1D NumPy array representing the concatenated time series.
      Also returns the base cycle (first period) as a reference.
    """
    x = np.linspace(0, period, num_points, endpoint=False)
    base_cycle = np.sin(x)
    # Create cycles by rotating the base cycle with a random integer shift (simulate phase variation)
    cycles = []
    for i in range(num_cycles):
        # Choose a random shift in [0, num_points)
        shift = np.random.randint(0, num_points)
        cycle = np.roll(base_cycle, shift)
        # Optionally add a small amount of noise
        cycle += np.random.normal(0, noise_level, size=num_points)
        cycles.append(cycle)
    data = np.concatenate(cycles)
    return data, base_cycle

def compress_sine_wave(data, base_cycle):
    """
    Compress synthetic periodic data by representing it as repeated cycles.
    
    For ideal periodic data, the base cycle is stored once,
    and for each cycle, the phase shift (an integer index) is stored.
    
    Parameters:
      data       : The synthetic time series data.
      base_cycle : The base cycle (1 period) of the sine wave.
      
    Returns:
      A tuple (base_cycle, shift_indices) that represents the compressed data.
    """
    num_points = len(base_cycle)
    # Calculate how many full cycles are in the data.
    num_cycles = len(data) // num_points
    shift_indices = []
    for i in range(num_cycles):
        cycle = data[i*num_points:(i+1)*num_points]
        # Compare the cycle with every possible rotation of the base_cycle.
        rotations = [np.roll(base_cycle, shift) for shift in range(num_points)]
        # Use Euclidean distance to find the best matching rotation.
        distances = [np.linalg.norm(cycle - rot) for rot in rotations]
        best_shift = np.argmin(distances)
        shift_indices.append(best_shift)
    return base_cycle, shift_indices

def decompress_sine_wave(compressed_data, num_cycles):
    """
    Reconstruct the synthetic time series data from the compressed representation.
    
    Parameters:
      compressed_data: A tuple (base_cycle, shift_indices)
      num_cycles     : Number of cycles to reconstruct.
      
    Returns:
      A 1D NumPy array representing the reconstructed time series.
    """
    base_cycle, shift_indices = compressed_data
    num_points = len(base_cycle)
    cycles = []
    for shift in shift_indices:
        cycles.append(np.roll(base_cycle, shift))
    data_reconstructed = np.concatenate(cycles)
    return data_reconstructed

def benchmark_sine_compression(num_cycles=10000, num_points=100, noise_level=0.01):
    """
    Benchmark the FRP-inspired cyclic data structure approach on synthetic periodic data.
    
    Generates a synthetic sine wave (with added noise) that mimics real-world periodic data,
    then "compresses" it by storing the base cycle and the rotation (phase shift) indices,
    and finally measures the compression ratio and timing.
    
    Returns:
      The compression ratio.
    """
    data, base_cycle = simulate_sine_wave(period=2*math.pi, num_points=num_points,
                                          num_cycles=num_cycles, noise_level=noise_level)
    original_size = data.size  # assuming each sample is one unit (or byte)
    
    start_time = time.time()
    compressed_data = compress_sine_wave(data, base_cycle)
    compress_time = time.time() - start_time
    
    start_time = time.time()
    reconstructed = decompress_sine_wave(compressed_data, num_cycles)
    decompress_time = time.time() - start_time
    
    # Check reconstruction error
    reconstruction_error = np.linalg.norm(data - reconstructed)
    
    # Assume:
    # - The base cycle is stored as num_points floats (each 8 bytes, say).
    # - Each shift index is stored as an integer (4 bytes).
    compressed_size = num_points*8 + num_cycles * 4
    compression_ratio = compressed_size / (original_size * 8)  # original stored as 8-byte floats

    print(f"FRP-Inspired Synthetic Sine Wave Compression Benchmark:")
    print(f"  Number of Cycles: {num_cycles}")
    print(f"  Points per Cycle: {num_points}")
    print(f"  Original Size: {original_size*8} bytes (assuming 8 bytes per float)")
    print(f"  Compressed Size: {compressed_size} bytes")
    print(f"  Compression Ratio: {compression_ratio:.4f} (lower is better)")
    print(f"  Compression Time: {compress_time:.6f} seconds")
    print(f"  Decompression Time: {decompress_time:.6f} seconds")
    print(f"  Reconstruction Error (L2 norm): {reconstruction_error:.6f}")
    print("-" * 60)
    return compression_ratio

#####################################################
# MAIN FUNCTION: Run Benchmarks for Both Approaches
#####################################################
def main():
    # For demonstration, we can test with a 64-bit full reptend prime.
    # Here we use a placeholder prime. Replace with a verified full reptend prime as needed.
    large_frp = 4099  # example candidate (must be verified as full reptend)
    max_digits = 4098  # Limit for demonstration purposes (in practice, p-1 digits can be huge)
    
    print("=== FRP-Based Pseudo-Random Number Generator Benchmark ===")
    benchmark_prng(large_frp, num_samples=10000, max_digits=max_digits)
    
    print("\n=== Synthetic Periodic Data Compression Benchmark ===")
    benchmark_sine_compression(num_cycles=10000, num_points=100, noise_level=0.01)

if __name__ == "__main__":
    main()
