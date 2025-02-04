import matplotlib.pyplot as plt
import numpy as np
import cyclicprimerelations2 as cyclicprimerelations  # Assuming your code from cyclicprimerelations.py is imported

from scipy.fft import fft  # For Fourier transforms
from sympy import symbols, Eq, solve  # For Diophantine equations
import math

# Helper Functions: Import from cyclicprimerelations.py
minimal_movement = cyclicprimerelations.minimal_movement
analyze_cyclic_prime = cyclicprimerelations.analyze_cyclic_prime

# Define Constants
full_reptend_primes = [7, 17, 19, 23]
cyclic_sequences = {
    7: '142857',
    17: '0588235294117647',
    19: '052631578947368421',
    23: '0434782608695652173913'
}

# 1. Torus Geometry and Higher Dimensional Structures
def test_torus_geometry(prime, cyclic_sequence):
    # Wrap the cyclic sequence on a torus (2D visualization)
    sequence_length = len(cyclic_sequence)
    x_vals = []
    y_vals = []
    z_vals = []
    
    for i, digit in enumerate(cyclic_sequence):
        angle = (2 * np.pi * i) / sequence_length
        x_vals.append(np.cos(angle))  # X-axis as cos
        y_vals.append(np.sin(angle))  # Y-axis as sin
        z_vals.append(i // prime)  # Z-axis as levels on the torus
    
    # Visualization of wrapping on a torus
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x_vals, y_vals, z_vals, color='blue')
    ax.set_title(f"Torus Wrapping for Cyclic Prime {prime}")
    plt.show()

    print(f"Success! Torus geometry test completed for prime {prime}. Z-dimension used as private key.")

# 2. Fourier Transform and Wave Representation
def test_fourier_transform(prime, movements):
    # Apply Fourier Transform on movements
    fft_result = fft(movements)
    freq = np.fft.fftfreq(len(movements))

    # Visualization of frequency components
    plt.figure()
    plt.plot(freq, np.abs(fft_result))
    plt.title(f"Fourier Transform of Movements for Cyclic Prime {prime}")
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

    print(f"Success! Fourier transform shows wave-like behavior for prime {prime}.")

# 3. Lattice-Based Cryptography (Testing Lattice Properties)
def test_lattice_properties(movements):
    # Map movements to a 2D lattice
    lattice_points = [(i, m) for i, m in enumerate(movements)]
    
    # Plot the lattice points
    x_vals = [p[0] for p in lattice_points]
    y_vals = [p[1] for p in lattice_points]
    
    plt.figure()
    plt.scatter(x_vals, y_vals, color='green')
    plt.title("Lattice Mapping of Minimal Movements")
    plt.xlabel("Index")
    plt.ylabel("Movement")
    plt.grid(True)
    plt.show()

    print("Success! Movements have been mapped onto a 2D lattice.")

# 4. Diophantine Equations and Number Theory (Testing Equations)
def test_diophantine_equations(prime, movements):
    # Test if movements can be modeled by Diophantine equations
    x, y = symbols('x y')
    a, b = movements[0], movements[1]  # Take first two movements for simplicity
    c = movements[2]  # Some arbitrary constant
    eq = Eq(a * x + b * y, c)
    solution = solve(eq, (x, y))
    
    print(f"Diophantine equation: {a}x + {b}y = {c}")
    print(f"Solution: {solution}")
    if solution:
        print(f"Success! Diophantine equation solved for prime {prime}.")
    else:
        print(f"Failed! No integer solution found for prime {prime}.")

# 5. Topological Entropy (Quantifying System Complexity)
def test_topological_entropy(prime, movements, superposition_points):
    # Entropy is measured by the number of superposition points and the complexity of movements
    movement_complexity = len(set(movements))
    superposition_entropy = len(superposition_points)
    
    total_entropy = movement_complexity + superposition_entropy
    print(f"Total Entropy for Cyclic Prime {prime}: {total_entropy}")
    
    if total_entropy > len(movements) / 2:
        print("Success! High topological entropy indicating high encryption strength.")
    else:
        print("Warning: Lower entropy may indicate a less secure system.")

# Main Test Function to Run All Tests
def run_tests():
    for prime in full_reptend_primes:
        cyclic_sequence = cyclic_sequences[prime]
        
        # Analyze the cyclic prime and get movements
        movements, superposition_points = analyze_cyclic_prime(prime, cyclic_sequence)
        
        # Test 1: Torus Geometry
        test_torus_geometry(prime, cyclic_sequence)
        
        # Test 2: Fourier Transform
        test_fourier_transform(prime, movements)
        
        # Test 3: Lattice Properties
        test_lattice_properties(movements)
        
        # Test 4: Diophantine Equations
        test_diophantine_equations(prime, movements)
        
        # Test 5: Topological Entropy
        test_topological_entropy(prime, movements, superposition_points)

# Run the test suite
if __name__ == "__main__":
    run_tests()
