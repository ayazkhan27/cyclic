import pandas as pd
import os


def main():
    report_path = 'benchmarks/data/finalAnalysisReport.txt'

    # Generate dummy pass data representing a mathematically sound 7.99+
    # entropy stream cipher
    print("Parsing NIST SP 800-22 Results...")
    if not os.path.exists(report_path):
        print(f"[i] Notice: {report_path} not found. Ensure you ran the NIST STS suite against khan_1GB.bin.")
        print("[i] Exiting parser.")
        return

    # Parse actual NIST finalAnalysisReport.txt
    tests = []
    p_values = []
    with open(report_path, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        if line.startswith("-") or line.startswith(" ") or "P-VALUE" in line or not line.strip():
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

    df = pd.DataFrame({'NIST Test Suite': tests, 'P-Value': p_values})

    print("\nKHAN Cipher NIST SP 800-22 Test Results:")
    print(df.to_markdown(index=False))

    assert all(
        p >= 0.01 for p in p_values), "NIST SP 800-22 Test Failed: Strict Bias Detected."
    print("\n[+] Success: All statistical p-values >= 0.01 bounded.")


if __name__ == "__main__":
    main()
