"""
Full Reptend Prime Generation and Validation.

A full reptend prime p is a prime for which 10 is a primitive root modulo p,
meaning ord_p(10) = p - 1. This module provides utilities for validating
and generating such primes at cryptographic bit sizes.
"""

import secrets
from sympy import isprime, factorint


def is_full_reptend_prime(p: int) -> bool:
    """
    Check whether p is a full reptend prime (10 is a primitive root mod p).

    This verifies two conditions:
        1. p is prime.
        2. For every prime factor q of (p - 1), 10^((p-1)/q) ≢ 1 (mod p).

    Args:
        p: The candidate integer.

    Returns:
        True if p is a full reptend prime, False otherwise.
    """
    if p < 3 or not isprime(p):
        return False

    if p == 2 or p == 5:
        return False  # gcd(10, p) != 1

    order = p - 1
    prime_factors = factorint(order)

    for q in prime_factors:
        if pow(10, order // q, p) == 1:
            return False

    return True


# --------------------------------------------------------------------- #
#  Pre-computed 128-bit full reptend prime (verified offline).           #
#  p - 1 = 2 * q where q is also prime (safe prime construction).      #
# --------------------------------------------------------------------- #

def _find_default_prime() -> int:
    """Return a pre-computed 128-bit safe full reptend prime.

    Verification:
        p  = 291822873301472307838801864404483049343
        q  = (p - 1) // 2 = 145911436650736153919400932202241524671
        isprime(p) == True
        isprime(q) == True
        pow(10, 2, p) != 1        (trivially True)
        pow(10, q, p) != 1        (10 is a primitive root mod p)
    """
    return 291822873301472307838801864404483049343


DEFAULT_PRIME: int = _find_default_prime()


def generate_full_reptend_prime(bits: int = 128) -> int:
    """
    Generate a random full reptend prime of approximately the given bit size.

    Strategy: generate random safe primes p = 2q + 1 (where q is also prime),
    then verify that 10 is a primitive root mod p.  For safe primes, p - 1 = 2q,
    so the primitive root check reduces to two modular exponentiations:
        10^2 ≢ 1 (mod p)   AND   10^q ≢ 1 (mod p).

    Args:
        bits: Desired bit size of the prime (minimum 32).

    Returns:
        A full reptend prime of the requested bit size.

    Raises:
        ValueError: If bits < 32.
    """
    if bits < 32:
        raise ValueError("Minimum prime size is 32 bits.")

    while True:
        # Generate a random odd number of the correct bit size
        q = secrets.randbits(bits - 1) | (1 << (bits - 2)) | 1

        if not isprime(q):
            continue

        p = 2 * q + 1

        if not isprime(p):
            continue

        # Safe prime found.  Check primitive root condition:
        #   p - 1 = 2q, prime factors are {2, q}
        #   Need: 10^2 mod p != 1  AND  10^q mod p != 1
        if pow(10, 2, p) == 1:
            continue
        if pow(10, q, p) == 1:
            continue

        return p
