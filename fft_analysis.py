import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from cyclicprimerelations import minimal_movement, generate_target_sequences

def analyze_fft_for_prime(prime, cyclic_sequence):
    # Generate movements
    sequence_length = len(cyclic_sequence)
    digit_positions = {}
    group_length = len(str(prime))
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
    
    target_sequences = generate_target_sequences(prime, cyclic_sequence)
    movements = []
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence)
        movements.append(movement)

    # Perform FFT
    movements_array = np.array(movements)
    fft_result = fft(movements_array)
    frequencies = fftfreq(len(movements_array))

    # Plot original movements and FFT results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle(f'FFT Analysis for Cyclic Prime {prime}')

    # Original movements
    ax1.plot(movements_array)
    ax1.set_title('Original Movements')
    ax1.set_xlabel('Index')
    ax1.set_ylabel('Movement')

    # FFT magnitude
    ax2.plot(frequencies, np.abs(fft_result))
    ax2.set_title('FFT Magnitude')
    ax2.set_xlabel('Frequency')
    ax2.set_ylabel('Magnitude')
    ax2.set_xlim(0, 0.5)  # Show only positive frequencies up to Nyquist frequency

    plt.tight_layout()
    plt.show()

    # Analyze dominant frequencies
    sorted_frequencies = sorted(zip(frequencies, np.abs(fft_result)), key=lambda x: x[1], reverse=True)
    dominant_frequencies = sorted_frequencies[1:6]  # Exclude DC component (0 frequency)

    print(f"Dominant frequencies for prime {prime}:")
    for freq, mag in dominant_frequencies:
        print(f"Frequency: {freq:.4f}, Magnitude: {mag:.4f}")

    return fft_result, frequencies

# Analyze cyclic primes
primes_and_sequences = [
    (7, '142857'),
    (17, '0588235294117647'),
    (19, '052631578947368421'),
    (23, '0434782608695652173913')
]

for prime, sequence in primes_and_sequences:
    fft_result, frequencies = analyze_fft_for_prime(prime, sequence)