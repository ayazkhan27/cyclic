from sympy import primerange, isprime, factorint
from multiprocessing import Pool, cpu_count

def is_full_reptend(prime):
    """
    Check if a prime number is a full reptend prime.
    A prime p is a full reptend prime if 10 is a primitive root modulo p.
    That is, the smallest integer k for which 10^k ≡ 1 (mod p) is p-1.
    """
    if not isprime(prime):
        return False

    phi = prime - 1  # For a prime, Euler's totient is p-1.
    factors = factorint(phi).keys()  # Unique prime factors of (p-1).

    # 10 must not have order dividing any factor of p-1.
    return all(pow(10, phi // q, prime) != 1 for q in factors)

def check_full_reptend(prime):
    """
    Returns the prime if it is a full reptend prime; otherwise returns None.
    """
    return prime if is_full_reptend(prime) else None

def generate_all_full_reptend_primes(start, end):
    """
    Generate all full reptend primes in the interval [start, end) using multiprocessing.
    """
    # Get all prime numbers in the given range.
    primes = list(primerange(start, end))
    
    with Pool(cpu_count()) as pool:
        results = pool.map(check_full_reptend, primes)
    
    # Filter out None values (non-full-reptend primes)
    return [p for p in results if p is not None]

if __name__ == '__main__':
    # For example, find all FRPs from 983 up to 10,000.
    start_val = 10000
    end_val = 11000  # Adjust this as needed.
    
    frp_list = generate_all_full_reptend_primes(start_val, end_val)
    
    print(f"Full Reptend Primes from {start_val} to {end_val}:")
    print(frp_list)
    
    # Optionally, print them as a Python list literal for easy copy-paste.
    frp_list_literal = ", ".join(str(p) for p in frp_list)
    print("\nPython List Literal:")
    print(f"[{frp_list_literal}]")
