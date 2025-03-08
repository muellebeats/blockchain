import hashlib
from ecdsa import SigningKey, SECP256k1

def generar_usuario():
    # 1. Generamos la clave privada y la pública
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.verifying_key
    
    private_key_hex = sk.to_string().hex()
    public_key_hex = vk.to_string().hex()
    
    # 2. Derivamos el user_id con SHA-256 sobre la clave pública
    user_id = hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()
    # Opcionalmente, podrías quedarte con los primeros 8-10 caracteres, según prefieras.
    
    # 3. Retornamos todo lo necesario
    return {
        "private_key": private_key_hex,
        "public_key": public_key_hex,
        "user_id": user_id
    }

if __name__ == "__main__":
    usuario = generar_usuario()
    print("Clave Privada:", usuario["private_key"])
    print("Clave Pública:", usuario["public_key"])
    print("User ID (hash de la clave pública):", usuario["user_id"])
