import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from khan_cipher.core import KhanKeystream, derive_key

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({'font.family': 'serif', 'font.size': 12})


def main():
    os.makedirs('benchmarks/plots', exist_ok=True)

    # Generate keystream 256*256 = 65536 bytes directly
    size = 256 * 256
    master_key = os.urandom(32)
    salt = os.urandom(16)
    iv = os.urandom(16)
    derived_key = derive_key(master_key, salt)
    ksg = KhanKeystream(derived_key, 100003, iv)
    keystream = bytes([ksg.get_next_byte() for _ in range(size)])

    signal = np.array(list(keystream), dtype=float)
    signal -= np.mean(signal)

    # 1. Autocorrelation Plot (1D)
    # limit lag to 500 for visualization
    max_lag = 500
    if len(signal) > max_lag:
        # Use a subset to calculate correlation to avoid O(N^2) explosion
        lag_signal = signal[:2000]
        autocorr = np.correlate(lag_signal, lag_signal, mode='full')
        # Extract the positive lags
        autocorr = autocorr[len(autocorr) // 2: len(autocorr) // 2 + max_lag]

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
    sns.heatmap(matrix, cmap='viridis', cbar=True,
                xticklabels=False, yticklabels=False)
    plt.title('2D Heatmap of KHAN PRNG Keystream (64KB)')
    plt.tight_layout()
    plt.savefig('benchmarks/plots/autocorrelation_heatmap.png', dpi=300)
    plt.close()


if __name__ == "__main__":
    main()
