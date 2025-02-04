import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from mpl_toolkits.mplot3d import Axes3D

# Function to generate movement data based on your minimal movement rules
def generate_movement_data(prime, cyclic_sequence):
    """ Generates structured 3D movement data based on cyclic prime properties """
    sequence_length = prime - 1
    x_vals, y_vals, z_vals = [], [], []
    digit_positions = {str(i): [idx for idx, d in enumerate(cyclic_sequence) if d == str(i)] for i in range(10)}

    def minimal_movement(start, target):
        """ Compute minimal movement with modular constraints """
        start_positions = digit_positions[start]
        target_positions = digit_positions[target]
        min_movement = sequence_length
        for s in start_positions:
            for t in target_positions:
                cw = (t - s) % sequence_length
                ccw = (s - t) % sequence_length
                movement = cw if cw <= ccw else -ccw
                min_movement = movement if abs(movement) < abs(min_movement) else min_movement
        return min_movement

    # Generate movements for each fraction
    fractions = list(range(1, prime))
    movements = [minimal_movement(cyclic_sequence[0], cyclic_sequence[i]) for i in range(1, min(len(cyclic_sequence), prime))]


    # Extend into 3D space with superposition structure
    z = 0
    for i in range(20):  # Increase depth for better fractal analysis
        for idx, (n, m) in enumerate(zip(fractions, movements)):
            x_vals.append((i * prime) + n)
            y_vals.append(m)
            z_vals.append(z)
        z += 1
        for idx in range(len(movements)):  # Flip superposition movement at each level
            if abs(movements[idx]) == (prime - 1) // 2:
                movements[idx] = -movements[idx]

    return np.array(x_vals), np.array(y_vals), np.array(z_vals)

# Box-counting method with modular adaptation
def box_counting(x, y, z, min_box_size=1, max_box_size=10, num_scales=10):
    """ Compute fractal dimension using modified box-counting for modular data """
    box_sizes = np.logspace(np.log10(min_box_size), np.log10(max_box_size), num_scales)
    counts = []
    for box_size in box_sizes:
        grid_x = (x // box_size).astype(int)
        grid_y = (y // box_size).astype(int)
        grid_z = (z // box_size).astype(int)
        unique_boxes = set(zip(grid_x, grid_y, grid_z))
        counts.append(len(unique_boxes))
    return box_sizes, counts

# Compute fractal dimension for prime 17
prime = 17
cyclic_sequence = '0588235294117647'  # Full reptend decimal expansion
x_vals, y_vals, z_vals = generate_movement_data(prime, cyclic_sequence)
box_sizes, counts = box_counting(x_vals, y_vals, z_vals)

# Perform log-log regression
log_box_sizes = np.log(box_sizes)
log_counts = np.log(counts)
slope, intercept, _, _, _ = linregress(log_box_sizes, log_counts)
fractal_dimension = -slope

# Plot log-log fractal dimension estimation
plt.figure(figsize=(8, 6))
plt.scatter(log_box_sizes, log_counts, label="Box Counting Data")
plt.plot(log_box_sizes, intercept + slope * log_box_sizes, 'r', label=f"Fit Line (D_f = {fractal_dimension:.2f})")
plt.xlabel("log(Box Size)")
plt.ylabel("log(Count of Boxes)")
plt.legend()
plt.title(f"Fractal Dimension Estimation for Cyclic Prime {prime}")
plt.show()

print(f"Estimated Fractal Dimension: {fractal_dimension:.2f}")
