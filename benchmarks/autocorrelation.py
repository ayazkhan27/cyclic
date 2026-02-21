import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from khan_cipher.core import encrypt

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({'font.family': 'serif', 'font.size': 12})

def main():
    os.makedirs('benchmarks/plots', exist_ok=True)
    
    # Generate keystream 256*256 = 65536 bytes
    size = 256 * 256
    master_key = os.urandom(32)
    plaintext = b'\x00' * size
    payload = encrypt(plaintext, master_key)
    keystream = payload[32:-32]
    
    signal = np.array(list(keystream), dtype=float)
    signal -= np.mean(signal)
    
    # 1. Autocorrelation Plot (1D)
    # limit lag to 500 for visualization
    max_lag = 500
    if len(signal) > max_lag:
        lag_signal = signal[:2000] # Use a subset to calculate correlation to avoid O(N^2) explosion
        autocorr = np.correlate(lag_signal, lag_signal, mode='full')
        # Extract the positive lags
        autocorr = autocorr[len(autocorr)//2 : len(autocorr)//2 + max_lag]
        
        plt.figure(figsize=(10, 5))
        plt.plot(range(max_lag), autocorr, color='green')
        plt.xlabel('Lag')
        plt.ylabel('Correlation')
        plt.title('KHAN PRNG 1D Autocorrelation')
        plt.tight_layout()
        plt.savefig('benchmarks/plots/autocorrelation_1d.png', dpi=300)
        plt.close()

    # 2. 2D Heatmap (Spatial layout of bytes 256x256)
    matrix = np.array(list(keystream)).reshape((256, 256))
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, cmap='viridis', cbar=True, xticklabels=False, yticklabels=False)
    plt.title('2D Heatmap of KHAN PRNG Keystream (64KB)')
    plt.tight_layout()
    plt.savefig('benchmarks/plots/autocorrelation_heatmap.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    main()
