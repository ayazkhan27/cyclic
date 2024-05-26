import matplotlib.pyplot as plt
import numpy as np

# Define the cyclic sequence for the prime 7
cyclic_sequence = '142857'
sequence_length = len(cyclic_sequence)
digit_positions = {digit: idx for idx, digit in enumerate(cyclic_sequence)}

def minimal_movement(start_digit, target_digit, digit_positions, sequence_length):
    start_pos = digit_positions[start_digit]
    target_pos = digit_positions[target_digit]
    
    # Calculate clockwise and anticlockwise movements
    clockwise_movement = (target_pos - start_pos) % sequence_length
    anticlockwise_movement = (start_pos - target_pos) % sequence_length
    
    # Return the minimal movement (positive for clockwise, negative for anticlockwise)
    return clockwise_movement if clockwise_movement <= anticlockwise_movement else -anticlockwise_movement

# Define the correct target digits for each fraction
fractions = [2, 3, 4, 5, 6]
target_digits = ['2', '4', '5', '7', '8']
expected_movements = [2, 1, -2, -1, 3]

movements = []

# Calculate movements for each target digit
for target_digit in target_digits:
    movement = minimal_movement(cyclic_sequence[0], target_digit, digit_positions, sequence_length)
    movements.append(movement)

# Print movements and net overall movement before plotting
superposition_movements = [m for m in movements if abs(m) == sequence_length // 2]
non_superposition_movements = [m for m in movements if abs(m) != sequence_length // 2]
net_movement = sum(non_superposition_movements)

print("Expected Movements:", expected_movements)
print("Calculated Movements:", movements)
print("Superposition Movements:", superposition_movements)
print("Net Overall Movement:", net_movement)

# Visualization
fig, ax = plt.subplots(figsize=(12, 6))

# Plot movements
for idx, (n, m) in enumerate(zip(fractions, movements)):
    fraction_label = f"{n}/7"
    if abs(m) == sequence_length // 2:
        ax.plot([idx, idx], [0, -m], 'purple', linestyle='dotted')
        ax.plot([idx, idx], [0, m], 'purple', linestyle='dotted')
    else:
        color = 'blue' if m > 0 else 'red' if m < 0 else 'green'
        ax.plot([idx, idx], [0, m], marker='o', color=color)

# Setting x-axis with fractions
ax.set_xticks(range(len(fractions)))
ax.set_xticklabels([f'{n}/7' for n in fractions])

# Setting y-axis with movements
ax.set_yticks(range(-sequence_length, sequence_length + 1))
ax.set_yticklabels(range(-sequence_length, sequence_length + 1))

# Adding second y-axis for cyclic sequence
secax = ax.secondary_yaxis('right')
# Calculate tick positions for cyclic sequence
sequence_ticks = list(range(-sequence_length, sequence_length + 1))
cyclic_labels = ['1', '4', '2', '8', '5', '7'] * ((len(sequence_ticks) // sequence_length) + 1)
cyclic_labels = cyclic_labels[:len(sequence_ticks)]
secax.set_yticks(sequence_ticks)
secax.set_yticklabels(cyclic_labels)

# Adjust secondary y-axis position to prevent overlap
secax.spines['right'].set_position(('outward', 40))

ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)
ax.grid(color='gray', linestyle='--', linewidth=0.5)
ax.set_title('Minimal Movements for Cyclic Prime 7')
ax.set_ylabel('Movement on Dial')
ax.set_xlabel('Fraction n/7')

plt.show()
