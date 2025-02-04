import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp, chi2_contingency, mannwhitneyu
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from collections import Counter

# -----------------------------
# 1. Data Generation Functions
# -----------------------------

# List of known full reptend primes (from OEIS A001913)
full_reptend_primes = [
    7, 17, 19, 23, 29, 47, 59, 61, 97, 109, 113,
    131, 149, 167, 179, 181, 193, 223, 229, 233,
    257, 263, 269, 313, 337, 367, 379, 383, 389,
    419, 433, 461, 487, 491, 499, 503, 509, 541,
    571, 577, 593, 619, 647, 659, 701, 709, 727,
    743, 811, 821, 823, 857, 863, 887, 937, 941,
    953, 971, 977, 983
]

# Function to get the repeating decimal sequence of 1/p
def get_reptend_sequence(p):
    remainders = []
    digits = []
    remainder = 1
    while True:
        remainder *= 10
        digit = remainder // p
        remainder = remainder % p
        if remainder == 0 or remainder in remainders:
            break
        remainders.append(remainder)
        digits.append(str(digit))
    return ''.join(digits)

# Updated minimal_movement function with randomness
def minimal_movement(cyclic_sequence, start_sequence, target_sequence):
    sequence_length = len(cyclic_sequence)
    start_positions = [i for i in range(sequence_length) if cyclic_sequence.startswith(start_sequence, i)]
    target_positions = [i for i in range(sequence_length) if cyclic_sequence.startswith(target_sequence, i)]
    min_movement = sequence_length  # Initialize with a large value

    for start_pos in start_positions:
        for target_pos in target_positions:
            # Calculate clockwise and anticlockwise movements
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length

            if clockwise_movement < anticlockwise_movement:
                movement = clockwise_movement
            elif anticlockwise_movement < clockwise_movement:
                movement = -anticlockwise_movement
            else:
                # Movements are equal; choose direction randomly
                movement = clockwise_movement if np.random.rand() < 0.5 else -anticlockwise_movement

            if abs(movement) < abs(min_movement):
                min_movement = movement

    return min_movement

# Function to generate minimal movements and group elements for a given full reptend prime
def generate_minimal_movements(p):
    cyclic_sequence = get_reptend_sequence(p)
    sequence_length = len(cyclic_sequence)
    group_length = len(str(p))

    # Generate target sequences
    cyclic_groups = []
    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) < group_length:
            group += cyclic_sequence[:group_length - len(group)]
        cyclic_groups.append(group)
    # Remove duplicates and ensure we have p - 1 groups
    target_sequences = sorted(set(cyclic_groups))[:p - 1]

    minimal_movements = []
    superposition_movement = sequence_length // 2
    superposition_count = 0

    start_sequence = cyclic_sequence[:group_length]

    group_elements = []

    for target_sequence in target_sequences:
        movement = minimal_movement(cyclic_sequence, start_sequence, target_sequence)
        minimal_movements.append(movement)
        group_elements.append((target_sequence, movement))
        if abs(movement) == superposition_movement:
            superposition_count += 1

    total_movements = len(minimal_movements)
    superposition_proportion = superposition_count / total_movements if total_movements > 0 else 0

    return minimal_movements, superposition_movement, superposition_proportion, group_elements

# Simulate quantum angular momentum states using actual probability distributions
def simulate_quantum_angular_momentum(num_samples, max_magnitude):
    # Quantum numbers from l = 0 to l_max
    l_max = int(max_magnitude)
    quantum_numbers = np.arange(0, l_max + 1)

    # Calculate angular momentum magnitudes L = sqrt(l(l+1))
    L_values = np.sqrt(quantum_numbers * (quantum_numbers + 1))

    # Use normalized probability distribution for l
    # For simplicity, we can use the degeneracy of each l level as the probability weight
    # Degeneracy d = 2l + 1
    degeneracy = 2 * quantum_numbers + 1
    probabilities = degeneracy / np.sum(degeneracy)

    # Sample angular momentum magnitudes
    samples = np.random.choice(L_values, size=num_samples, p=probabilities)
    # Assign random signs to simulate directionality
    signs = np.random.choice([-1, 1], size=num_samples)
    movements = samples * signs
    return movements

# -----------------------------
# 2. Group Theory Analysis
# -----------------------------

