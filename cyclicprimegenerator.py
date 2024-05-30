from sympy import primerange, isprime

def is_full_reptend(prime):
    # Check if 10 is a primitive root modulo prime
    for i in range(1, prime - 1):
        if pow(10, i, prime) == 1:
            if i == prime - 1:
                return True
            else:
                return False
    return True

def generate_full_reptend_primes(max_bit_size):
    full_reptend_primes = {}
    for bit_size in range(2, max_bit_size + 1):
        print(f"Checking {bit_size}-bit primes...")
        start = 2 ** (bit_size - 1)
        end = 2 ** bit_size
        for prime in primerange(start, end):
            if is_full_reptend(prime):
                full_reptend_primes[bit_size] = prime
                print(f"Found {bit_size}-bit full reptend prime: {prime}")
                break
    return full_reptend_primes

max_bit_size = 20  # Maximum bit size to consider
full_reptend_primes = generate_full_reptend_primes(max_bit_size)
print("Full Reptend Primes:")
for bit_size, prime in full_reptend_primes.items():
    print(f"{bit_size}-bit prime:", prime)
