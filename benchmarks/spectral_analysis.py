import os
import numpy as np
import scipy.fft
import matplotlib.pyplot as plt
from khan_cipher.core import encrypt

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({'font.family': 'serif', 'font.size': 12})


def main():
    os.makedirs('benchmarks/plots', exist_ok=True)

    # Generate 10,000 bytes of keystream
    master_key = os.urandom(32)
    plaintext = b'\x00' * 10000
    payload = encrypt(plaintext, master_key)
    keystream = payload[32:-32]

    # Convert bytes to numpy array
    signal = np.array(list(keystream), dtype=float)

    # Remove DC component (mean)
    signal -= np.mean(signal)

    # Calculate FFT
    fft_result = scipy.fft.fft(signal)
    fft_magnitude = np.abs(fft_result)

    # Plot only positive frequencies
    n = len(signal)
    freqs = scipy.fft.fftfreq(n)

    pos_mask = freqs > 0
    freqs = freqs[pos_mask]
    magnitude = fft_magnitude[pos_mask]

    plt.figure(figsize=(12, 6))
    plt.plot(freqs, magnitude, color='purple', alpha=0.8)
    plt.axhline(y=np.mean(magnitude), color='r',
                linestyle='--', label='Mean Magnitude')
    plt.xlabel('Frequency')
    plt.ylabel('Magnitude')
    plt.title('FFT Spectrum of KHAN PRNG Keystream (10KB)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('benchmarks/plots/fft_spectrum.png', dpi=300)
    plt.close()


if __name__ == "__main__":
    main()
