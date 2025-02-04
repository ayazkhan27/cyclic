import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress

# Import functions from provided files
from cyclicprimerelations import minimal_movement, generate_target_sequences
from FFTStandardDevTest import analyze_cyclic_movements

# Harmonic Model Function (Sine Wave)
def harmonic_model(x, A, omega, phi, C):
    return A * np.sin(omega * x + phi) + C

# Brownian Motion Model Function
def brownian_motion_model(x, D):
    return np.sqrt(2 * D * x)


def analyze_movement_patterns(primes_and_sequences):
    for prime, sequence in primes_and_sequences:
        print(f"\nAnalyzing advanced properties for cyclic prime: {prime}\n")
        
        # Get movement data from existing analysis function
        results = analyze_cyclic_movements(prime, sequence)
        movements = results['fft']
        x_data = np.arange(len(movements))

        # Harmonic Balance Test
        try:
            popt, _ = curve_fit(harmonic_model, x_data, movements, p0=[1, 2 * np.pi / prime, 0, 0])
            A, omega, phi, C = popt
            print(f"Harmonic Model Parameters for prime {prime}: A={A}, omega={omega}, phi={phi}, C={C}")
            plt.figure(figsize=(10, 6))
            plt.plot(x_data, movements, 'b-', label='Data')
            plt.plot(x_data, harmonic_model(x_data, *popt), 'r--', label='Harmonic Fit')
            plt.xlabel('Fraction Index (n/p)')
            plt.ylabel('Movement')
            plt.title(f'Harmonic Balance Analysis for Cyclic Prime {prime}')
            plt.legend()
            plt.grid(True)
            plt.show()
        except Exception as e:
            print(f"Harmonic Balance fitting failed for prime {prime}: {e}")

        # Brownian Motion Analysis (Standard Deviation vs. Time)
        time_steps = x_data
        standard_devs = np.sqrt(np.cumsum(np.square(movements - np.mean(movements))))

        try:
            slope, intercept, r_value, p_value, std_err = linregress(time_steps, standard_devs)
            print(f"Brownian Motion Analysis for prime {prime}: Slope (D) = {slope}, R^2 = {r_value**2}")
            plt.figure(figsize=(10, 6))
            plt.plot(time_steps, standard_devs, 'b-', label='Standard Deviation')
            plt.plot(time_steps, slope * time_steps + intercept, 'r--', label='Brownian Fit')
            plt.xlabel('Time Steps')
            plt.ylabel('Standard Deviation')
            plt.title(f'Brownian Motion Analysis for Cyclic Prime {prime}')
            plt.legend()
            plt.grid(True)
            plt.show()
        except Exception as e:
            print(f"Brownian Motion analysis failed for prime {prime}: {e}")

        # Fractal-Like Behavior Analysis
        try:
            log_time_steps = np.log(time_steps[1:])
            log_standard_devs = np.log(standard_devs[1:])
            slope, intercept = np.polyfit(log_time_steps, log_standard_devs, 1)
            print(f"Fractal Dimension Analysis for prime {prime}: Estimated Fractal Dimension = {slope}")
            plt.figure(figsize=(10, 6))
            plt.plot(log_time_steps, log_standard_devs, 'b-', label='Log-Log Data')
            plt.plot(log_time_steps, slope * log_time_steps + intercept, 'r--', label='Linear Fit')
            plt.xlabel('Log(Time Steps)')
            plt.ylabel('Log(Standard Deviation)')
            plt.title(f'Fractal Dimension Analysis for Cyclic Prime {prime}')
            plt.legend()
            plt.grid(True)
            plt.show()
        except Exception as e:
            print(f"Fractal Dimension analysis failed for prime {prime}: {e}")


# Example usage
primes_and_sequences = [
    (7, '142857'),
    (17, '0588235294117647'),
    (19, '052631578947368421'),
    (23, '0434782608695652173913')
]

analyze_movement_patterns(primes_and_sequences)