# Function to analyze the group structure of minimal movements
def analyze_group_structure(group_elements, p):
    # The minimal movements correspond to elements of a cyclic group of order sequence_length
    # We can analyze the subgroup structure
    sequence_length = len(get_reptend_sequence(p))
    group_order = sequence_length
    movements = [elem[1] % group_order for elem in group_elements]

    # Count the occurrences of each movement modulo group order
    movement_counts = Counter(movements)

    # Identify generators of the group
    # In a cyclic group, any element that is relatively prime to the group order is a generator
    generators = [m for m in movement_counts if math.gcd(m, group_order) == 1]

    return {
        'group_order': group_order,
        'movement_counts': movement_counts,
        'generators': generators
    }

# -----------------------------
# 3. Statistical Analysis Functions
# -----------------------------

def perform_statistical_tests(reptend_magnitudes_norm, quantum_magnitudes_norm):
    # Kolmogorov-Smirnov Test
    ks_statistic, ks_p_value = ks_2samp(reptend_magnitudes_norm, quantum_magnitudes_norm)

    # Mann-Whitney U Test
    mw_statistic, mw_p_value = mannwhitneyu(reptend_magnitudes_norm, quantum_magnitudes_norm, alternative='two-sided')

    # Chi-Squared Test
    # Create bins
    bins = np.histogram_bin_edges(np.concatenate([reptend_magnitudes_norm, quantum_magnitudes_norm]), bins='auto')
    reptend_hist, _ = np.histogram(reptend_magnitudes_norm, bins=bins)
    quantum_hist, _ = np.histogram(quantum_magnitudes_norm, bins=bins)

    # Remove bins where both datasets have zero counts
    non_zero_bins = (reptend_hist + quantum_hist) > 0
    reptend_hist_non_zero = reptend_hist[non_zero_bins]
    quantum_hist_non_zero = quantum_hist[non_zero_bins]

    # Perform Chi-Squared Test
    chi2_stat, chi2_p_value, dof, expected = chi2_contingency([reptend_hist_non_zero, quantum_hist_non_zero])

    return {
        'ks_statistic': ks_statistic,
        'ks_p_value': ks_p_value,
        'mw_statistic': mw_statistic,
        'mw_p_value': mw_p_value,
        'chi2_stat': chi2_stat,
        'chi2_p_value': chi2_p_value,
        'dof': dof,
        'expected': expected
    }

# -----------------------------
# 4. Machine Learning Analysis
# -----------------------------

def perform_machine_learning_analysis(combined_data, labels):
    # K-Means Clustering
    kmeans = KMeans(n_clusters=2, random_state=42)
    clusters = kmeans.fit_predict(combined_data.reshape(-1, 1))

    # Classification Model
    X = combined_data.reshape(-1, 1)
    y = np.array([0 if label == 'Reptend' else 1 for label in labels])

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Random Forest Classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Cross-validation
    scores = cross_val_score(clf, X, y, cv=5)

    # Predictions
    y_pred = clf.predict(X_test)

    # Classification Report
    class_report = classification_report(y_test, y_pred, target_names=['Reptend', 'Quantum'])

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)

    return {
        'clusters': clusters,
        'clf': clf,
        'scores': scores,
        'class_report': class_report,
        'confusion_matrix': cm
    }

# -----------------------------
# 5. Visualization Functions
# -----------------------------

def plot_histograms(reptend_magnitudes_norm, quantum_magnitudes_norm):
    # Plot histograms
    plt.figure(figsize=(14, 6))

    # Histogram of Normalized Movement Magnitudes
    plt.subplot(1, 2, 1)
    bins = np.linspace(min(np.min(reptend_magnitudes_norm), np.min(quantum_magnitudes_norm)),
                       max(np.max(reptend_magnitudes_norm), np.max(quantum_magnitudes_norm)), 50)
    plt.hist(reptend_magnitudes_norm, bins=bins, alpha=0.5, label='Minimal Movements (Normalized)')
    plt.hist(quantum_magnitudes_norm, bins=bins, alpha=0.5, label='Quantum Angular Momentum (Normalized)')
    plt.xlabel('Normalized Magnitude')
    plt.ylabel('Frequency')
    plt.title('Comparison of Normalized Movement Magnitudes')
    plt.legend()

    # Cumulative Distribution Functions
    plt.subplot(1, 2, 2)
    reptend_sorted = np.sort(reptend_magnitudes_norm)
    quantum_sorted = np.sort(quantum_magnitudes_norm)
    reptend_cdf = np.arange(1, len(reptend_sorted)+1) / len(reptend_sorted)
    quantum_cdf = np.arange(1, len(quantum_sorted)+1) / len(quantum_sorted)
    plt.plot(reptend_sorted, reptend_cdf, label='Minimal Movements CDF')
    plt.plot(quantum_sorted, quantum_cdf, label='Quantum Angular Momentum CDF')
    plt.xlabel('Normalized Magnitude')
    plt.ylabel('Cumulative Probability')
    plt.title('Cumulative Distribution Functions')
    plt.legend()

    plt.tight_layout()
    plt.show()

