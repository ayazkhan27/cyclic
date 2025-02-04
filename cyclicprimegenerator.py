from sympy import primerange, isprime, factorint
from multiprocessing import Pool, cpu_count

def is_full_reptend(prime):
    """
    Check if a prime number is a full reptend prime efficiently.
    A prime p is a full reptend prime if 10 is a primitive root modulo p.
    This means the smallest integer k for which 10^k ≡ 1 (mod p) is p-1.
    """
    if not isprime(prime):  # Ensure the number is prime
        return False

    phi = prime - 1  # Euler's totient function for prime p is p-1
    factors = factorint(phi).keys()  # Get unique prime factors of (p-1)

    # Check if 10^(phi/q) % p != 1 for all prime factors q of phi
    if all(pow(10, phi // q, prime) != 1 for q in factors):
        return True
    return False

def find_full_reptend_prime_for_bit(bit_size):
    """
    Find the first full reptend prime in the given bit size range.
    """
    start, end = 2 ** (bit_size - 1), 2 ** bit_size
    for prime in primerange(start, end):
        if is_full_reptend(prime):
            return (bit_size, prime)
    return (bit_size, None)  # No full reptend prime found in this range

def generate_full_reptend_primes(max_bit_size):
    """
    Generate full reptend primes for bit sizes up to max_bit_size using parallel processing.
    Returns a dictionary mapping bit size to the first full reptend prime found in that range.
    """
    with Pool(cpu_count()) as pool:  # Use all available CPU cores
        results = pool.map(find_full_reptend_prime_for_bit, range(2, max_bit_size + 1))
    # Filter out any bit sizes that didn't yield a prime.
    return {bit_size: prime for bit_size, prime in results if prime}

# Specify the maximum bit size to consider (you can increase this as needed)
max_bit_size = 64
full_reptend_primes = generate_full_reptend_primes(max_bit_size)

print("\nFull Reptend Primes by Bit Size:")
for bit_size, prime in sorted(full_reptend_primes.items()):
    print(f"{bit_size}-bit full-reptend prime: {prime}")

# Create a sorted list of the full reptend primes (by prime value)
sorted_frps = sorted(full_reptend_primes.values())

# Print the list in a format you can copy and paste into your analysis script.
print("\nSorted List of Full Reptend Primes:")
print(sorted_frps)

# Optionally, if you want a comma-separated string (for easy copy-paste as a Python list literal):
frp_list_literal = ", ".join(str(p) for p in sorted_frps)
print("\nPython List Literal:")
print(f"[{frp_list_literal}]")
