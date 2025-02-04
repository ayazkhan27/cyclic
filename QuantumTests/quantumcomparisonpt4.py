# quantumcomparisonpt4.py

import numpy as np
from scipy.spatial import procrustes
from scipy.stats import wasserstein_distance, ks_2samp  # Added ks_2samp import
from quantumcomparisonpt3 import (
    simulate_quantum_angular_momentum,
    generate_minimal_movements,
    perform_statistical_tests,
    perform_machine_learning_analysis,
    plot_histograms,
    plot_clusters,
    plot_confusion_matrix,
    full_reptend_primes
)
# Additional imports if needed from quantumcomparisonpt3

# Function to calculate lateral inversion of a dataset
def lateral_inversion(data):
    return -data

# Function to perform Procrustes analysis for dataset alignment
def procrustes_analysis(data1, data2):
    _, _, disparity = procrustes(data1.reshape(-1, 1), data2.reshape(-1, 1))
    return disparity

# Cross-correlation function to find phase shift alignment
def cross_correlation(reptend, quantum):
    correlation = np.correlate(reptend, quantum, mode='full')
    shift_index = correlation.argmax() - (len(reptend) - 1)
    return shift_index, correlation[correlation.argmax()]

# Bootstrap testing function for robustness analysis
def bootstrap_ks_test(data1, data2, n_iter=1000):
    p_values = []
    for _ in range(n_iter):
        sample1 = np.random.choice(data1, size=len(data1), replace=True)
        sample2 = np.random.choice(data2, size=len(data2), replace=True)
        _, p_value = ks_2samp(sample1, sample2)
        p_values.append(p_value)
    return np.mean(p_values), np.std(p_values)

# Main function to perform extended analysis
def main():
    # Generate minimal movements for each full reptend prime and simulate quantum data
    full_reptend_data = []
    for p in full_reptend_primes:
        if p > 3:  # Skip primes with short sequences
            minimal_movements, superposition_movement, superposition_proportion, group_elements = generate_minimal_movements(p)
            full_reptend_data.append(minimal_movements)

    # Flatten the full reptend prime minimal movements
    reptend_movements = np.array([abs(m) for movements in full_reptend_data for m in movements])
    reptend_normalized = (reptend_movements - np.mean(reptend_movements)) / np.std(reptend_movements)

    # Simulate quantum angular momentum data
    quantum_magnitudes = simulate_quantum_angular_momentum(len(reptend_normalized), max(reptend_movements))
    quantum_normalized = (quantum_magnitudes - np.mean(quantum_magnitudes)) / np.std(quantum_magnitudes)

    # Perform lateral inversion
    quantum_inverted = lateral_inversion(quantum_normalized)

    # Perform Procrustes analysis
    disparity = procrustes_analysis(reptend_normalized, quantum_inverted)
    print(f"Procrustes Disparity (Inverted Quantum): {disparity}")

    # Perform cross-correlation to find phase shift alignment
    shift, max_corr = cross_correlation(reptend_normalized, quantum_normalized)
    print(f"Optimal Shift in Cross-correlation: {shift}, Max Correlation: {max_corr}")

    # Compute Wasserstein Distance for additional similarity measure
    wasserstein_dist = wasserstein_distance(reptend_normalized, quantum_normalized)
    print(f"Wasserstein Distance: {wasserstein_dist}")

    # Bootstrap KS test for robust p-value estimation
    mean_p_value, p_value_std = bootstrap_ks_test(reptend_normalized, quantum_normalized)
    print(f"Bootstrap KS Mean p-value: {mean_p_value}, Std Dev: {p_value_std}")

    # Perform statistical tests using function from quantumcomparisonpt3
    stats_results = perform_statistical_tests(reptend_normalized, quantum_normalized)
    print("\nStatistical Test Results:")
    print(f"Kolmogorov-Smirnov test statistic: {stats_results['ks_statistic']}")
    print(f"p-value (KS Test): {stats_results['ks_p_value']}")
    print(f"Mann-Whitney U test statistic: {stats_results['mw_statistic']}")
    print(f"p-value (Mann-Whitney U Test): {stats_results['mw_p_value']}")
    print(f"Chi-Squared test statistic: {stats_results['chi2_stat']}")
    print(f"p-value (Chi-Squared Test): {stats_results['chi2_p_value']}")

    # Interpretations based on p-values
    print("\nInterpretation of Results:")
    if stats_results['ks_p_value'] < 0.05:
        print("Kolmogorov-Smirnov Test: The distributions are statistically different.")
    else:
        print("Kolmogorov-Smirnov Test: No significant difference between distributions.")

    if stats_results['mw_p_value'] < 0.05:
        print("Mann-Whitney U Test: The distributions are statistically different.")
    else:
        print("Mann-Whitney U Test: No significant difference between distributions.")

    if stats_results['chi2_p_value'] < 0.05:
        print("Chi-Squared Test: The distributions are statistically different.")
    else:
        print("Chi-Squared Test: No significant difference between distributions.")

    # Visualization functions from quantumcomparisonpt3
    plot_histograms(reptend_normalized, quantum_normalized)
    combined_data = np.concatenate((reptend_normalized, quantum_normalized))
    labels = np.array(['Reptend'] * len(reptend_normalized) + ['Quantum'] * len(quantum_normalized))
    ml_results = perform_machine_learning_analysis(combined_data, labels)
    plot_clusters(combined_data, ml_results['clusters'])
    plot_confusion_matrix(ml_results['confusion_matrix'])

    # Print Machine Learning Results
    print(f"\nCross-validation Accuracy: {np.mean(ml_results['scores']):.2f} ± {np.std(ml_results['scores']):.2f}")
    print("\nClassification Report:")
    print(ml_results['class_report'])

    # Error Analysis
    cm = ml_results['confusion_matrix']
    false_positives = cm[0][1]
    false_negatives = cm[1][0]
    print("Confusion Matrix:")
    print(cm)
    print("\nError Analysis:")
    print(f"False Positives (Type I Errors): {false_positives}")
    print(f"False Negatives (Type II Errors): {false_negatives}")

# Execute main function
if __name__ == "__main__":
    main()