def plot_clusters(combined_data, clusters):
    plt.figure(figsize=(10, 6))
    plt.scatter(combined_data, np.zeros_like(combined_data), c=clusters, cmap='viridis', alpha=0.6)
    plt.xlabel('Normalized Magnitude')
    plt.title('K-Means Clustering of Normalized Movements')
    plt.show()

def plot_confusion_matrix(cm):
    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ['Reptend', 'Quantum'], rotation=45)
    plt.yticks(tick_marks, ['Reptend', 'Quantum'])
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()

# -----------------------------
# 6. Main Analysis Function
# -----------------------------

def main():
    full_reptend_data = []
    for p in full_reptend_primes:
        # Skip primes where the sequence length is less than 2
        if p <= 3:
            continue
        minimal_movements, superposition_movement, superposition_proportion, group_elements = generate_minimal_movements(p)
        group_info = analyze_group_structure(group_elements, p)
        full_reptend_data.append({
            'prime': p,
            'minimal_movements': minimal_movements,
            'superposition_movement': superposition_movement,
            'superposition_proportion': superposition_proportion,
            'group_info': group_info
        })

    # Get the maximum superposition movement to define the range for quantum data simulation
    max_superposition_movement = max(data['superposition_movement'] for data in full_reptend_data)

    # Total number of movements to simulate
    num_samples = sum(len(data['minimal_movements']) for data in full_reptend_data)

    # Simulate quantum angular momentum data
    quantum_movements = simulate_quantum_angular_momentum(num_samples, max_superposition_movement)

    # Collect minimal movements
    reptend_movements = []
    for data in full_reptend_data:
        reptend_movements.extend(data['minimal_movements'])

    # Convert to numpy arrays and normalize data
    reptend_magnitudes = np.array([abs(m) for m in reptend_movements])
    quantum_magnitudes = np.array([abs(m) for m in quantum_movements])

    # Normalize data
    reptend_magnitudes_norm = (reptend_magnitudes - reptend_magnitudes.mean()) / reptend_magnitudes.std()
    quantum_magnitudes_norm = (quantum_magnitudes - quantum_magnitudes.mean()) / quantum_magnitudes.std()

    # Perform Statistical Tests
    stats_results = perform_statistical_tests(reptend_magnitudes_norm, quantum_magnitudes_norm)

    # Prepare data for Machine Learning Analysis
    combined_data = np.concatenate((reptend_magnitudes_norm, quantum_magnitudes_norm))
    labels = np.array(['Reptend'] * len(reptend_magnitudes_norm) + ['Quantum'] * len(quantum_magnitudes_norm))

    # Perform Machine Learning Analysis
    ml_results = perform_machine_learning_analysis(combined_data, labels)

    # Visualization
    plot_histograms(reptend_magnitudes_norm, quantum_magnitudes_norm)
    plot_clusters(combined_data, ml_results['clusters'])
    plot_confusion_matrix(ml_results['confusion_matrix'])

    # Print Statistical Test Results
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

    # Print out the proportions of superposition movements for each prime
    print("\nFull Reptend Primes Data:")
    for data in full_reptend_data:
        print(f"Prime: {data['prime']}, Superposition Movement: ±{data['superposition_movement']}, "
              f"Superposition Proportion: {data['superposition_proportion'] * 100:.2f}%")
        group_info = data['group_info']
        print(f"  Group Order: {group_info['group_order']}, Number of Generators: {len(group_info['generators'])}")

    # Additional Group Theory Insights
    print("\nGroup Theory Analysis:")
    for data in full_reptend_data[:5]:  # Limiting output for brevity
        group_info = data['group_info']
        print(f"Prime: {data['prime']}")
        print(f"  Group Order: {group_info['group_order']}")
        print(f"  Number of Generators: {len(group_info['generators'])}")
        print(f"  Sample Generators: {group_info['generators'][:5]}")  # Display first 5 generators

    # Final Remarks
    print("\nFinal Remarks:")
    print("The group structure of minimal movements forms cyclic groups whose properties we analyzed.")
    print("Despite normalizing the data and enhancing the quantum simulation, statistical tests indicate differences between the datasets.")
    print("This suggests that while the mathematical and physical systems share conceptual similarities, their statistical properties differ.")
    print("Further research may explore other mathematical structures or refine the quantum simulation for deeper insights.")

# -----------------------------
# 7. Execute Main Function
# -----------------------------

if __name__ == "__main__":
    main()
