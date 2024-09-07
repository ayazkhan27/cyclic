import importlib.util
import sys
from decimal import Decimal, getcontext

# Import the khan_encryption2 module from a specific path
module_name = "khan_encryption2"
file_path = "/home/zephyr27/Documents/GitHub/cyclic/khan_encryption_2.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
ke = importlib.util.module_from_spec(spec)
sys.modules[module_name] = ke
spec.loader.exec_module(ke)

def generate_cyclic_sequence(prime, length):
    getcontext().prec = length + 10
    decimal_expansion = str(Decimal(1) / Decimal(prime))[2:]
    return decimal_expansion[:length]

# Prize message encryption
prime = 1051
cyclic_sequence = generate_cyclic_sequence(prime, prime - 1)
plaintext = "ayaz"
start_position = 774
superposition_sequence_length = 75672

ciphertext, char_to_movement, movement_to_char, z_value, superposition_sequence, iv, salt, z_layers = ke.khan_encrypt(
    plaintext, prime, cyclic_sequence, start_position, superposition_sequence_length
)

encrypted_prize_message = ''.join(map(str, ciphertext))
print("Encrypted prize message:", encrypted_prize_message)
