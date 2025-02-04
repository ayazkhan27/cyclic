import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.fft import fft2, fftshift, fft
from scipy.signal import cwt, ricker

#####################################################
# Full Reptend Primes List
#####################################################
# This list contains full reptend primes. In our context,
# p represents a full reptend prime—a prime for which the repeating
# decimal of 1/p has maximal length (p-1 digits). Think of p as a unique
# identifier or a “data codex” whose repeating decimal is its signature.
primes = np.array([7, 17, 19, 23, 29, 47, 59, 61, 97, 109, 113, 131, 149, 167,
                   179, 181, 193, 223, 229, 233, 257, 263, 269, 313, 337, 367,
                   379, 383, 389, 419, 433, 461, 487, 491, 499, 503, 509, 541,
                   571, 577, 593, 619, 647, 659, 701, 709, 727, 743, 811, 821,
                   823, 857, 863, 887, 937, 941, 953, 971, 977, 983])

#####################################################
# Function: get_cyclic_sequence
#####################################################
# Compute the repeating decimal (the cyclic sequence) of 1/p for a full reptend prime.
# For example, for p = 7, the repeating sequence is "142857".
# This sequence serves as the "data signature" or fingerprint of p.
def get_cyclic_sequence(p):
    remainder = 1
    seen = {}
    sequence = ""
    # Perform long division until a remainder repeats.
    while remainder and remainder not in seen:
        seen[remainder] = len(sequence)
        remainder *= 10
        sequence += str(remainder // p)
        remainder %= p
    if remainder:
        start = seen[remainder]
        sequence = sequence[start:]
    # Ensure the result is exactly (p-1) digits by zero-padding if necessary.
    return sequence.zfill(p - 1)

#####################################################
# Function: generate_target_sequences
#####################################################
# Given a full reptend prime p and its cyclic sequence (the repeating decimal for 1/p),
# generate all cyclic permutations (target sequences) of length equal to the number of digits in p.
# Mathematically, each cyclic permutation corresponds to the repeating decimal for a fraction n/p.
def generate_target_sequences(p, cyclic_sequence):
    seq_len = len(cyclic_sequence)
    group_length = len(str(p))
    cyclic_groups = []
    for i in range(seq_len):
        group = cyclic_sequence[i:i+group_length]
        if len(group) == group_length:
            cyclic_groups.append(group)
        else:
            # Handle wrap-around: append the beginning of the string.
            wrap_group = cyclic_sequence[i:] + cyclic_sequence[:group_length - len(group)]
            cyclic_groups.append(wrap_group)
    # Remove duplicates and sort them.
    cyclic_groups = sorted(set(cyclic_groups))
    # There are exactly (p-1) distinct fractions (n/p for n=1,...,p-1).
    return cyclic_groups[:p - 1]

#####################################################
# Function: minimal_movement
#####################################################
# For a given starting sequence (from 1/p) and a target sequence (for some n/p),
# compute the minimal cyclic rotation (or shift) required to transform the starting sequence
# into the target sequence. The two options (clockwise and anticlockwise) are computed, and
# the one with the smaller absolute value is chosen.
#
# Example for p = 7:
#   - The repeating sequence for 1/7 is "142857".
#   - To obtain the repeating sequence for 2/7, which should be "285714",
#     one can either shift 4 positions to the left (–4) or 2 positions to the right (+2).
#     Since |+2| < |–4|, the minimal movement is +2.
def minimal_movement(start_seq, target_seq, digit_positions, seq_len, cyclic_sequence):
    start_positions = digit_positions[start_seq]
    target_positions = digit_positions[target_seq]
    min_move = seq_len  # Start with a large value
    for s in start_positions:
        for t in target_positions:
            clockwise = (t - s) % seq_len
            anticlockwise = (s - t) % seq_len
            if clockwise <= anticlockwise:
                move = clockwise  # Positive: clockwise rotation
            else:
                move = -anticlockwise  # Negative: anticlockwise rotation
            if abs(move) < abs(min_move):
                min_move = move
    return min_move

#####################################################
# Function: prepare_movement_matrix
#####################################################
# Construct a 2D movement matrix where each row corresponds to a full reptend prime.
# For each prime, we compute the cyclic sequence (the repeating decimal of 1/p) and then
# calculate the minimal movements required to transform the sequence for 1/p to that for n/p.
# These movements (one per fraction) are stored as a row. All rows are padded with zeros to equalize
# their lengths.
def prepare_movement_matrix(primes):
    movement_matrix = []
    max_len = 0
    # Process each full reptend prime.
    for p in primes:
        cyclic_seq = get_cyclic_sequence(p)
        seq_len = len(cyclic_seq)
        # Build a dictionary mapping each cyclic group to its indices in the cycle.
        digit_positions = {}
        group_length = len(str(p))
        for i in range(seq_len):
            group = cyclic_seq[i:i+group_length]
            if len(group) == group_length:
                digit_positions.setdefault(group, []).append(i)
            else:
                wrap = cyclic_seq[i:] + cyclic_seq[:group_length - len(group)]
                digit_positions.setdefault(wrap, []).append(i)
        # Extract target sequences (which represent the repeating decimals for n/p).
        target_seqs = generate_target_sequences(p, cyclic_seq)
        movements = []
        # Use the first target sequence as the starting sequence (corresponding to 1/p).
        start_seq = cyclic_seq[:len(target_seqs[0])]
        # For each target sequence, compute the minimal cyclic rotation.
        for t in target_seqs:
            mov = minimal_movement(start_seq, t, digit_positions, seq_len, cyclic_seq)
            movements.append(mov)
        max_len = max(max_len, len(movements))
        movement_matrix.append(movements)
    # Pad each row to have the same length.
    for i in range(len(movement_matrix)):
        if len(movement_matrix[i]) < max_len:
            movement_matrix[i].extend([0] * (max_len - len(movement_matrix[i])))
    return np.array(movement_matrix)

#####################################################
# Function: fft_2d_analysis
#####################################################
# Perform a 2D Fast Fourier Transform (FFT) on the movement matrix.
# The FFT is shifted so that the zero frequency is centered for visualization.
def fft_2d_analysis(mov_matrix):
    fft_result = fft2(mov_matrix)
    fft_shifted = fftshift(np.abs(fft_result))
    print("FFT Result (magnitude):")
    print(fft_shifted)
    print("Shape of FFT Result:", fft_shifted.shape)
    plt.imshow(fft_shifted, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.title('2D FFT of Cyclic Prime Movements')
    plt.show()
    return fft_result

#####################################################
# Function: wavelet_analysis
#####################################################
# Perform wavelet transform analysis on each row (each prime's movement sequence)
# using the Ricker (Mexican hat) wavelet. This provides a time–frequency (or scale)
# representation that helps reveal how the cyclic shifts behave at different scales.
# The resulting scalograms are plotted for each prime.
def wavelet_analysis(mov_matrix):
    widths = np.arange(1, 31)  # Range of scales for the wavelet transform
    for idx, row in enumerate(mov_matrix):
        cwt_result = cwt(row, ricker, widths)
        print(f"Wavelet Transform for prime at index {idx} (prime = {primes[idx]}):")
        print(cwt_result)
        print("Shape:", cwt_result.shape)
        plt.imshow(cwt_result, extent=[0, len(row), 1, 31], cmap='PRGn', aspect='auto',
                   vmax=abs(cwt_result).max(), vmin=-abs(cwt_result).max())
        plt.title(f'Wavelet Transform (Prime {primes[idx]})')
        plt.xlabel('Index in Movement Sequence')
        plt.ylabel('Wavelet Scale')
        plt.colorbar()
        plt.show()

#####################################################
# Contextual Comments: Real-World Analogy for Variables
#####################################################
# In our analysis:
#
# - "p" represents a full reptend prime, which in a real-world context could be seen as a unique 
#    identifier or a data code.
#
# - The "cyclic sequence" is the repeating decimal of 1/p (for example, "142857" for p=7). 
#    This is like the unique data signature or fingerprint of p.
#
# - The "iterative fractions" (1/p, 2/p, ..., (p-1)/p) correspond to the different cyclic permutations 
#    of the repeating sequence. They can be thought of as different perspectives or views of the data signature.
#
# - The "minimal movement" is the smallest cyclic rotation needed to convert the repeating sequence 
#    for 1/p into that for n/p. In other words, it quantifies how the data signature shifts from one 
#    fraction to the next.
#
# If you can deduce a general pattern in how the cyclic sequence shifts (i.e., in the minimal movements) 
# from 1/p to 2/p, 3/p, ... up to (p-1)/p, then you might be able to predict the structure of the repeating 
# decimal from p alone—and ultimately derive a formula characterizing full reptend primes.

#####################################################
# Main Code Execution
#####################################################
# Generate the 2D movement matrix for our list of full reptend primes.
mov_matrix = prepare_movement_matrix(primes)
print("Movement Matrix:")
print(mov_matrix)
print("Shape of Movement Matrix:", mov_matrix.shape)

# Perform a 2D FFT analysis on the movement matrix.
fft_result = fft_2d_analysis(mov_matrix)

# Perform wavelet analysis on the movement matrix.
wavelet_analysis(mov_matrix)
