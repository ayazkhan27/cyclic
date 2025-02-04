import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.fft import fft
from sympy import divisors
from scipy.stats import entropy
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

#####################################################
# Function: minimal_movement
#####################################################
# This function computes the minimal cyclic rotation needed to transform
# a starting cyclic group (derived from the repeating decimal for 1/p)
# into a target cyclic group (which represents the repeating decimal for n/p).
#
# For example, for p=7:
#   - The repeating decimal for 1/7 is "142857".
#   - To obtain 2/7, the correct cyclic shift should yield "285714".
#     Here, one can either shift 4 positions left (resulting in -4) or
#     2 positions right (resulting in +2). Since |2| < |4|, the minimal rotation is +2.
#
# The function uses the provided positions (from digit_positions) of the starting
# sequence and the target sequence on the circular dial (the repeating cycle)
# to calculate both the clockwise and anticlockwise shifts and returns the one
# with the smallest absolute value.
def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence):
    # Retrieve all positions (indices) in the cycle where the start and target sequences occur.
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]

    min_movement = sequence_length  # Initialize with a large value (larger than any possible rotation)

    # Iterate over all occurrences of the start and target sequences.
    for start_pos in start_positions:
        for target_pos in target_positions:
            # Compute the clockwise movement: how many steps from start to target modulo the cycle length.
            clockwise_movement = (target_pos - start_pos) % sequence_length
            # Compute the anticlockwise movement: how many steps in the reverse direction.
            anticlockwise_movement = (start_pos - target_pos) % sequence_length
            
            # Determine which direction gives the minimal absolute movement.
            if clockwise_movement <= anticlockwise_movement:
                movement = clockwise_movement  # Positive indicates clockwise rotation.
            else:
                movement = -anticlockwise_movement  # Negative indicates anticlockwise rotation.

            # Keep track of the movement with the smallest absolute value.
            if abs(movement) < abs(min_movement):
                min_movement = movement

    return min_movement

#####################################################
# Function: generate_target_sequences
#####################################################
# This function extracts the cyclic groups (or segments) from the full repeating
# decimal (the cyclic sequence) for a prime p. These cyclic groups represent
# all possible cyclic permutations, each corresponding mathematically to the 
# repeating sequence for a different fraction n/p (where 1 ≤ n < p).
#
# For example, for p=7 with cycle "142857", the possible target sequences include:
# "142857", "428571", "285714", etc. These are used to calculate the minimal rotation
# required to transition from the sequence for 1/7 to that for 2/7, 3/7, etc.
def generate_target_sequences(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    group_length = len(str(prime))  # Number of digits to group together (typically equal to len(str(p)))
    
    if prime < 10:
        # For single-digit primes, simply return the unique digits.
        return sorted(set(cyclic_sequence))
    else:
        cyclic_groups = []
        # Slide over the cycle to extract groups of length equal to the number of digits in prime.
        for i in range(sequence_length):
            group = cyclic_sequence[i:i+group_length]
            if len(group) == group_length:
                cyclic_groups.append(group)
            else:
                # Handle wrap-around: if the end of the string is reached, append the beginning.
                wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length - len(group)]
                cyclic_groups.append(wrap_around_group)
        
        # Remove duplicates by converting to a set, then sort them.
        cyclic_groups = sorted(set(cyclic_groups))
        # Return the first p-1 elements (which correspond to the fractions 1/p to (p-1)/p)
        return cyclic_groups[:prime - 1]

