#!/usr/bin/env python3
"""
Optimized FRP-Based Circular Buffer Using Digit-Group Scheduling
"""

import numpy as np
import pandas as pd
import time
import kagglehub

#####################################################
# Part A: Optimized FRP Sequence & Schedule Functions
#####################################################

def get_prime_grouping(p):
    """Determine the digit grouping size (equal to number of digits in p)"""
    return len(str(p))

def get_cyclic_sequence(p, max_digits=None):
    """
    Compute the repeating decimal (cyclic sequence) of 1/p for a full reptend prime.
    Also returns the order of remainders for scheduling.
    
    Parameters:
      p         : Full reptend prime.
      max_digits: (Optional) Maximum number of digits to compute.
    
    Returns:
      sequence      : String representing the cyclic sequence.
      remainder_order: List of remainders encountered (used for scheduling).
    """
    remainder = 1
    seen = {}
    sequence = ""
    remainder_order = []
    while remainder and remainder not in seen and (max_digits is None or len(sequence) < max_digits):
        seen[remainder] = len(sequence)
        remainder_order.append(remainder)
        remainder *= 10
        sequence += str(remainder // p)
        remainder %= p
    if remainder and max_digits is None:  # Handle full reptend cycle
        start = seen[remainder]
        sequence = sequence[start:]
        remainder_order = remainder_order[start:]
    else:  # Truncate remainders if max_digits is set
        remainder_order = remainder_order[:max_digits]
    # Pad sequence if needed
    if max_digits is not None:
        sequence = sequence.ljust(max_digits, '0')[:max_digits]
    return sequence, remainder_order

def generate_cyclic_groups(sequence, group_size):
    """Generate all cyclic groups of size `group_size` from the sequence"""
    n = len(sequence)
    groups = []
    for i in range(n):
        if i + group_size <= n:
            groups.append(sequence[i:i+group_size])
        else:
            # Handle wrap-around groups
            wrap = sequence[i:] + sequence[:(i+group_size)%n]
            groups.append(wrap)
    return groups[:len(sequence)]  # Return exactly p-1 groups

def compute_shift_schedule(p, cyclic_sequence):
    """
    Compute optimized shift schedule using digit-group indexing
    Returns: (schedule_indices, buffer_size)
    """
    d = get_prime_grouping(p)
    groups = generate_cyclic_groups(cyclic_sequence, d)
    
    # Create group -> first occurrence index mapping
    group_map = {}
    for idx, group in enumerate(groups):
        if group not in group_map:
            group_map[group] = idx
    
    # Generate schedule based on fraction order
    schedule = []
    for n in range(1, p):
        # Calculate first group of n/p (equivalent to nth cyclic permutation)
        target_group = groups[(n * (p-1) // p) % (p-1)]  # Mathematical shortcut
        schedule.append(group_map[target_group])
    
    return np.array(schedule, dtype=int), len(groups)

#####################################################
# Part B: Enhanced Circular Buffer Implementation
#####################################################

class CyclicBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.write_count = 0  # Track total writes for analytics

    def write(self, data, index):
        """Write data to calculated index with automatic wrap-around"""
        idx = index % self.size
        self.buffer[idx] = data
        self.write_count += 1

    def get_utilization(self):
        """Calculate buffer slot utilization statistics"""
        used = sum(1 for x in self.buffer if x is not None)
        return used, self.size - used

#####################################################
# Part C: Benchmarking & Validation
#####################################################

def frp_buffer_benchmark(p, sensor_data, max_digits=None):
    # Generate cyclic sequence and schedule
    cyclic_sequence, _ = get_cyclic_sequence(p, max_digits)
    schedule, buffer_size = compute_shift_schedule(p, cyclic_sequence)
    
    print(f"Using FRP p={p} (digit grouping={get_prime_grouping(p)})")
    print(f"Generated schedule covers {buffer_size} buffer indices")
    
    # Initialize buffer and execute writes
    buffer = CyclicBuffer(buffer_size)
    start_time = time.time()
    
    for i, reading in enumerate(sensor_data):
        buffer.write(reading, schedule[i % len(schedule)])
    
    elapsed = time.time() - start_time
    
    # Performance metrics
    used, unused = buffer.get_utilization()
    print("\nBenchmark Results:")
    print(f"  Total Writes: {len(sensor_data):,}")
    print(f"  Buffer Size: {buffer_size}")
    print(f"  Utilization: {used}/{buffer_size} ({used/buffer_size:.1%})")
    print(f"  Total Time: {elapsed:.4f}s")
    print(f"  Avg Write Time: {elapsed/len(sensor_data):.2e}s/op")
    print(f"  Final Buffer Sample: {buffer.buffer[:10]}...")
    
    return buffer

def main():
    # Load dataset
    try:
        path = kagglehub.dataset_download("sudhanvahg/hourly-sensor-data-for-forecasting")
        df = pd.read_csv(f"{path}/data.csv")
        sensor_data = df["Count"].values
    except Exception as e:
        print(f"Data loading failed: {e}")
        return

    # Example benchmark configurations
    primes_to_test = [
        (7, None),     # Small 1-digit prime
        (17, None),    # 2-digit prime
        (18229, None),  # Optimal Prime Selection (Equal to Data Length)
    ]

    for p, max_digits in primes_to_test:
        print(f"\n{'='*40}")
        print(f"Running Benchmark for p={p}")
        frp_buffer_benchmark(p, sensor_data, max_digits)

if __name__ == "__main__":
    main()