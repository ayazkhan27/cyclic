from decimal import Decimal, getcontext

def calculate_decimal_expansion(prime):
    # Set precision to (p-1) digits
    getcontext().prec = prime - 1
    
    # Calculate the reciprocal of the prime
    reciprocal = Decimal(1) / Decimal(prime)
    
    # Convert to string and remove the '0.' prefix
    decimal_expansion = str(reciprocal)[2:]
    
    # Return the first (p-1) digits
    return decimal_expansion[:prime - 1]

# Calculate the decimal expansion of 1/257
decimal_expansion_257 = calculate_decimal_expansion(257)
print("Decimal expansion of 1/257 (first 256 digits):", decimal_expansion_257)

# Calculate the decimal expansion of 1/65537
decimal_expansion_65537 = calculate_decimal_expansion(65537)
print("Decimal expansion of 1/65537 (first 65536 digits):", decimal_expansion_65537)
