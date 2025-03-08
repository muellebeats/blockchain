from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
import hashlib
import json
from time import time
from ecdsa import VerifyingKey, SECP256k1, BadSignatureError

app = Flask(__name__)

# Variable global para guardar la clave pública registrada
registered_key = None

# -----------------------------
# BLOQUES Y BLOCKCHAIN
# -----------------------------
class ChatBlock:
    def __init__(self, index, timestamp, content, block_type, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.content = content
        self.block_type = block_type
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "content": self.content,
            "block_type": self.block_type,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty):
        prefix = '0' * difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.compute_hash()
        return self.hash

class ChatBlockchain:
    def __init__(self, difficulty=2):
        self.chain = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = ChatBlock(
            index=0,
            timestamp=time(),
            content="Bloque Génesis",
            block_type="system",
            previous_hash="0"
        )
        genesis_block.mine(self.difficulty)
        self.chain.append(genesis_block)

    def add_message(self, content, block_type="chat"):
        previous_block = self.chain[-1]
        new_block = ChatBlock(
            index=previous_block.index + 1,
            timestamp=time(),
            content=content,
            block_type=block_type,
            previous_hash=previous_block.hash
        )
        new_block.mine(self.difficulty)
        self.chain.append(new_block)
        return new_block

    def get_chain(self):
        chain_data = []
        for block in self.chain:
            block_dict = block.__dict__.copy()
            readable_time = datetime.fromtimestamp(block_dict["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
            block_dict["readable_timestamp"] = readable_time
            chain_data.append(block_dict)
        return chain_data

chat_chain = ChatBlockchain()

# -----------------------------
# RUTAS
# -----------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign')
def sign():
    return render_template('sign.html')

@app.route('/genz')
def genz():
    return render_template('genz.html')

@app.route('/getchain')
def getchain():
    chain_data = chat_chain.get_chain()
    return render_template('chain_template.html', chain=chain_data)

@app.route('/chain', methods=['GET'])
def show_chain_json():
    return jsonify(chat_chain.get_chain())

@app.route('/form_register')
def form_register():
    return render_template('register.html')

@app.route('/sign_message', methods=['POST'])
def sign_message():
    # Aquí puedes agregar la lógica para firmar en el navegador, si la necesitas.
    pass

@app.route('/form_send_message')
def form_send_message():
    return render_template('send_message.html')

@app.route('/register', methods=['POST'])
def register():
    global registered_key
    public_key_hex = request.form.get('public_key')
    if not public_key_hex:
        return render_template('error.html', error="Falta parámetro 'public_key'"), 400
    try:
        VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
    except Exception:
        return render_template('error.html', error="Clave pública inválida"), 400
    registered_key = public_key_hex
    return redirect(url_for('form_send_message'))

@app.route('/send_message', methods=['POST'])
def send_message():
    global registered_key
    
    # 1. Obtenemos los datos del formulario, incluyendo user_id
    user_id = request.form.get('user_id')
    content = request.form.get('content')
    signature_hex = request.form.get('signature')
    
    # 2. Verificamos que no falte nada
    if not user_id or not content or not signature_hex:
        return render_template('error.html', error="Faltan parámetros (user_id, content, signature)"), 400
    if not registered_key:
        return render_template('error.html', error="No hay clave pública registrada"), 400

    # 3. Verificamos la firma
    try:
        vk = VerifyingKey.from_string(bytes.fromhex(registered_key), curve=SECP256k1)
        
        # Opcional: si el usuario está firmando "UserID + content" en el frontend,
        # aquí deberías verificar esa misma cadena EXACTA:
        # combined_message = f"UserID: {user_id}\nContent: {content}"
        # vk.verify(bytes.fromhex(signature_hex), combined_message.encode('utf-8'), hashfunc=hashlib.sha256)
        
        # Pero si solo firma 'content', lo dejamos tal cual:
        vk.verify(bytes.fromhex(signature_hex), content.encode('utf-8'), hashfunc=hashlib.sha256)
        
    except BadSignatureError:
        return render_template('error.html', error="Firma inválida (BadSignatureError)"), 400
    except Exception as e:
        return render_template('error.html', error=f"Error al verificar la firma: {str(e)}"), 400
    
    # 4. Guardamos en la cadena (puedes añadir user_id al 'content' si lo deseas)
    final_content = f"[UserID={user_id}] {content}"
    chat_chain.add_message(final_content, block_type="chat")
    
    # 5. Redirigimos para ver la cadena
    return redirect(url_for('getchain'))

@app.route('/error')
def error_page():
    return render_template('error.html', error="Ha ocurrido un error")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
