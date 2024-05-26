from sympy import primerange

def is_full_reptend(prime):
    for i in range(1, prime - 1):
        if pow(10, i, prime) == 1:
            if i == prime - 1:
                return True
        else:
            return False

def generate_full_reptend_primes(max_bit_size):
    full_reptend_primes = {}
    for bit_size in range(2, max_bit_size + 1):
        for prime in primerange(2 ** (bit_size - 1) + 1, 2 ** bit_size):
            if (prime - 1) % bit_size == 0 and is_full_reptend(prime):
                full_reptend_primes[bit_size] = prime
                break
    return full_reptend_primes

max_bit_size = 16  # Maximum bit size to consider
full_reptend_primes = generate_full_reptend_primes(max_bit_size)
print("Full Reptend Primes:")
for bit_size, prime in full_reptend_primes.items():
    print(f"{bit_size}-bit prime:", prime)
