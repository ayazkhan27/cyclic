import numpy as np
from sympy.ntheory import isprime
from sympy import gcd, Matrix
from math import gcd as math_gcd
import random
import string
from decimal import Decimal, getcontext
import khan_encryption_2 as ke
import matplotlib.pyplot as plt

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

def analyze_group_structure(cyclic_sequence, prime):
    """
    Analyze group properties of the cyclic sequence modulo the prime.
    Check for closure, identity, inverses, and associativity in the group.
    """
    mod_values = [int(x) % prime for x in cyclic_sequence]  # Modulo prime for each value in the sequence
    length = len(mod_values)

    # Check for closure: a + b (mod prime) must stay in the group
    closure_test = all((mod_values[i] + mod_values[j]) % prime in mod_values for i in range(length) for j in range(length))
    print(f"Closure under addition modulo {prime}: {'Passed' if closure_test else 'Failed'}")
    
    # Check for identity element
    identity_element = 0
    has_identity = any(x == identity_element for x in mod_values)
    print(f"Identity element (0 under addition modulo {prime}): {'Found' if has_identity else 'Not found'}")

    # Check for inverses: for each a, there must be some b such that (a + b) % prime = 0
    inverses_exist = all(any((mod_values[i] + mod_values[j]) % prime == identity_element for j in range(length)) for i in range(length))
    print(f"Inverses for each element: {'Exist' if inverses_exist else 'Do not exist'}")

    # Check for associativity (a + (b + c)) % prime == ((a + b) + c) % prime
    associativity_test = all(((mod_values[i] + (mod_values[j] + mod_values[k]) % prime) % prime == 
                              ((mod_values[i] + mod_values[j]) % prime + mod_values[k]) % prime)
                             for i in range(length) for j in range(length) for k in range(length))
    print(f"Associativity of addition modulo {prime}: {'Passed' if associativity_test else 'Failed'}")

def analyze_cyclic_subgroup_structure(cyclic_sequence, prime):
    """
    Analyze the cyclic subgroup properties. Specifically check if the sequence generates a cyclic subgroup of Z_prime.
    """
    mod_values = [int(x) % prime for x in cyclic_sequence]  # Modulo prime for each value in the sequence
    order = len(set(mod_values))  # The number of unique elements under modulo prime
    
    # The subgroup order must divide the group order (which is prime)
    is_cyclic_subgroup = (prime % order == 0)
    print(f"Generated cyclic subgroup: {'Yes' if is_cyclic_subgroup else 'No'} (Subgroup order: {order}, Prime: {prime})")

def check_gcd_with_prime(cyclic_sequence, prime):
    """
    Check if the greatest common divisor (gcd) of elements in the cyclic sequence with the prime is 1.
    If gcd(x, prime) != 1 for any x, it could indicate a potential weakness.
    """
    gcd_results = [math_gcd(int(x), prime) for x in cyclic_sequence]
    non_trivial_gcds = [g for g in gcd_results if g != 1]
    if non_trivial_gcds:
        print(f"Non-trivial gcd values found with prime: {non_trivial_gcds}")
    else:
        print("All elements are coprime with the prime.")

def main():
    cyclic_prime = 1051  # The prime used in the cyclic sequence
    start_position = 551  # Starting position for encryption

    # Generate cyclic sequence
    cyclic_sequence = generate_cyclic_sequence(cyclic_prime, cyclic_prime - 1)

    # Algebraic tests
    print("\n--- Group Theory and Algebraic Analysis ---")
    
    # Test group structure
    analyze_group_structure(cyclic_sequence, cyclic_prime)

    # Check cyclic subgroup properties
    analyze_cyclic_subgroup_structure(cyclic_sequence, cyclic_prime)

    # Check GCD with prime for potential vulnerabilities
    check_gcd_with_prime(cyclic_sequence, cyclic_prime)

if __name__ == "__main__":
    main()
