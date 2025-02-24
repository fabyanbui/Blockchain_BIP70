import hashlib
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Blockchain lưu các blocks
blockchain = []
peers = []

# Hàm tạo block mới
def create_block(previous_hash):
    block = {
        'index': len(blockchain) + 1,
        'timestamp': str(datetime.utcnow()),
        'previous_hash': previous_hash,
        'data': f"Block {len(blockchain) + 1}",
        'hash': ''
    }
    block['hash'] = hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
    blockchain.append(block)
    return block

# Endpoint để lấy Blockchain
@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    return jsonify(blockchain)

# Endpoint để thêm block mới
@app.route('/mine', methods=['GET'])
def mine_block():
    previous_hash = blockchain[-1]['hash'] if blockchain else '0'
    block = create_block(previous_hash)
    
    # Broadcast block mới tới toàn bộ mạng
    for peer in peers:
        requests.post(f"http://{peer}/add_block", json=block)

    return jsonify(block)

# Nhận block từ các peers
@app.route('/add_block', methods=['POST'])
def add_block():
    block = request.json
    blockchain.append(block)
    return jsonify({"message": "Block added"}), 201

# Kết nối đến Flask Bootstrap Server để lấy danh sách peers
@app.route('/connect', methods=['POST'])
def connect():
    global peers
    response = requests.get("http://localhost:5000/peers")
    peers = [f"{peer_info['ip']}:{peer_info['port']}" for peer_info in response.json().values()]
    return jsonify({"message": "Connected to peers", "peers": peers})

if __name__ == '__main__':
    app.run(port=6000)