#####################################################
# Function: analyze_cyclic_movements
#####################################################
# This function integrates the above ideas:
# - It maps the cyclic sequence (the repeating decimal for 1/p) onto a circular dial.
# - It then generates the target sequences corresponding to each fraction n/p.
# - For each target, it calculates the minimal rotation needed to transform the starting
#   sequence into the target sequence using the minimal_movement function.
# - It also computes an FFT on the resulting movement array and basic statistics.
#
# The output is a dictionary containing the FFT result and statistical measures,
# which will later be used to extract features for machine learning analysis.
def analyze_cyclic_movements(prime, cyclic_sequence):
    sequence_length = len(cyclic_sequence)
    digit_positions = {}  # To store indices for each group
    group_length = len(str(prime))
    
    # Populate digit_positions: map each cyclic group to the indices where it occurs.
    for i in range(sequence_length):
        group = cyclic_sequence[i:i+group_length]
        if len(group) == group_length:
            if group in digit_positions:
                digit_positions[group].append(i)
            else:
                digit_positions[group] = [i]
        else:
            wrap_around_group = cyclic_sequence[i:] + cyclic_sequence[:group_length - len(group)]
            if wrap_around_group in digit_positions:
                digit_positions[wrap_around_group].append(i)
            else:
                digit_positions[wrap_around_group] = [i]
    
    # Generate all target sequences, each representing the cyclic shift for a fraction n/p.
    target_sequences = generate_target_sequences(prime, cyclic_sequence)
    movements = []
    
    # Use the first group (derived from 1/p) as the start sequence.
    start_sequence = cyclic_sequence[:len(target_sequences[0])]
    
    # For each target sequence (which mathematically represents the repeating decimal for n/p),
    # compute the minimal rotation (shift) required to transform the start sequence into the target.
    for target_sequence in target_sequences:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence)
        movements.append(movement)

    movements = np.array(movements)
    
    # Compute the Fast Fourier Transform (FFT) of the movement sequence to analyze its frequency content.
    fft_result = fft(movements)
    
    # Calculate basic statistics from the movement sequence.
    mean = np.mean(movements)
    std_dev = np.std(movements)
    max_movement = np.max(np.abs(movements))
    
    # Also compute autocorrelations at potential periods (divisors of p-1).
    potential_periods = divisors(prime - 1)[1:]  # Skip the trivial divisor 1.
    autocorrelations = [np.correlate(movements, np.roll(movements, shift))[0] for shift in potential_periods]
    
    # Return all these computed values in a dictionary.
    return {
        'fft': fft_result,
        'mean': mean,
        'std_dev': std_dev,
        'max_movement': max_movement,
        'autocorrelations': dict(zip(potential_periods, autocorrelations)),
        'movement_distribution': None  # Not used in feature vector
    }

#####################################################
# Helper function: calculate_lyapunov_exponent
#####################################################
# This function calculates the Lyapunov exponent from the movement data.
# The Lyapunov exponent is a measure of the sensitivity to initial conditions,
# computed as the average of the logarithm of the absolute differences between successive movements.
def calculate_lyapunov_exponent(movements):
    movements = np.array(movements)
    diffs = np.abs(np.diff(movements))
    with np.errstate(divide='ignore'):
        lyapunov = np.mean(np.log(diffs[diffs > 0]))
    return lyapunov if not math.isnan(lyapunov) else 0

#####################################################
# Helper function: fractal_dimension_box_counting
#####################################################
# This function estimates the fractal dimension of the movement sequence using
# the box-counting method. It counts, for various scales, the number of segments
# where the data has nonzero variance. The slope of the line in the log-log plot
# of scale versus count gives an estimate of the fractal dimension.
def fractal_dimension_box_counting(data, scales):
    counts = []
    for scale in scales:
        count = 0
        for i in range(0, len(data), scale):
            if i + scale < len(data):
                if np.std(data[i:i+scale]) > 0:
                    count += 1
        counts.append(count)
    return counts

