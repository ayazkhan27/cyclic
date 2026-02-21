"""
NIST SP 800-22 Statistical Test Parser / Inline Validator.

When a real NIST STS finalAnalysisReport.txt is present, this script
parses it and reports p-values.  Otherwise, it runs a compact subset of
statistical tests (frequency, runs, chi-squared byte uniformity) on a
freshly generated 1 MB keystream sample as a lightweight CI substitute.
"""

import os
import math
from collections import Counter

import pandas as pd
from khan_cipher.core import KhanKeystream, derive_key


# ------------------------------------------------------------------ #
#  Lightweight inline statistical tests                              #
# ------------------------------------------------------------------ #

def _monobit_frequency_test(data: bytes) -> float:
    """NIST SP 800-22 Test 1: Frequency (Monobit).

    Converts bytes to bits, counts +1/-1 balance, returns p-value via erfc.
    """
    n = len(data) * 8
    s = 0
    for byte in data:
        for bit in range(8):
            s += 1 if (byte >> bit) & 1 else -1
    s_obs = abs(s) / math.sqrt(n)
    return math.erfc(s_obs / math.sqrt(2))


def _runs_test(data: bytes) -> float:
    """NIST SP 800-22 Test 2: Runs.

    Counts the number of uninterrupted bit-runs, returns p-value.
    """
    bits = []
    for byte in data:
        for bit in range(8):
            bits.append((byte >> bit) & 1)
    n = len(bits)
    ones = sum(bits)
    pi = ones / n

    if abs(pi - 0.5) >= (2.0 / math.sqrt(n)):
        return 0.0  # prerequisite fails

    v_obs = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            v_obs += 1

    p_value = math.erfc(
        abs(v_obs - 2 * n * pi * (1 - pi))
        / (2 * math.sqrt(2 * n) * pi * (1 - pi))
    )
    return p_value


def _chi_squared_byte_uniformity(data: bytes) -> float:
    """Chi-squared test for uniform byte distribution.

    Each of 256 possible byte values should appear with equal probability.
    Returns p-value via the regularized incomplete gamma function.
    """
    counts = Counter(data)
    n = len(data)
    expected = n / 256.0
    chi2 = sum((counts.get(i, 0) - expected) ** 2 / expected for i in range(256))

    # Approximate p-value via scipy if available, else use a rough bound
    try:
        from scipy.stats import chi2 as chi2_dist
        p_value = 1.0 - chi2_dist.cdf(chi2, df=255)
    except ImportError:
        # Rough normal approximation for large df
        z = (chi2 - 255) / math.sqrt(2 * 255)
        p_value = math.erfc(z / math.sqrt(2)) / 2
    return p_value


# ------------------------------------------------------------------ #
#  Main                                                               #
# ------------------------------------------------------------------ #

def main():
    report_path = 'benchmarks/data/finalAnalysisReport.txt'

    print("Parsing NIST SP 800-22 Results...")

    if os.path.exists(report_path):
        # ---- Parse real NIST STS output ----
        tests, p_values = [], []
        with open(report_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            if (line.startswith("-") or line.startswith(" ")
                    or "P-VALUE" in line or not line.strip()):
                continue
            parts = line.split()
            if len(parts) >= 12:
                try:
                    p_val = float(parts[-2])
                    test_name = parts[-1]
                    tests.append(test_name)
                    p_values.append(p_val)
                except ValueError:
                    continue

        if not tests:
            print("[-] Failed to parse any tests from the report.")
            return

        df = pd.DataFrame(
            {'NIST Test Suite': tests, 'P-Value': p_values}
        )
        print("\nKHAN Cipher NIST SP 800-22 Test Results:")
        print(df.to_markdown(index=False))

        assert all(
            p >= 0.01 for p in p_values
        ), "NIST SP 800-22 Test Failed: Strict Bias Detected."
        print("\n[+] Success: All statistical p-values >= 0.01 bounded.")

    else:
        # ---- Inline lightweight statistical tests on 1 MB sample ----
        print("[i] No external NIST report found. Running inline tests on 1 MB keystream...\n")

        sample_size = 1024 * 1024  # 1 MB
        key = os.urandom(32)
        salt = os.urandom(16)
        iv = os.urandom(16)
        derived_key = derive_key(key, salt)
        ksg = KhanKeystream(derived_key, 100003, iv)
        data = bytes([ksg.get_next_byte() for _ in range(sample_size)])

        tests = [
            ("Frequency (Monobit)", _monobit_frequency_test(data)),
            ("Runs", _runs_test(data)),
            ("Chi-Squared Byte Uniformity", _chi_squared_byte_uniformity(data)),
        ]

        df = pd.DataFrame(tests, columns=["Test", "P-Value"])
        print("KHAN Cipher Inline Statistical Validation (1 MB sample):")
        print(df.to_string(index=False))

        failed = [t for t, p in tests if p < 0.01]
        if failed:
            print(f"\n[-] FAILED tests: {failed}")
            raise SystemExit(1)
        else:
            print("\n[+] All inline statistical tests passed (p >= 0.01).")


if __name__ == "__main__":
    main()
