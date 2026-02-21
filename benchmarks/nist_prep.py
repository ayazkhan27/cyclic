import os
import sys
from khan_cipher.core import encrypt

def main():
    os.makedirs('benchmarks/data', exist_ok=True)
    target_size = 1073741824 # 1 GB
    
    chunk_size = 10 * 1024 * 1024
    master_key = os.urandom(32)
    
    print(f"Generating 1GB of KHAN keystream data...")
    with open('benchmarks/data/khan_1GB.bin', 'wb') as f:
        bytes_written = 0
        while bytes_written < target_size:
            plaintext = b'\x00' * min(chunk_size, target_size - bytes_written)
            payload = encrypt(plaintext, master_key)
            keystream = payload[32:-32]
            f.write(keystream)
            bytes_written += len(keystream)
            print(f"Written {bytes_written / 1024 / 1024:.2f} MB", end='\r')
            sys.stdout.flush()
            
    print("\nGeneration complete. Ready for NIST STS or Dieharder.")

if __name__ == "__main__":
    main()
