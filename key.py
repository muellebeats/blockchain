from ecdsa import SigningKey, SECP256k1

# Generar la clave privada (SigningKey)
sk = SigningKey.generate(curve=SECP256k1)
# Obtener la clave pública (VerifyingKey)
vk = sk.verifying_key

# Convertir ambas a hexadecimal
private_key_hex = sk.to_string().hex()
public_key_hex = vk.to_string().hex()

print("Clave privada (hex):", private_key_hex)
print("Clave pública (hex):", public_key_hex)
