import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft2, fftshift
from scipy.signal import cwt, ricker

# Import your functions from cyclicprimerelations.py
from cyclicprimerelations import generate_target_sequences, minimal_movement

def prepare_movement_matrix(primes, sequences):
    """ Generate a 2D movement matrix for primes and their sequences. """
    movement_matrix = []
    
    # Determine the maximum length of movements
    max_length = 0
    temp_movement_matrix = []
    
    # First pass to determine maximum length
    for prime, cyclic_sequence in zip(primes, sequences):
        sequence_length = len(cyclic_sequence)
        digit_positions = {}
        group_length = len(str(prime))
        
        # Generate target sequences
        target_sequences = generate_target_sequences(prime, cyclic_sequence)
        movements = []
        
        # Define positions for single or multi-digit sequences
        for i in range(sequence_length):
            group = cyclic_sequence[i:i+group_length]
            if len(group) == group_length:
                if group in digit_positions:
                    digit_positions[group].append(i)
                else:
                    digit_positions[group] = [i]
            else:  # Wrap-around case
                wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length-len(group)]
                if wrap_around_group in digit_positions:
                    digit_positions[wrap_around_group].append(i)
                else:
                    digit_positions[wrap_around_group] = [i]

        # Calculate movements
        start_sequence = cyclic_sequence[:len(target_sequences[0])]
        for target_sequence in target_sequences:
            movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence)
            movements.append(movement)
        
        temp_movement_matrix.append(movements)
        max_length = max(max_length, len(movements))
    
    # Second pass to pad movements to the same length
    for movements in temp_movement_matrix:
        if len(movements) < max_length:
            movements.extend([0] * (max_length - len(movements)))
        movement_matrix.append(movements)
    
    # Print movement matrix and its shape
    print("Movement Matrix:")
    for row in movement_matrix:
        print(row)
    print(f"Shape of Movement Matrix: {np.shape(movement_matrix)}")
    
    return np.array(movement_matrix)

def fft_2d_analysis(movement_matrix):
    """ Perform 2D FFT on the movement matrix and visualize the result. """
    fft_result = fft2(movement_matrix)
    fft_shifted = fftshift(np.abs(fft_result))  # Center FFT result for visualization
    
    # Print FFT results
    print("FFT Result (magnitude):")
    print(fft_shifted)
    print(f"Shape of FFT Result: {fft_shifted.shape}")
    
    plt.imshow(fft_shifted, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.title('2D FFT of Cyclic Prime Movements')
    plt.show()

    return fft_result

def wavelet_analysis(movement_matrix):
    """ Perform wavelet analysis on the movement matrix. """
    widths = np.arange(1, 31)
    for idx, row in enumerate(movement_matrix):
        cwt_result = cwt(row, ricker, widths)
        
        # Print Wavelet Transform Results
        print(f"Wavelet Transform (Prime {idx+1}):")
        print(cwt_result)
        print(f"Shape of Wavelet Transform Result: {cwt_result.shape}")
        
        plt.imshow(cwt_result, extent=[0, len(row), 1, 31], cmap='PRGn', aspect='auto',
                   vmax=abs(cwt_result).max(), vmin=-abs(cwt_result).max())
        plt.title(f'Wavelet Transform (Prime {idx+1})')
        plt.show()

# Example usage
primes = [7, 17, 19, 23]
sequences = ['142857', '0588235294117647', '052631578947368421', '0434782608695652173913']

# Step 1: Prepare 2D movement matrix
movement_matrix = prepare_movement_matrix(primes, sequences)

# Step 2: Perform 2D FFT analysis
fft_result = fft_2d_analysis(movement_matrix)

# Step 3: Perform Wavelet analysis
wavelet_analysis(movement_matrix)
