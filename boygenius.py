import sympy as sp

# Define symbols
n, k = sp.symbols('n k')
S = sp.Function('S')(n)  # Cyclic sequence
M = sp.Function('M')(S, S)  # Minimal movement function

# Theorem 1: Uniqueness of Movements
unique_movements_theorem = sp.All(M(S, S) == M(S, S), (S,))

# Theorem 2: Net Overall Movement is Zero
net_movement_theorem = sp.Eq(sp.Sum(M(S, S), (S, 1, n-1)), 0)

# Theorem 3: Superposition Movement is Half the Sequence Length
superposition_movement_theorem = sp.Eq(M(S, S), (n-1) // 2)

# Theorem 4: Total Unique Movements
total_unique_movements_theorem = sp.Eq(sp.Cardinality(sp.FiniteSet(M(S, S) for S in range(1, n))), n-3)

# Verify theorems
theorem_proofs = {
    'unique_movements_theorem': unique_movements_theorem,
    'net_movement_theorem': net_movement_theorem,
    'superposition_movement_theorem': superposition_movement_theorem,
    'total_unique_movements_theorem': total_unique_movements_theorem
}

for name, theorem in theorem_proofs.items():
    print(f"{name}: {sp.simplify(theorem)}")
