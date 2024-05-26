import matplotlib.pyplot as plt
import numpy as np

# Define the numbers on the dial
numbers = [1, 4, 2, 8, 5, 7]

# Number of points on the dial
num_points = len(numbers)

# Generate angles for each number
angles = np.linspace(0, 2*np.pi, num_points, endpoint=False).tolist()

# Create the plot
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect('equal')

# Plot the dial numbers
for num, angle in zip(numbers, angles):
    x = (1.15) * np.cos(angle)  # Adjusted radius
    y = (1.15) * np.sin(angle)  # Adjusted radius
    ax.text(x, y, str(num), ha='center', va='center', fontsize=18)  # Increased font size

# Draw the circle
circle = plt.Circle((0, 0), 1, color='black', fill=False)
ax.add_artist(circle)

# Set axis limits and remove axis labels
ax.set_xlim(-1.5, 1.5)  # Adjusted axis limits
ax.set_ylim(-1.5, 1.5)  # Adjusted axis limits
ax.axis('off')

# Save the figure
plt.savefig('circular_dial.png', bbox_inches='tight')
plt.show()
