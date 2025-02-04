import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.stats import entropy
from sklearn.feature_selection import mutual_info_regression

# Import functions from provided files
from cyclicprimerelations import minimal_movement, generate_target_sequences
from FFTStandardDevTest import analyze_cyclic_movements

def prepare_data(primes_and_sequences):
    features = []
    
    for prime, sequence in primes_and_sequences:
        # Get movement data from existing analysis function
        results = analyze_cyclic_movements(prime, sequence)
        movements = results['fft']
        mean_movement = results['mean']
        std_dev_movement = results['std_dev']
        max_movement = results['max_movement']
        
        # Features to include
        feature_vector = [
            mean_movement,
            std_dev_movement,
            max_movement,
            entropy(np.histogram(movements.real, bins='auto')[0]),
            mutual_info_regression(np.array(movements.real[:-1]).reshape(-1, 1), movements.real[1:])[0]
        ]
        features.append(feature_vector)
    
    features = np.array(features)
    return features

def perform_unsupervised_ml(features):
    # Standardize the data
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Apply PCA for dimensionality reduction
    pca = PCA(n_components=2)
    features_pca = pca.fit_transform(features_scaled)
    
    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(features_pca)
    
    # Evaluate clustering using silhouette score
    silhouette_avg = silhouette_score(features_pca, clusters)
    print("Silhouette Score:", silhouette_avg)
    
    # Plot the clustering results
    plt.figure(figsize=(10, 6))
    plt.scatter(features_pca[:, 0], features_pca[:, 1], c=clusters, cmap='viridis', s=50, alpha=0.7)
    plt.title("KMeans Clustering of Cyclic Prime Features")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.colorbar(label='Cluster')
    plt.show()

def analyze_new_properties(primes_and_sequences):
    features = prepare_data(primes_and_sequences)
    perform_unsupervised_ml(features)

# Example usage with a larger range of full reptend primes
primes_and_sequences = [
    (7, '142857'),
    (17, '0588235294117647'),
    (19, '052631578947368421'),
    (23, '0434782608695652173913'),
    (29, '0344827586206896551724137931'),
    (47, '0212765957446808510638297872340425531914893617'),
    (59, '0169491525423728813559322033898305084745762711864406779661'),
    (61, '016393442622950819672131147540983606557377049180327868852459'),
    (97, '010309278350515463917525773195876288659793814432989690721649484536082474226804123711340206185567')
]

analyze_new_properties(primes_and_sequences)
