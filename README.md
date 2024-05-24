# KHAN Algorithm (Key Hashed and Asymmetric Nonce) Encryption System

## Overview

The KHAN (Key Hashed and Asymmetric Nonce) Algorithm is an advanced cryptographic system designed for secure data encryption and decryption. It employs unique techniques such as cyclic primes, superposition sequences, and layered encryption to provide robust security. This README provides a comprehensive guide to understanding and utilizing the KHAN encryption system, including its core functions and usage.

## Features

- **Cyclic Prime and Sequence**: Utilizes cyclic primes and sequences to generate unique encryption keys.
- **Superposition Sequence**: Implements superposition sequences to enhance encryption complexity.
- **Z-Layers**: Employs Z-layers for additional encryption depth.
- **IV and Salt**: Uses Initialization Vector (IV) and Salt for added security.
- **Multiple Encryption Layers**: Supports multiple encryption layers for robust security.

## Modules

### khan_encryption.py

#### Core Functions

- **generate_plaintext(length)**: Generates a random plaintext string of specified length.
- **minimal_movement(start_sequence, target_sequence, digit_positions, sequence_length)**: Calculates the minimal movement required between sequences.
- **generate_target_sequences(prime, cyclic_sequence)**: Generates target sequences based on the cyclic prime.
- **analyze_cyclic_prime(prime, cyclic_sequence, start_position)**: Analyzes the cyclic prime and returns movements for each sequence.
- **generate_keys(prime, cyclic_sequence, start_position)**: Generates encryption and decryption keys.
- **generate_superposition_sequence(prime)**: Generates a superposition sequence.
- **calculate_z_value(superposition_sequence)**: Calculates the Z-value from the superposition sequence.
- **assign_z_layer(movement, salt)**: Assigns a Z-layer to a movement based on a hashed salt.
- **khan_encrypt(plaintext, prime, cyclic_sequence, start_position)**: Encrypts the plaintext using the KHAN algorithm.
- **khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, prime, start_position, cyclic_sequence)**: Decrypts the ciphertext using the KHAN algorithm.
- **encrypt_message(plaintext, char_to_movement, z_value, superposition_sequence, salt, prime)**: Encrypts a message into ciphertext.
- **decrypt_message(cipher_text, movement_to_char, z_value, superposition_sequence, z_layers, salt, prime)**: Decrypts a ciphertext back into plaintext.

### masterpiecencryption.py

#### Usage

This script demonstrates how to utilize the KHAN encryption functions to encrypt and decrypt a message. It includes user input for starting dial positions and superposition sequences, measures encryption and decryption times, and verifies the success of the decryption.

### cyclicprimerelations.py

#### Visualization

Provides functions to compute and visualize minimal movements for a given cyclic prime. This script helps understand the movements within the cyclic sequence and the impact of different primes.

### 3Dcyclicplot.py

#### 3D Visualization

Offers 3D visualization of minimal movements for cyclic primes, showing the relationship between different levels of movements and their corresponding primes.

## Example Usage

### Encryption and Decryption

```python
from khan_encryption import khan_encrypt, khan_decrypt

# Setup encryption parameters
cyclic_prime = 167
start_position = 43
cyclic_sequence = '005988023952095808383233532934131736526946107784431137724550898203592814371257485029940119760479041916167664670658682634730538922155688622754491017964071856287425149700598802395209580838323353293413173652694610778443113772455089820359281437125748502994011976047904191616766467065868263473053892215568862275449101796407185628742514970059880239520958083832335329341317365269461077844311377245508982035928143712574850299401197604790419161676646706586826347305389221556886227544910179640718562874251497'[:166]

# Generate random plaintext
plaintext = generate_plaintext(128)

# Encrypt the plaintext
ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = khan_encrypt(plaintext, cyclic_prime, cyclic_sequence, start_position)

# Decrypt the ciphertext
decrypted_text = khan_decrypt(ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers, cyclic_prime, start_position, cyclic_sequence)

# Verify decryption
assert plaintext == decrypted_text
print("Decryption successful!")
