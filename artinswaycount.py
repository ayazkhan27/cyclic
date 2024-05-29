import sympy

def is_full_reptend_prime(p):
    # Check if p is not 2 or 5 and the order of 10 modulo p is p-1
    if p in (2, 5):
        return False
    return sympy.ntheory.residue_ntheory.n_order(10, p) == p - 1

def count_full_reptend_primes(limit):
    primes = list(sympy.primerange(1, limit))
    full_reptend_primes_count = sum(1 for prime in primes if is_full_reptend_prime(prime))
    return full_reptend_primes_count

def main():
    max_n = 4  # Set the maximum n value as per the OEIS A086018 sequence
    results = []

    for n in range(1, max_n + 1):
        limit = 10 ** n
        count = count_full_reptend_primes(limit)
        results.append(count)
        print(f"A086018 for 10^{n}: {count}")

if __name__ == "__main__":
    main()
