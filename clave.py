from ecdsa import SigningKey, SECP256k1

sk = SigningKey.generate(curve=SECP256k1)
private_key_hex = sk.to_string().hex()
public_key_hex = sk.verifying_key.to_string().hex()

print("Clave privada (hex):", private_key_hex)  # 64 caracteres
print("Clave pública (hex):", public_key_hex)    # 128 caracteres
