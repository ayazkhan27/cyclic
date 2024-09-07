import sympy
import time

def khan_cyclic_sequence(p):
    if not sympy.isprime(p):
        return None

    # Determine block size k
    k = len(str(p))

    # Generate all possible k-digit blocks
    blocks = [f"{i:0{k}d}" for i in range(p-1)]
    blocks.sort()

    # Check if the middle digit is 9 (except for 7)
    middle_digit = '9' if p != 7 else '8'
    middle_index = (p-1) // 2
    if blocks[middle_index][0] != middle_digit:
        return None

    # Construct the sequence
    sequence = ''.join(blocks)

    return sequence

def modular_exponentiation_cyclic_sequence(p):
    if not sympy.isprime(p):
        return None

    sequence = ""
    current = 1
    for _ in range(p - 1):
        digit = (current * 10) // p
        sequence += str(digit)
        current = (current * 10) % p

    return sequence

def compare_algorithms(p):
    print(f"\nComparing algorithms for prime {p}:")

    start = time.time()
    khan_result = khan_cyclic_sequence(p)
    khan_time = time.time() - start

    start = time.time()
    mod_result = modular_exponentiation_cyclic_sequence(p)
    mod_time = time.time() - start

    print(f"Khan Method: {'Success' if khan_result else 'Failure'}")
    print(f"Time taken: {khan_time:.6f} seconds")

    print(f"Modular Exponentiation Method: {'Success' if mod_result else 'Failure'}")
    print(f"Time taken: {mod_time:.6f} seconds")

    if khan_result and mod_result:
        if khan_result == mod_result:
            print("Results match!")
        else:
            print("Results do not match.")
            print(f"Khan result: {khan_result}")
            print(f"Modular result: {mod_result}")

    if khan_time < mod_time:
        print("The Khan Method is faster.")
    elif mod_time < khan_time:
        print("The Modular Exponentiation Method is faster.")
    else:
        print("Both methods have similar performance.")

    return khan_result if khan_result else mod_result

def main():
    while True:
        try:
            p = int(input("Enter a full reptend prime number (or 0 to exit): "))
            if p == 0:
                break
            result = compare_algorithms(p)
            if result:
                print(f"Cyclic sequence for 1/{p}: {result}")
            else:
                print(f"{p} is not a full reptend prime or the method failed.")
        except ValueError:
            print("Please enter a valid integer.")

if __name__ == "__main__":
    main()