import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft
from sympy import divisors

# Import functions from your existing script
from cyclicprimerelations import minimal_movement, generate_target_sequences, analyze_cyclic_prime

def analyze_cyclic_movements(prime, cyclic_sequence):
    # Use your existing function to get the movements
    analyze_cyclic_prime(prime, cyclic_sequence)
    
    # Re-calculate movements to use in our analysis
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

    # Convert movements to numpy array
    movements = np.array(movements)
    
    # 1. Fourier Transform
    fft_result = fft(movements)
    frequencies = np.fft.fftfreq(len(movements))
    
    # 2. Basic Statistics
    mean = np.mean(movements)
    std_dev = np.std(movements)
    max_movement = np.max(np.abs(movements))
    
    # 3. Periodicity Analysis
    potential_periods = divisors(prime - 1)[1:]  # Exclude 1 as a trivial divisor
    autocorrelations = [np.correlate(movements, np.roll(movements, shift))[0] for shift in potential_periods]
    
    # 4. Movement Distribution
    unique_movements, movement_counts = np.unique(movements, return_counts=True)
    
    # 5. Cumulative Sum Analysis
    cumulative_sum = np.cumsum(movements)
    
    # Plotting
    fig, axs = plt.subplots(3, 2, figsize=(15, 20))
    fig.suptitle(f'Analysis of Cyclic Movements for Prime {prime}')
    
    # Plot original movements
    axs[0, 0].plot(movements)
    axs[0, 0].set_title('Original Movements')
    axs[0, 0].set_xlabel('Index')
    axs[0, 0].set_ylabel('Movement')
    
    # Plot Fourier Transform
    axs[0, 1].plot(frequencies, np.abs(fft_result))
    axs[0, 1].set_title('Fourier Transform')
    axs[0, 1].set_xlabel('Frequency')
    axs[0, 1].set_ylabel('Magnitude')
    
    # Plot Autocorrelations
    axs[1, 0].bar(potential_periods, autocorrelations)
    axs[1, 0].set_title('Autocorrelations at Potential Periods')
    axs[1, 0].set_xlabel('Period')
    axs[1, 0].set_ylabel('Autocorrelation')
    
    # Plot Movement Distribution
    axs[1, 1].bar(unique_movements, movement_counts)
    axs[1, 1].set_title('Movement Distribution')
    axs[1, 1].set_xlabel('Movement')
    axs[1, 1].set_ylabel('Count')
    
    # Plot Cumulative Sum
    axs[2, 0].plot(cumulative_sum)
    axs[2, 0].set_title('Cumulative Sum of Movements')
    axs[2, 0].set_xlabel('Index')
    axs[2, 0].set_ylabel('Cumulative Sum')
    
    # Text summary
    summary = f"""
    Prime: {prime}
    Mean Movement: {mean:.2f}
    Standard Deviation: {std_dev:.2f}
    Max Absolute Movement: {max_movement}
    """
    axs[2, 1].text(0.1, 0.1, summary, fontsize=12)
    axs[2, 1].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'fft': fft_result,
        'mean': mean,
        'std_dev': std_dev,
        'max_movement': max_movement,
        'autocorrelations': dict(zip(potential_periods, autocorrelations)),
        'movement_distribution': dict(zip(unique_movements, movement_counts))
    }

# Analyze cyclic primes
primes_and_sequences = [
    (7, '142857'),
    (17, '0588235294117647'),
    (19, '052631578947368421'),
    (23, '0434782608695652173913')
]

for prime, sequence in primes_and_sequences:
    results = analyze_cyclic_movements(prime, sequence)
    print(f"\nAnalysis results for prime {prime}:")
    print(f"Mean: {results['mean']}")
    print(f"Standard Deviation: {results['std_dev']}")
    print(f"Max Movement: {results['max_movement']}")
    print("Autocorrelations:", results['autocorrelations'])
    print("Movement Distribution:", results['movement_distribution'])