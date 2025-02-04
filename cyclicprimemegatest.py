import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from scipy.fft import fft
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from scipy.signal import find_peaks
from scipy.stats import entropy
from sklearn.feature_selection import mutual_info_regression
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import ARDRegression

# Import functions from provided files
from cyclicprimerelations import minimal_movement, generate_target_sequences
from FFTStandardDevTest import analyze_cyclic_movements


def analyze_new_properties(primes_and_sequences):
    results_summary = []

    for prime, sequence in primes_and_sequences:
        print(f"\nAnalyzing cyclic prime: {prime}\n")

        # Get movement data from existing analysis function
        results = analyze_cyclic_movements(prime, sequence)
        movements = results['fft']
        mean_movement = results['mean']
        std_dev_movement = results['std_dev']
        max_movement = results['max_movement']

        # 1. Fractal Analysis using Box Counting
        box_counts = []
        scales = np.linspace(1, len(movements) // 2, num=10, dtype=int)
        for scale in scales:
            reshaped = np.array_split(movements, len(movements) // scale)
            non_empty_boxes = sum([1 for segment in reshaped if np.any(segment)])
            box_counts.append(non_empty_boxes)
        results_summary.append({'prime': prime, 'scales': scales, 'box_counts': box_counts})

        # 2. Permutation Entropy
        movements_normalized = (movements - np.min(movements)) / (np.max(movements) - np.min(movements))
        pe_order = 3
        perm_counts = np.zeros(math.factorial(pe_order))
        for i in range(len(movements_normalized) - pe_order + 1):
            pattern = tuple(np.argsort(movements_normalized[i:i + pe_order]))
            perm_index = sum([j * math.factorial(pe_order - k - 1) for k, j in enumerate(pattern)])
            perm_counts[perm_index] += 1
        perm_entropy = entropy(perm_counts)
        results_summary[-1].update({'permutation_entropy': perm_entropy})

        # 3. Cross Correlation with Previous Prime (if available)
        if len(results_summary) > 1:
            prev_movements = results_summary[-2]['movements']
            cross_corr = np.correlate(prev_movements, movements, mode='full')
            results_summary[-1].update({'cross_correlation': cross_corr})
        else:
            results_summary[-1].update({'cross_correlation': None})

        # 4. Shannon Entropy
        shannon_entropy = entropy(np.histogram(movements.real, bins='auto')[0])
        results_summary[-1].update({'shannon_entropy': shannon_entropy})

        # 5. Autoregressive (AR) Model
        try:
            X = np.arange(len(movements)).reshape(-1, 1)
            y = movements
            ar_model = LinearRegression().fit(X, y)
            ar_coeff = ar_model.coef_
            results_summary[-1].update({'ar_coeff': ar_coeff})
        except Exception as e:
            results_summary[-1].update({'ar_coeff': None})

        # 6. Mutual Information for Movement
        try:
            movements_reshaped = np.array(movements).reshape(-1, 1)
            mi = mutual_info_regression(movements_reshaped[:-1], movements[1:])
            results_summary[-1].update({'mutual_information': mi})
        except Exception as e:
            results_summary[-1].update({'mutual_information': None})

        # Append movements for potential use in cross-correlation
        results_summary[-1].update({'movements': movements})

    # Display consolidated plots for all analyses
    plot_new_results(results_summary)


def plot_new_results(results_summary):
    # Box Counting Plot
    plt.figure(figsize=(15, 10))
    for result in results_summary:
        plt.plot(result['scales'], result['box_counts'], label=f"Prime {result['prime']}")
    plt.xlabel('Scale')
    plt.ylabel('Box Count')
    plt.title('Fractal Box Counting Analysis for Cyclic Primes')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Permutation Entropy Results
    plt.figure(figsize=(15, 10))
    primes = [result['prime'] for result in results_summary]
    permutation_entropies = [result['permutation_entropy'] for result in results_summary]
    plt.bar(primes, permutation_entropies, color='blue')
    plt.xlabel('Prime')
    plt.ylabel('Permutation Entropy')
    plt.title('Permutation Entropy for Cyclic Primes')
    plt.grid(True)
    plt.show()

    # Shannon Entropy Results
    plt.figure(figsize=(15, 10))
    shannon_entropies = [result['shannon_entropy'] for result in results_summary]
    plt.bar(primes, shannon_entropies, color='green')
    plt.xlabel('Prime')
    plt.ylabel('Shannon Entropy')
    plt.title('Shannon Entropy for Cyclic Primes')
    plt.grid(True)
    plt.show()

    # Cross Correlation Plot (for each prime)
    for result in results_summary:
        if result['cross_correlation'] is not None:
            plt.figure(figsize=(15, 10))
            plt.plot(result['cross_correlation'], label=f"Prime {result['prime']} Cross Correlation")
            plt.xlabel('Lag')
            plt.ylabel('Cross Correlation')
            plt.title(f'Cross Correlation for Cyclic Prime {result["prime"]} with Previous Prime')
            plt.legend()
            plt.grid(True)
            plt.show()

    # Autoregressive Coefficients
    plt.figure(figsize=(15, 10))
    ar_coeffs = [result['ar_coeff'][0] if result['ar_coeff'] is not None else 0 for result in results_summary]
    plt.bar(primes, ar_coeffs, color='purple')
    plt.xlabel('Prime')
    plt.ylabel('AR Coefficient')
    plt.title('Autoregressive Coefficients for Cyclic Primes')
    plt.grid(True)
    plt.show()

    # Mutual Information Results
    plt.figure(figsize=(15, 10))
    mutual_informations = [result['mutual_information'][0] if result['mutual_information'] is not None else 0 for result in results_summary]
    plt.bar(primes, mutual_informations, color='orange')
    plt.xlabel('Prime')
    plt.ylabel('Mutual Information')
    plt.title('Mutual Information between Successive Movements for Cyclic Primes')
    plt.grid(True)
    plt.show()


# Example usage
primes_and_sequences = [
    (7, '142857'),
    (17, '0588235294117647'),
    (19, '052631578947368421'),
    (23, '0434782608695652173913')
]

analyze_new_properties(primes_and_sequences)
