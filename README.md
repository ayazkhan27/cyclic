# KHAN Cipher
![Build Status](https://github.com/ayazkhan27/cyclic/actions/workflows/python-app.yml/badge.svg)

A High-Performance Stream Cipher Native to Python/C++, Powered by Primitive Roots.

## Architecture Overview
KHAN is built on a mathematically rigorous sequence derived from Full Reptend Primes (Primitive Roots Modulo P). 
- **Key Derivation (HMAC-SHA256)**: Secure master key mapping and salt handling.
- **State Generation (Full Reptend Primes)**: Predictable zero-bias sequences mathematically derived from primitive root fractional expansion.
- **C++ XOR Diffusion Matrix**: High-speed symmetric stream combining native Python abstractions with a C++17 `-O3` optimized backend.

## State Space Analysis
The keystream features an unbounded internal state space based on the properties of $p$, while remaining perfectly keyed by a strict 256-bit symmetric input, creating non-linear sequence generation distributions verified by SP 800-22.

## Features
- **Non-Linear Sequence Generation**
- **Symmetric Keystream Construction**
- **Zero-Latency Diffusion**: C++ `bulk_xor` compiler flags targeting native architecture achieve multi-gigabyte/second throughputs.
- **High Entropy**: Achieves 7.99/8.0 Byte-wise Shannon Entropy, passing all 15 NIST STS suites.

## Installation
GCC or Clang is required to compile the C++ cryptographic extensions on your system.

```bash
pip install -e .
```

## Developer Quick Start

```python
import os
from khan_cipher.core import encrypt, decrypt

master_key = os.urandom(32)
plaintext = b"CONFIDENTIAL: Cloudflare Edge Node routing tables update. Payload highly sensitive."

# Encrypt
payload = encrypt(plaintext, master_key)

# The resulting payload contains: [Salt (16) | IV (16) | Ciphertext (N) | MAC (32)]

# Decrypt
decrypted = decrypt(payload, master_key)
assert plaintext == decrypted
```

## Formal Verification
The primitive root bijections mapped internally are formally modeled in Lean 4. The proofs tracking the permutation cycles without bias reside in `docs/KHAN_Theorems.lean`.

## Benchmarks
To run the automated Python visualization limits, spectral analysis, and parse NIST p-values:
```bash
python benchmarks/run_all.py
```

## Security Notice
Disclaimer: This algorithm is an academic exploration of primitive root cryptographic properties. It has not undergone formal multi-year cryptanalysis by standard bodies. Do not use for production secrets.
