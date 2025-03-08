# sign_local.py
import sys
import hashlib
from ecdsa import SigningKey, SECP256k1

def main():
    # Verificamos que se hayan pasado dos parámetros: la clave privada y el mensaje
    if len(sys.argv) != 3:
        print("Uso: python sign_local.py <PRIVATE_KEY_HEX> <MENSAJE>")
        sys.exit(1)
    
    private_key_hex = sys.argv[1]
    message = sys.argv[2]

    # Convertimos la clave privada de hex a bytes y creamos la firma
    sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
    signature = sk.sign(message.encode('utf-8'), hashfunc=hashlib.sha256)

    # Mostramos la firma en hex
    print("Firma (hex):", signature.hex())

if __name__ == "__main__":
    main()

