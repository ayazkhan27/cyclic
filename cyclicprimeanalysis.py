import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from mpl_toolkits.mplot3d import Axes3D

# Import functions from provided files
from cyclicprimerelations import minimal_movement, generate_target_sequences, analyze_cyclic_prime
from FFTStandardDevTest import analyze_cyclic_movements


def run_full_analysis(primes_and_sequences):
    results_summary = []
    for prime, sequence in primes_and_sequences:
        print(f"Analyzing cyclic prime: {prime}\n")
        
        # 1. Analyze Movements and Plot in 2D
        results = analyze_cyclic_movements(prime, sequence)
        movements = results['fft']
        mean_movement = results['mean']
        std_dev_movement = results['std_dev']
        max_movement = results['max_movement']
        
        # Store results for further analysis
        results_summary.append({
            'prime': prime,
            'mean': mean_movement,
            'std_dev': std_dev_movement,
            'max_movement': max_movement,
            'autocorrelations': results['autocorrelations'],
            'movement_distribution': results['movement_distribution']
        })

        # 2. Perform Fourier Analysis and Output Frequencies
        fft_magnitude = np.abs(movements)
        fft_frequencies = fftfreq(len(movements))
        print(f"Fourier Frequencies and Magnitudes for prime {prime}:\n")
        for freq, mag in zip(fft_frequencies, fft_magnitude):
            print(f"Frequency: {freq}, Magnitude: {mag}")
        print("\n")

        # 3. Generate 2D Visualization of Movements
        generate_2d_movement_plot(prime, sequence, movements)
        
        # 4. Generate Improved 3D Cascading Staircase Plot
        generate_improved_3d_cascading_plot(prime, sequence, movements)
        
        print("--------------------------------------------------\n")

    # 5. Compare Summarized Results
    summarize_results(results_summary)


def generate_2d_movement_plot(prime, sequence, movements):
    plt.figure(figsize=(10, 6))
    plt.plot(movements, marker='o', linestyle='-', color='blue')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.xlabel('Fraction Index (n/p)')
    plt.ylabel('Minimal Movement')
    plt.title(f'Movements for Cyclic Prime {prime}')
    plt.grid(True)
    plt.show()


def generate_improved_3d_cascading_plot(prime, sequence, movements):
    # Prepare 3D Plot
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    z = 0
    x_vals = []
    y_vals = []
    z_vals = []
    colors = []

    # Identify superposition movement as (p-1)/2
    superposition_movement = (prime - 1) // 2
    superposition_indices = [i for i, m in enumerate(movements) if abs(m) == superposition_movement]

    for i in range(4):  # Change the range for more steps
        for idx, (n, m) in enumerate(zip(range(1, prime), movements)):
            x_vals.append((i * prime) + n)
            y_vals.append(m)
            z_vals.append(z)
            if idx in superposition_indices:
                colors.append('green' if m > 0 else 'yellow')
            else:
                colors.append('blue')
        z += 1
        x_vals.append(i * prime + prime)
        y_vals.append(0)
        z_vals.append(z)
        colors.append('blue')

        # Alternate superposition movement for next level
        for idx in superposition_indices:
            movements[idx] = -movements[idx]

    ax.plot(x_vals, y_vals, z_vals, color='blue', alpha=0.5)
    for x, y, z, c in zip(x_vals, y_vals, z_vals, colors):
        ax.scatter(x, y, z, color=c)

    ax.set_xlabel('Fraction (n/p)')
    ax.set_ylabel('Movement on Dial')
    ax.set_zlabel('Z Axis')
    ax.set_title(f'3D Minimal Movements for Cyclic Prime {prime}')
    plt.show()


def summarize_results(results_summary):
    print("Summary of Results for All Analyzed Primes:\n")
    for result in results_summary:
        print(f"Prime: {result['prime']}\n")
        print(f"Mean Movement: {result['mean']}\n")
        print(f"Standard Deviation: {result['std_dev']}\n")
        print(f"Maximum Movement: {result['max_movement']}\n")
        print(f"Autocorrelations: {result['autocorrelations']}\n")
        print(f"Movement Distribution: {result['movement_distribution']}\n")
        print("--------------------------------------------------\n")


# Example usage
primes_and_sequences = [
    (7, '142857'),
    (17, '0588235294117647'),
    (19, '052631578947368421'),
    (23, '0434782608695652173913')
]

run_full_analysis(primes_and_sequences)
