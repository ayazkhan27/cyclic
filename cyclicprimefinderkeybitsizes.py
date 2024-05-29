import sympy
from decimal import Decimal, getcontext

# Function to calculate the decimal expansion of the reciprocal of a prime
def calculate_decimal_expansion(prime):
    getcontext().prec = prime - 1  # Set precision to the length of the expansion
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]  # Get decimal expansion as string, skipping '0.'
    return decimal_expansion

# Function to find the first n full reptend prime numbers
def get_first_n_full_reptend_primes(n):
    full_reptend_primes = []
    candidate = 7  # Start from the smallest known full reptend prime
    while len(full_reptend_primes) < n:
        if sympy.isprime(candidate) and sympy.is_primitive_root(10, candidate):
            full_reptend_primes.append(candidate)
        candidate += 2  # Increment by 2 to check the next odd number
    return full_reptend_primes

# Main function to generate full reptend primes and their cyclic sequences for specified key sizes
def generate_full_reptend_primes_and_sequences(key_sizes):
    full_reptend_primes = {}
    for bits in key_sizes:
        closest_prime = None
        closest_diff = float('inf')
        primes = get_first_n_full_reptend_primes(10)  # Get the first 10 full reptend primes
        for prime in primes:
            diff = abs(bits - prime.bit_length())
            if diff < closest_diff:
                closest_prime = prime
                closest_diff = diff
        if closest_prime:
            cyclic_sequence = calculate_decimal_expansion(closest_prime)
            full_reptend_primes[bits] = (closest_prime, cyclic_sequence)
    return full_reptend_primes

# Specify the key sizes
key_sizes = [2, 4, 8, 16, 32, 64]

# Generate full reptend primes and their respective cyclic sequences for specified key sizes
full_reptend_primes = generate_full_reptend_primes_and_sequences(key_sizes)

# Display the results
for bits, (prime, cyclic_sequence) in full_reptend_primes.items():
    print(f"Key Size: {bits} bits, Full Reptend Prime: {prime}, Cyclic Sequence: {cyclic_sequence}")
