import matplotlib.pyplot as plt

def get_repeating_sequence(n):
    sequence = ""
    remainder = 1
    remainders = {}
    pos = 0

    while remainder != 0 and remainder not in remainders:
        remainders[remainder] = pos
        remainder *= 10
        digit = remainder // n
        sequence += str(digit)
        remainder %= n
        pos += 1

    if remainder in remainders:
        start = remainders[remainder]
        sequence = sequence[start:]

    return sequence

def minimal_movement(start_digit, target_digit, digit_positions, sequence_length):
    start_pos = digit_positions[start_digit]
    target_pos = digit_positions[target_digit]
    clockwise_movement = (target_pos - start_pos) % sequence_length
    anticlockwise_movement = (start_pos - target_pos) % sequence_length
    return clockwise_movement if clockwise_movement <= anticlockwise_movement else -anticlockwise_movement

def visualize_cyclic_prime(n):
    repeating_sequence = get_repeating_sequence(n)
    sequence_length = len(repeating_sequence)
    digit_positions = {digit: idx for idx, digit in enumerate(repeating_sequence)}

    starting_digit = repeating_sequence[0]
    print(f"Repeating sequence for 1/{n}: {repeating_sequence}")
    print(f"Starting digit for 1/{n}: {starting_digit}")

    fractions = list(range(2, n))
    movements = []
    starting_digits = [repeating_sequence[(i - 1) % sequence_length] for i in fractions]

    for start_digit in starting_digits:
        movement = minimal_movement(starting_digit, start_digit, digit_positions, sequence_length)
        movements.append(movement)

    superposition_movement = sequence_length // 2
    movements.append(superposition_movement)
    fractions.append(n - 1)

    superposition_movements = [m for m in movements if abs(m) == superposition_movement]
    non_superposition_movements = [m for m in movements if abs(m) != superposition_movement]
    net_movement = sum(non_superposition_movements)

    print("Movements:", movements)
    print("Superposition Movements:", superposition_movements)
    print("Net Overall Movement:", net_movement)

    fig, ax = plt.subplots(figsize=(12, 6))

    for idx, (m) in enumerate(movements):
        fraction_label = f"{fractions[idx]}/{n}"
        if abs(m) == superposition_movement:
            ax.plot([0, -m], [idx, idx], 'purple', linestyle='dotted', label=fraction_label if idx == 0 else "")
            ax.plot([0, m], [idx, idx], 'purple', linestyle='dotted')
        else:
            color = 'blue' if m > 0 else 'red' if m < 0 else 'green'
            ax.plot([0, m], [idx, idx], marker='o', color=color, label=fraction_label if idx == 0 else "")

    ax.set_yticks(range(len(fractions)))
    ax.set_yticklabels([f'{i}/{n}' for i in fractions])

    ax.set_xticks(range(-sequence_length, sequence_length + 1))
    ax.set_xticklabels(range(-sequence_length, sequence_length + 1))

    secax = ax.secondary_xaxis('bottom')
    sequence_ticks = list(range(-sequence_length, sequence_length + 1))
    cyclic_labels = list(repeating_sequence) * (len(sequence_ticks) // len(repeating_sequence) + 1)
    cyclic_labels = cyclic_labels[:len(sequence_ticks)]
    secax.set_xticks(sequence_ticks)
    secax.set_xticklabels(cyclic_labels)

    secax.spines['bottom'].set_position(('outward', 40))

    ax.legend()
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.grid(color='gray', linestyle='--', linewidth=0.5)
    ax.set_title(f'Minimal Movements for Cyclic Prime {n}')
    ax.set_xlabel('Movement on Dial')
    ax.set_ylabel(f'Fraction n/{n}')

    plt.show()

# Example usage
cyclic_prime = int(input("Enter a cyclic prime number: "))
visualize_cyclic_prime(cyclic_prime)
