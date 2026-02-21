import os
from khan_cipher.core import encrypt, decrypt

print("="*50)
print("KHAN CIPHER - ENTERPRISE DEMONSTRATION")
print("="*50)

master_key = os.urandom(32)
print(f"Master Key (256-bit): {master_key.hex()}")

plaintext = b"CONFIDENTIAL: Cloudflare Edge Node routing tables update. Payload highly sensitive."
print(f"\n[+] Plaintext: {plaintext.decode()}")

payload = encrypt(plaintext, master_key)

salt = payload[:16]
iv = payload[16:32]
# Ciphertext is everything except salt(16), iv(16), and mac(32)
ciphertext = payload[32:-32]
mac = payload[-32:]

print(f"[+] Generated Salt: {salt.hex()}")
print(f"[+] Generated IV: {iv.hex()}")
print(f"[+] Ciphertext: {ciphertext.hex()}")
print(f"[i] Total Payload Size: {len(payload)} bytes")

decrypted = decrypt(payload, master_key)
print(f"\n[+] Decrypted Text: {decrypted.decode()}")

assert plaintext == decrypted, "DECRYPTION FAILED!"
print("\n[SUCCESS] Symmetric encryption and decryption cycle mathematically verified.")
