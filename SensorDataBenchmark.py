#!/usr/bin/env python3
"""
FRP-Based Circular Buffer Scheduling on Sensor Data (Corrected Implementation)

This script uses the properties of Full Reptend Primes (FRPs) to generate a cyclic schedule
for writing sensor data into a circular buffer. The key correction ensures that all buffer
indices are covered by deriving the schedule from the order of remainders during the cyclic
sequence generation.
"""

import numpy as np
import pandas as pd
import time
import kagglehub

#####################################################
# PART A: FRP CYCLIC SEQUENCE & SCHEDULING FUNCTIONS
#####################################################

def get_cyclic_sequence(p, max_digits=None):
    """
    Compute the repeating decimal (cyclic sequence) of 1/p for a full reptend prime,
    and track the order of remainders to generate the schedule.
    
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

def compute_cyclic_schedule(remainder_order):
    """
    Compute the cyclic scheduling order from the remainder sequence.
    Each remainder r corresponds to buffer index (r-1).
    """
    return np.array([r - 1 for r in remainder_order], dtype=int)

#####################################################
# PART B: CIRCULAR BUFFER IMPLEMENTATION
#####################################################

class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size

    def write_at(self, index, data):
        """Write data to the buffer at the specified index."""
        self.buffer[index % self.size] = data  # Ensure index wraps correctly

    def read_all(self):
        """Return a copy of the buffer contents."""
        return list(self.buffer)

def benchmark_circular_buffer_FRP(p, sensor_data, max_digits=None):
    # Get cyclic sequence and remainder order
    cyclic_seq, remainder_order = get_cyclic_sequence(p, max_digits)
    schedule = compute_cyclic_schedule(remainder_order)
    
    print(f"FRP Scheduling Order for p={p} (length={len(schedule)}):")
    print(schedule[:20], "...")  # Print first 20 elements for preview
    
    # Initialize buffer with size equal to schedule length
    buffer_size = len(schedule)
    circ_buffer = CircularBuffer(buffer_size)
    
    # Write data using the schedule
    start_time = time.time()
    schedule_length = len(schedule)
    for i, reading in enumerate(sensor_data):
        circ_buffer.write_at(schedule[i % schedule_length], reading)
    elapsed = time.time() - start_time
    
    print(f"\nFRP-Based Circular Buffer Benchmark for p={p}:")
    print(f"  Sensor Readings Written: {len(sensor_data)}")
    print(f"  Buffer Size: {buffer_size}")
    print(f"  Total Write Time: {elapsed:.6f} seconds")
    print(f"  Average Write Time per Reading: {elapsed/len(sensor_data):.8f} seconds")
    
    # Check for unwritten slots
    final_buffer = circ_buffer.read_all()
    unwritten = final_buffer.count(None)
    print(f"  Unwritten Slots: {unwritten}/{buffer_size}")
    print("  Final Buffer Sample:", final_buffer[:20])
    print("-" * 60)
    return circ_buffer

#####################################################
# MAIN FUNCTION
#####################################################

def main():
    # Download dataset
    try:
        path = kagglehub.dataset_download("sudhanvahg/hourly-sensor-data-for-forecasting")
        print("Dataset path:", path)
    except Exception as e:
        print("Download error:", e)
        return

    # Load data
    try:
        df = pd.read_csv(f"{path}/data.csv")
        sensor_data = df["Count"].to_numpy()
    except Exception as e:
        print("Data loading error:", e)
        return

    # Configuration - Example with p=17 (small FRP)
    p = 32779  # Full reptend prime (17-1=16 digit cycle)
    max_digits = None  # Use full cycle length (p-1=16)

    print(f"\n=== FRP Circular Buffer Benchmark (p={p}) ===")
    benchmark_circular_buffer_FRP(p, sensor_data, max_digits)

if __name__ == "__main__":
    main()