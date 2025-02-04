import kagglehub
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, r2_score
from scipy.stats import linregress, t
import warnings

warnings.filterwarnings('ignore')

# Download the CERN dataset
path = kagglehub.dataset_download("fedesoriano/cern-electron-collision-data")
cern_data_path = f"{path}/dielectron.csv"

# Load the dataset
data = pd.read_csv(cern_data_path)

# Extracting the relevant features
cern_features = data[['E1', 'E2', 'pt1', 'pt2', 'eta1', 'eta2', 'phi1', 'phi2', 'M']]

# Normalizing the data
scaler = StandardScaler()
cern_features_normalized = scaler.fit_transform(cern_features)

# Function to compute minimal movement for cyclic prime
def minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, cyclic_sequence):
    start_positions = digit_positions[start_sequence]
    target_positions = digit_positions[target_sequence]
    min_movement = sequence_length  # Initialize with a value larger than any possible movement
    for start_pos in start_positions:
        for target_pos in target_positions:
            # Calculate clockwise and anticlockwise movements
            clockwise_movement = (target_pos - start_pos) % sequence_length
            anticlockwise_movement = (start_pos - target_pos) % sequence_length
            # Find the minimal movement
            movement = clockwise_movement if clockwise_movement <= anticlockwise_movement else -anticlockwise_movement
            if abs(movement) < abs(min_movement):
                min_movement = movement
    return min_movement

# Generating minimal movement data for a larger range of cyclic primes
cyclic_primes = [7, 17, 19, 23, 29, 47, 59, 61, 97, 109, 113, 131, 149, 167, 173, 179, 181, 191, 193, 223, 229, 233, 239, 251, 257, 263, 269, 283, 307, 311, 313, 331, 347, 349, 353, 359, 367, 373, 379, 389, 397, 401, 409, 419, 431, 439, 443, 449, 461, 463, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 577, 587, 593, 601, 607, 613, 617, 619, 631, 641, 643, 647, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 761, 769, 773, 787, 797, 809, 811, 821, 829, 839]
cyclic_sequences = [str(1 / p)[2:] for p in cyclic_primes[:100]]  # Approximation to generate sequences for the first 100 primes

minimal_movements = []
for prime, sequence in zip(cyclic_primes[:100], cyclic_sequences):
    sequence_length = len(sequence)
    digit_positions = {digit: [idx for idx, d in enumerate(sequence) if d == digit] for digit in set(sequence)}
    start_sequence = sequence[0]
    for target_sequence in sequence[1:]:
        movement = minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length, sequence)
        minimal_movements.append(movement)

# Adjusting the size of CERN data to match minimal movements size
cern_features_normalized = cern_features_normalized[:1707]

# Converting minimal movements to a DataFrame
minimal_movements_df = pd.DataFrame(minimal_movements, columns=['MinimalMovement'])
minimal_movements_normalized = scaler.fit_transform(minimal_movements_df)

# Combining both datasets for comparison
combined_data = np.concatenate((cern_features_normalized, minimal_movements_normalized), axis=1)

# PCA for Dimensionality Reduction
pca = PCA(n_components=2)
combined_data_pca = pca.fit_transform(combined_data)

# Clustering Analysis with KMeans
kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(combined_data_pca)
silhouette_avg = silhouette_score(combined_data_pca, labels)

# Plotting PCA and Clusters
plt.figure(figsize=(10, 6))
plt.scatter(combined_data_pca[:, 0], combined_data_pca[:, 1], c=labels, cmap='viridis', alpha=0.6)
plt.title('PCA of Combined CERN and Cyclic Prime Data')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.colorbar(label='Cluster Label')
plt.show()

# Linear Regression Analysis to Check Correlation
cern_energy_sum = cern_features[['E1', 'E2']].sum(axis=1)
regression = linregress(cern_energy_sum[:len(minimal_movements)], minimal_movements[:len(cern_energy_sum)])

# Statistical Evaluation
p_value = regression.pvalue
r_squared = regression.rvalue ** 2
confidence_interval = 0.95
n = len(minimal_movements)
t_critical = t.ppf((1 + confidence_interval) / 2, df=n-2)
margin_of_error = t_critical * regression.stderr
lower_bound = regression.slope - margin_of_error
upper_bound = regression.slope + margin_of_error

# Summary of Results
print("\nSummary of Comparison Between CERN Data and Minimal Movement of Cyclic Primes")
print("Silhouette Score (Clustering Quality):", silhouette_avg)
print("R-squared Value (Correlation Strength):", r_squared)
print("P-value (Significance of Correlation):", p_value)
print(f"Confidence Interval for Slope (95%): [{lower_bound}, {upper_bound}]")

# Conclusion based on statistical results
if p_value < 0.05:
    print("\nConclusion: There is a statistically significant correlation between the minimal movement of cyclic primes and CERN electron data.")
    if r_squared > 0.5:
        print("The R-squared value suggests a moderate to strong correlation, indicating potential similarities between the phenomena.")
    else:
        print("However, the R-squared value is low, indicating that the correlation may not fully explain the relationship between these phenomena.")
else:
    print("\nConclusion: There is no statistically significant correlation between the minimal movement of cyclic primes and CERN electron data.")
