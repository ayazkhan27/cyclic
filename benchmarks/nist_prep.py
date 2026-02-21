import os
import sys
from khan_cipher.core import KhanKeystream, derive_key


def main():
    os.makedirs('benchmarks/data', exist_ok=True)
    target_size = 1073741824  # 1 GB

    chunk_size = 10 * 1024 * 1024
    master_key = os.urandom(32)
    salt = os.urandom(16)
    iv = os.urandom(16)
    derived_key = derive_key(master_key, salt)
    ksg = KhanKeystream(derived_key, 100003, iv)

    print("Generating 1GB of KHAN keystream data...")
    with open('benchmarks/data/khan_1GB.bin', 'wb') as f:
        bytes_written = 0
        while bytes_written < target_size:
            sz = min(chunk_size, target_size - bytes_written)
            chunk = bytes([ksg.get_next_byte() for _ in range(sz)])
            f.write(chunk)
            bytes_written += len(chunk)
            print(f"Written {bytes_written / 1024 / 1024:.2f} MB", end='\r')
            sys.stdout.flush()

    print("\nGeneration complete. Ready for NIST STS or Dieharder.")


if __name__ == "__main__":
    main()
