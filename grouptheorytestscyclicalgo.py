import random
from sympy.ntheory import isprime, primitive_root, primerange
from math import gcd as math_gcd
from decimal import Decimal, getcontext
import cyclic_khan_encryption as ke  # Import your new encryption module

# Helper function to check if a prime is a full reptend prime
def is_full_reptend_prime(prime):
    """
    Check if the given prime is a full reptend prime.
    """
    return isprime(prime) and primitive_root(prime) == 10

# Function to generate a cyclic sequence using a prime and its primitive root
def generate_cyclic_sequence(prime, length):
    """
    Generate a cyclic sequence using the primitive root of a prime number.
    """
    if not is_full_reptend_prime(prime):
        raise ValueError(f"The prime {prime} is not a full reptend prime.")
    
    root = primitive_root(prime)
    cyclic_sequence = [(root ** i) % prime for i in range(1, length + 1)]
    
    if len(set(cyclic_sequence)) < length // 2:
        raise ValueError("The cyclic sequence did not generate enough diversity.")
    
    return cyclic_sequence

def analyze_group_structure(cyclic_sequence, prime):
    """
    Analyze group properties of the cyclic sequence modulo the prime.
    """
    mod_values = [int(x) % prime for x in cyclic_sequence]
    length = len(mod_values)

    closure_test = all((mod_values[i] + mod_values[j]) % prime in mod_values for i in range(length) for j in range(length))
    print(f"Closure under addition modulo {prime}: {'Passed' if closure_test else 'Failed'}")
    
    identity_element = 0
    has_identity = any(x == identity_element for x in mod_values)
    print(f"Identity element (0 under addition modulo {prime}): {'Found' if has_identity else 'Not found'}")

    inverses_exist = all(any((mod_values[i] + mod_values[j]) % prime == identity_element for j in range(length)) for i in range(length))
    print(f"Inverses for each element: {'Exist' if inverses_exist else 'Do not exist'}")

    associativity_test = all(((mod_values[i] + (mod_values[j] + mod_values[k]) % prime) % prime == 
                              ((mod_values[i] + mod_values[j]) % prime + mod_values[k]) % prime)
                             for i in range(length) for j in range(length) for k in range(length))
    print(f"Associativity of addition modulo {prime}: {'Passed' if associativity_test else 'Failed'}")

def analyze_cyclic_subgroup_structure(cyclic_sequence, prime):
    """
    Analyze the cyclic subgroup properties. Specifically check if the sequence generates a cyclic subgroup of Z_prime.
    """
    mod_values = [int(x) % prime for x in cyclic_sequence]
    order = len(set(mod_values))
    
    is_cyclic_subgroup = (prime % order == 0)
    print(f"Generated cyclic subgroup: {'Yes' if is_cyclic_subgroup else 'No'} (Subgroup order: {order}, Prime: {prime})")

def check_gcd_with_prime(cyclic_sequence, prime):
    """
    Check if the greatest common divisor (gcd) of elements in the cyclic sequence with the prime is 1.
    """
    gcd_results = [math_gcd(int(x), prime) for x in cyclic_sequence]
    non_trivial_gcds = [g for g in gcd_results if g != 1]
    if non_trivial_gcds:
        print(f"Non-trivial gcd values found with prime: {non_trivial_gcds}")
    else:
        print("All elements are coprime with the prime.")

def main():
    # Choose a valid prime for generating a cyclic sequence
    full_reptend_primes = [p for p in primerange(100, 2000) if is_full_reptend_prime(p)]
    if not full_reptend_primes:
        raise ValueError("No full reptend primes found in the specified range.")
    
    # Select a prime and generate cyclic sequence
    prime = random.choice(full_reptend_primes)
    cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
    
    # Generate a start position
    start_position = random.randint(1, prime - 1)
    
    # Algebraic tests
    print("\n--- Group Theory and Algebraic Analysis ---")
    
    # Test group structure
    analyze_group_structure(cyclic_sequence, prime)

    # Check cyclic subgroup properties
    analyze_cyclic_subgroup_structure(cyclic_sequence, prime)

    # Check GCD with prime for potential vulnerabilities
    check_gcd_with_prime(cyclic_sequence, prime)

if __name__ == "__main__":
    main()