#####################################################
# Helper function: get_cyclic_sequence
#####################################################
# This function computes the repeating decimal (cyclic sequence) of 1/p for a full reptend prime.
# It uses long division to generate the cycle, ensuring the result is exactly p-1 digits.
def get_cyclic_sequence(prime):
    remainder = 1
    seen = {}
    sequence = ""
    # Perform long division until a remainder repeats, which indicates the cycle is complete.
    while remainder and remainder not in seen:
        seen[remainder] = len(sequence)
        remainder *= 10
        sequence += str(remainder // prime)
        remainder %= prime
    if remainder:
        start = seen[remainder]
        sequence = sequence[start:]
    # Pad with leading zeros if necessary.
    return sequence.zfill(prime - 1)

#####################################################
# Function: prepare_data
#####################################################
# This function extracts feature vectors from each full reptend prime.
# For each prime, using its cyclic sequence, it calls analyze_cyclic_movements
# to get the movement data, computes spectral features via FFT,
# and then calculates:
# - Standard deviation of the movements
# - Maximum movement (often the special superposition shift)
# - Lyapunov exponent (sensitivity measure)
# - Fractal dimension (complexity measure)
# - Dominant frequency (from the FFT)
# - Spectral entropy (disorder in the frequency spectrum)
#
# These six features form the feature vector used for clustering.
def prepare_data(primes_and_sequences):
    features = []
    labels = []
    scales = range(1, 11)  # Scales for fractal dimension calculation
    
    for prime, sequence in primes_and_sequences:
        # Analyze the cyclic movements for the prime.
        results = analyze_cyclic_movements(prime, sequence)
        
        # For spectral analysis, we work with the real part of the FFT of the movement array.
        fft_result = results['fft']
        movements = fft_result.real
        
        # Basic movement features (from the non-FFT domain)
        std_dev_movement = results['std_dev']
        max_movement = results['max_movement']
        
        # Reconstruct the original minimal movement array by taking the inverse FFT.
        original_movements = np.real(np.fft.ifft(fft_result))
        lyapunov_exponent = calculate_lyapunov_exponent(original_movements)
        
        # Compute the fractal dimension using box-counting on the original movements.
        fractal_counts = fractal_dimension_box_counting(original_movements, scales)
        valid = [(s, c) for s, c in zip(scales, fractal_counts) if c > 0]
        if len(valid) < 2:
            fractal_dimension = 0.0
        else:
            scales_filtered, counts_filtered = zip(*valid)
            fractal_dimension = -np.polyfit(np.log(scales_filtered), np.log(counts_filtered), 1)[0]
        
        # Compute spectral features:
        N = len(fft_result)
        freqs = np.fft.fftfreq(N)
        magnitudes = np.abs(fft_result)
        # Dominant Frequency: Find the frequency (excluding zero) with maximum magnitude.
        nonzero = np.where(freqs != 0)[0]
        if len(nonzero) > 0:
            idx = nonzero[np.argmax(magnitudes[nonzero])]
            dominant_frequency = np.abs(freqs[idx])
        else:
            dominant_frequency = 0
        
        # Spectral Entropy: Compute the power spectrum, normalize it, and then calculate its entropy.
        power_spectrum = magnitudes**2
        total_power = np.sum(power_spectrum)
        if total_power > 0:
            ps_norm = power_spectrum / total_power
            spectral_entropy = entropy(ps_norm)
        else:
            spectral_entropy = 0
        
        # Construct the feature vector.
        # Note: We omit the mean movement because it tends to be nearly constant.
        feature_vector = [
            std_dev_movement,    # Variability in the movements
            max_movement,        # The extreme (superposition) movement value
            lyapunov_exponent,   # Chaotic sensitivity measure
            fractal_dimension,   # Complexity of the cyclic pattern
            dominant_frequency,  # Strongest periodic component from FFT
            spectral_entropy     # Disorder of the spectral distribution
        ]
        features.append(feature_vector)
        labels.append(prime)
    
    return np.array(features), np.array(labels)

#####################################################
# Function: explain_clusters
#####################################################
# This helper function prints out detailed information about each cluster.
# For each cluster, it lists:
#   - The count of primes,
#   - The specific primes in the cluster,
#   - The mean and standard deviation of the feature vectors within the cluster.
# It also provides an extra note for clusters that appear outlying.
def explain_clusters(labels, clusters, features):
    unique_clusters = np.unique(clusters)
    for cluster in unique_clusters:
        indices = np.where(clusters == cluster)[0]
        cluster_primes = labels[indices]
        cluster_features = features[indices]
        print(f"\nCluster {cluster}:")
        print(f"  Count: {len(cluster_primes)}")
        print(f"  Primes: {cluster_primes}")
        print(f"  Mean Feature Vector: {np.mean(cluster_features, axis=0)}")
        print(f"  Std Feature Vector: {np.std(cluster_features, axis=0)}")
        if cluster == 2:
            print("  *** This cluster appears to be outlying, with primes having extreme spectral or chaotic features. ***")
    print()

#####################################################
# Function: perform_unsupervised_analysis
#####################################################
# This function performs the unsupervised machine learning analysis:
#   1. Standardizes the feature vectors.
#   2. Reduces the dimensionality to 2 components using PCA (for visualization).
#   3. Clusters the data using KMeans (3 clusters in this example).
#   4. Calculates and prints the silhouette score.
#   5. Plots the 2D PCA representation colored by cluster.
#   6. Calls explain_clusters to automatically list out the cluster contents and statistics.
def perform_unsupervised_analysis(features, labels):
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Reduce dimensionality with PCA.
    pca = PCA(n_components=2)
    features_pca = pca.fit_transform(features_scaled)
    
    # Apply KMeans clustering.
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(features_pca)
    
    silhouette_avg = silhouette_score(features_pca, clusters)
    print("Silhouette Score:", silhouette_avg)
    
    # Plot the PCA-reduced clustering result.
    plt.figure(figsize=(10, 6))
    plt.scatter(features_pca[:, 0], features_pca[:, 1], c=clusters, cmap='viridis', alpha=0.7)
    plt.colorbar(label='Cluster')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.title('KMeans Clustering of Cyclic Prime Features')
    plt.show()
    
    # Automatically explain the clusters by listing their elements and basic statistics.
    explain_clusters(labels, clusters, features)

#####################################################
# Main Code: Generate and Analyze Full Reptend Primes
#####################################################
# Define a (potentially large) list of full reptend primes.
# This list can include primes beyond 983. Here, a sample expanded list is provided.
full_reptend_primes = [
    7, 17, 19, 23, 29, 47, 59, 61, 97, 109, 113, 131, 149, 167,
    179, 181, 193, 223, 229, 233, 257, 263, 269, 313, 337, 367,
    379, 383, 389, 419, 433, 461, 487, 491, 499, 503, 509, 541,
    571, 577, 593, 619, 647, 659, 701, 709, 727, 743, 811, 821,
    823, 857, 863, 887, 937, 941, 953, 971, 977, 983, 1019, 1021,
    1033, 1051, 1063, 1069, 1087, 1091, 1097, 1103, 1109, 1153,
    1171, 1181, 1193, 1217, 1223, 1229, 1259, 1291, 1297, 1301,
    1303, 1327, 1367, 1381, 1429, 1433, 1447, 1487, 1531, 1543,
    1549, 1553, 1567, 1571, 1579, 1583, 1607, 1619, 1621, 1663,
    1697, 1709, 1741, 1777, 1783, 1789, 1811, 1823, 1847, 1861,
    1873, 1913, 1949, 1979, 2017, 2029, 2063, 2069, 2099, 2113,
    2137, 2141, 2143, 2153, 2179, 2207, 2221, 2251, 2269, 2273,
    2297, 2309, 2339, 2341, 2371, 2383, 2389, 2411, 2417, 2423,
    2447, 2459, 2473, 2539, 2543, 2549, 2579, 2593, 2617, 2621,
    2633, 2657, 2663, 2687, 2699, 2713, 2731, 2741, 2753, 2767,
    2777, 2789, 2819, 2833, 2851, 2861, 2887, 2897, 2903, 2909,
    2927, 2939, 2971, 3011, 3019, 3023, 3137, 3167, 3221, 3251,
    3257, 3259, 3299, 3301, 3313, 3331, 3343, 3371, 3389, 3407,
    3433, 3461, 3463, 3469, 3527, 3539, 3571, 3581, 3593, 3607,
    3617, 3623, 3659, 3673, 3701, 3709, 3727, 3767, 3779, 3821,
    3833, 3847, 3863, 3943, 3967, 3989, 4007, 4019, 4051, 4057,
    4073, 4091, 4099, 4127, 4139, 4153, 4177, 4211, 4217, 4219,
    4229, 4259, 4261, 4327, 4337, 4339, 4349, 4421, 4423, 4447,
    4451, 4457, 4463, 4567, 4583, 4651, 4673, 4691, 4703, 4783,
    4793, 4817, 4931, 4937, 4943, 4967, 5021, 5059, 5087, 5099,
    5153, 5167, 5179, 5189, 5233, 5273, 5297, 5303, 5309, 5381,
    5393, 5417, 5419, 5501, 5503, 5527, 5531, 5581, 5623, 5651,
    5657, 5659, 5669, 5701, 5737, 5741, 5743, 5749, 5779, 5783,
    5807, 5821, 5857, 5861, 5869, 5897, 5903, 5927, 5939, 5981,
    6011, 6029, 6047, 6073, 6113, 6131, 6143, 6211, 6217, 6221,
    6247, 6257, 6263, 6269, 6287, 6301, 6337, 6343, 6353, 6367,
    6389, 6473, 6553, 6571, 6619, 6659, 6661, 6673, 6691, 6701,
    6703, 6709, 6737, 6779, 6793, 6823, 6829, 6833, 6857, 6863,
    6869, 6899, 6949, 6967, 6971, 6977, 6983, 7019, 7057, 7069,
    7103, 7109, 7177, 7193, 7207, 7219, 7229, 7247, 7309, 7349,
    7393, 7411, 7433, 7451, 7457, 7459, 7487, 7499, 7541, 7577,
    7583, 7607, 7673, 7687, 7691, 7699, 7703, 7727, 7753, 7793,
    7817, 7823, 7829, 7873, 7901, 7927, 7937, 7949, 8017, 8059,
    8069, 8087, 8171, 8179, 8219, 8233, 8263, 8269, 8273, 8287,
    8291, 8297, 8353, 8377, 8389, 8423, 8429, 8447, 8501, 8513,
    8537, 8543, 8623, 8647, 8663, 8669, 8699, 8713, 8731, 8741,
    8753, 8783, 8807, 8819, 8821, 8861, 8863, 8887, 8971, 9011,
    9029, 9059, 9103, 9109, 9137, 9221, 9257, 9341, 9343, 9371,
    9377, 9421, 9461, 9473, 9491, 9497, 9539, 9623, 9629, 9697,
    9739, 9743, 9749, 9767, 9781, 9811, 9817, 9829, 9833, 9851,
    9857, 9887, 9931, 9949, 9967
]

# Generate (prime, cyclic_sequence) pairs using our helper function.
# For each prime, get the cyclic sequence of 1/p (which is the repeating decimal of 1/p).
primes_and_sequences = [(p, get_cyclic_sequence(p)) for p in full_reptend_primes]

# (Optional) Uncomment the following lines to print out the cyclic sequence for each prime.
# for prime, seq in primes_and_sequences:
#     print(f"Prime {prime} → Cyclic Sequence: {seq}")

# Prepare feature data from the cyclic prime analysis.
features, labels = prepare_data(primes_and_sequences)

# Run unsupervised analysis: Perform PCA, KMeans clustering, plot the result,
# and automatically explain the clusters (listing the primes in each cluster along with statistics).
perform_unsupervised_analysis(features, labels)
