"""
NIST SP 800-22 Rev. 1a Statistical Test Suite — Full Battery.

Runs all eligible tests from the NIST SP 800-22 battery on a 1,000,000-bit
keystream sample using the ``nistrng`` reference implementation.  Results are
saved to benchmarks/data/finalAnalysisReport.txt.

The ``linear_complexity`` test is skipped by default because it is O(n^2) and
takes 20+ minutes for 1M bits.  All other 13+ eligible tests run in ~60s.
"""

import os
import sys
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'src'))

from khan_cipher.core import KhanKeystream, derive_key  # noqa: E402
from khan_cipher.primes import DEFAULT_PRIME  # noqa: E402
import nistrng  # noqa: E402


STREAM_LENGTH_BITS = 1_000_000
REPORT_PATH = 'benchmarks/data/finalAnalysisReport.txt'

# linear_complexity is O(n^2) — impractical for CI at 1M bits
SKIP_TESTS = {"linear_complexity"}


def _generate_keystream_bits(n_bits: int) -> np.ndarray:
    """Generate n_bits of KHAN keystream as a numpy int8 0/1 array."""
    n_bytes = (n_bits + 7) // 8
    key = os.urandom(32)
    salt = os.urandom(16)
    iv = os.urandom(16)
    derived_key = derive_key(key, salt)
    ksg = KhanKeystream(derived_key, DEFAULT_PRIME, iv)
    raw = bytes([ksg.get_next_byte() for _ in range(n_bytes)])
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8))
    return bits[:n_bits].astype(np.int8)


def _run_nist_battery(bits: np.ndarray) -> pd.DataFrame:
    """Run NIST SP 800-22 tests one-by-one and collect results."""
    eligible = nistrng.check_eligibility_all_battery(
        bits, nistrng.SP800_22R1A_BATTERY
    )
    # Filter
    run_tests = [t for t in eligible if t not in SKIP_TESTS]
    skip_count = len(eligible) - len(run_tests)

    print(f"  Eligible : {len(eligible)} / 15")
    print(f"  Running  : {len(run_tests)} "
          f"(skipping {skip_count}: {SKIP_TESTS & set(eligible)})")
    print(f"  Bits     : {len(bits):,}\n")

    rows = []
    t0 = time.time()
    for name in run_tests:
        t_test = time.time()
        result = nistrng.run_by_name_battery(
            name, bits, nistrng.SP800_22R1A_BATTERY, False
        )
        dt = time.time() - t_test

        if result is None:
            continue

        # Result may be a nistrng.Result object or a tuple
        if isinstance(result, nistrng.Result):
            score = result.score
            passed = result.passed
        elif isinstance(result, tuple):
            # (Result, elapsed) tuple wrapping
            inner = result[0] if len(result) >= 1 else result
            if isinstance(inner, nistrng.Result):
                score = inner.score
                passed = inner.passed
            else:
                score = float(result[-1]) if result else 0.0
                passed = score >= 0.01
        else:
            continue

        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name:40s}  "
              f"p={score:.6f}  ({dt:.1f}s)")
        rows.append({
            "Test": name,
            "P-Value": round(float(score), 6),
            "Result": status
        })

    elapsed = time.time() - t0
    print(f"\n  Total elapsed: {elapsed:.1f}s")
    return pd.DataFrame(rows)


def _save_report(df: pd.DataFrame, path: str):
    """Save results to a plain-text report file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write("KHAN Cipher - NIST SP 800-22 Rev. 1a "
                "Statistical Test Results\n")
        f.write("=" * 62 + "\n")
        f.write(f"Stream length: {STREAM_LENGTH_BITS:,} bits\n")
        skipped = ', '.join(SKIP_TESTS) if SKIP_TESTS else 'none'
        f.write(f"Skipped tests: {skipped}\n\n")
        f.write(df.to_string(index=False))
        f.write("\n\n")
        n_pass = len(df[df["Result"] == "PASS"])
        n_total = len(df)
        f.write(f"Summary: {n_pass}/{n_total} tests passed.\n")
    print(f"\n[+] Report saved to {path}")


def _parse_existing_report(path: str):
    """Print an existing report file."""
    with open(path, 'r') as f:
        print(f.read())


def main():
    print("NIST SP 800-22 Statistical Test Suite")
    print("=" * 42 + "\n")

    if os.path.exists(REPORT_PATH):
        print(f"[i] Report found: {REPORT_PATH}\n")
        _parse_existing_report(REPORT_PATH)
    else:
        print("[i] Generating keystream and running "
              "full battery...\n")
        bits = _generate_keystream_bits(STREAM_LENGTH_BITS)
        df = _run_nist_battery(bits)
        _save_report(df, REPORT_PATH)

        failed = df[df["Result"] == "FAIL"]
        if len(failed) > 0:
            print(f"\n[-] {len(failed)} test(s) FAILED:")
            for _, row in failed.iterrows():
                print(f"    {row['Test']}: p={row['P-Value']}")
        n = len(df)
        n_pass = len(df[df["Result"] == "PASS"])
        print(f"\n[*] Summary: {n_pass}/{n} NIST SP 800-22 "
              "tests passed.")


if __name__ == "__main__":
    main()
