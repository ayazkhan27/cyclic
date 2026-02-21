import subprocess
import sys
import os

def main():
    scripts = [
        "benchmarks/entropy_metrics.py",
        "benchmarks/spectral_analysis.py",
        "benchmarks/autocorrelation.py",
        "benchmarks/parse_nist.py"
    ]
    
    print("==============================================")
    print("Executing ALL KHAN Benchmark Validation Suites")
    print("==============================================\n")
    
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    for script in scripts:
        print(f"[*] Running {script}...")
        try:
            subprocess.run([sys.executable, script], check=True)
            print(f"[+] {script} completed successfully.\n")
        except subprocess.CalledProcessError as e:
            print(f"[-] {script} failed with error {e}.\n")
            
    print("All Python generation and visualization tasks complete.")

if __name__ == "__main__":
    main()
