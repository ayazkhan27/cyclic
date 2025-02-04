import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler

# Import functions from provided files
from cyclicprimerelations import minimal_movement, generate_target_sequences
from FFTStandardDevTest import analyze_cyclic_movements


def analyze_complex_plane(primes_and_sequences):
    for prime, sequence in primes_and_sequences:
        print(f"\nAnalyzing complex plane representation for cyclic prime: {prime}\n")
        
        # Get movement data from existing analysis function
        results = analyze_cyclic_movements(prime, sequence)
        movements = results['fft']
        
        # Represent movements in the complex plane
        complex_movements = np.array([complex(m) for m in movements])
        real_parts = np.real(complex_movements)
        imag_parts = np.imag(complex_movements)
        
        plt.figure(figsize=(10, 6))
        plt.scatter(real_parts, imag_parts, color='blue', marker='o')
        plt.xlabel('Real Part')
        plt.ylabel('Imaginary Part')
        plt.title(f'Complex Plane Representation for Cyclic Prime {prime}')
        plt.grid(True)
        plt.axhline(0, color='black', lw=0.5)
        plt.axvline(0, color='black', lw=0.5)
        plt.show()


def calculate_lyapunov_exponent(primes_and_sequences):
    for prime, sequence in primes_and_sequences:
        print(f"\nCalculating Lyapunov exponent for cyclic prime: {prime}\n")
        
        # Get movement data from existing analysis function
        results = analyze_cyclic_movements(prime, sequence)
        movements = results['fft']
        x_data = np.arange(len(movements))
        
        # Calculate the differences in movement values to simulate divergence
        differences = np.diff(movements)
        abs_differences = np.abs(differences)
        
        try:
            log_differences = np.log(abs_differences[abs_differences > 0])
            log_time = np.log(x_data[1:len(log_differences) + 1])
            slope, intercept = np.polyfit(log_time, log_differences, 1)
            print(f"Estimated Lyapunov Exponent for prime {prime}: {slope}")
        except Exception as e:
            print(f"Lyapunov Exponent calculation failed for prime {prime}: {e}")


def plot_recurrence(primes_and_sequences):
    for prime, sequence in primes_and_sequences:
        print(f"\nGenerating recurrence plot for cyclic prime: {prime}\n")
        
        # Get movement data from existing analysis function
        results = analyze_cyclic_movements(prime, sequence)
        movements = results['fft']
        movements_scaled = StandardScaler().fit_transform(movements.reshape(-1, 1))
        
        # Create a recurrence plot
        distance_matrix = pdist(movements_scaled, metric='euclidean')
        recurrence_matrix = squareform(distance_matrix) < 0.5  # Threshold for recurrence
        
        plt.figure(figsize=(10, 6))
        plt.imshow(recurrence_matrix, cmap='binary', origin='lower')
        plt.title(f'Recurrence Plot for Cyclic Prime {prime}')
        plt.xlabel('Index')
        plt.ylabel('Index')
        plt.show()


def plot_poincare_section(primes_and_sequences):
    for prime, sequence in primes_and_sequences:
        print(f"\nGenerating Poincaré section for cyclic prime: {prime}\n")
        
        # Get movement data from existing analysis function
        results = analyze_cyclic_movements(prime, sequence)
        movements = results['fft']
        
        # Plot Poincaré section - Cross section at y = 0
        zero_crossings = [i for i in range(1, len(movements)) if movements[i-1] * movements[i] < 0]
        x_vals = [movements[i] for i in zero_crossings]
        y_vals = [movements[i+1] for i in zero_crossings[:-1]]
        
        plt.figure(figsize=(10, 6))
        plt.scatter(x_vals, y_vals, color='blue', marker='o')
        plt.xlabel('Movement at Crossing n')
        plt.ylabel('Movement at Crossing n+1')
        plt.title(f'Poincaré Section for Cyclic Prime {prime}')
        plt.grid(True)
        plt.show()


# Example usage
primes_and_sequences = [
    (7, '142857'),
    (17, '0588235294117647'),
    (19, '052631578947368421'),
    (23, '0434782608695652173913')
]

analyze_complex_plane(primes_and_sequences)
calculate_lyapunov_exponent(primes_and_sequences)
plot_recurrence(primes_and_sequences)
plot_poincare_section(primes_and_sequences)
