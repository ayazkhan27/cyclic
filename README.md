# KHAN Encryption Algorithm

## Overview
The Keyed Hashing and Asymmetric Nonce (KHAN) encryption algorithm is a novel encryption system based on cyclic primes and unique movement patterns. This algorithm ensures that each character in the plaintext is mapped to a unique movement in the cyclic sequence, providing robust security through its unique mathematical foundations.

## Features
- **Unique Movement Patterns:** Each character in the plaintext is mapped to a unique movement in the cyclic sequence.
- **Cyclic Primes:** Utilizes cyclic prime numbers and their sequences to generate encryption keys.
- **Superposition Movements:** Handles equal clockwise and anticlockwise movements efficiently.
- **Overall Net Movement of Zero:** Ensures that the net overall movement for each pattern sequence results in zero.
- **Security:** Designed to be resistant to common brute-force and frequency analysis attacks.

## Mathematical Description

Let \( p \) be a cyclic prime number, and let \( S \) be the first \( p-1 \) digits of its cyclic sequence.

For any \( n \) and \( k \) such that \( 1 \leq k \leq n \), let:

\[ S_k = \text{substring of } S \text{ starting at } k \text{ and length } \lfloor \log_{10}(p) \rfloor \]

### Movements
- **Clockwise Movement:**
\[ \text{clockwise}_k = (S_k - S_{k+1}) \mod (p-1) \]

- **Anticlockwise Movement:**
\[ \text{anticlockwise}_k = (S_{k+1} - S_k) \mod (p-1) \]

- **Minimal Movement:**
\[ \text{movement}_k = \min(\text{clockwise}_k, \text{anticlockwise}_k) \]

### Superposition Movements
A superposition movement occurs when the minimal movement is equal in both directions. The magnitude of the superposition movement is:

\[ \text{superposition} = \frac{p-1}{2} \]

### Net Overall Movement
The algorithm ensures that the overall net movement for each pattern sequence results in zero, thereby maintaining the integrity and consistency of the encryption:

\[ \sum_{k=1}^{n} \text{movement}_k = 0 \]

## Usage

### Installation

First, install the necessary dependencies using pip:
```sh
pip install pycryptodome
