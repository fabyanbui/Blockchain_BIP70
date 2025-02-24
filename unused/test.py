import streamlit as st
import hashlib
import json
import sqlite3
from datetime import datetime

# Kết nối SQLite để lưu tài khoản người dùng
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Tạo bảng nếu chưa có
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    balance REAL NOT NULL
)
""")
conn.commit()

# Class định nghĩa Block trong Blockchain
class Block:
    def __init__(self, index, previous_hash, transactions, timestamp):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "timestamp": self.timestamp
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

# Class Blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", [], str(datetime.utcnow()))
        self.chain.append(genesis_block)

    def add_transaction(self, sender, recipient, amount):
        if sender == recipient:
            return False
        transaction = {"sender": sender, "recipient": recipient, "amount": amount}
        self.pending_transactions.append(transaction)
        return True

    def mine_block(self):
        if not self.pending_transactions:
            return None
        last_block = self.chain[-1]
        new_block = Block(len(self.chain), last_block.hash, self.pending_transactions, str(datetime.utcnow()))
        self.chain.append(new_block)
        self.pending_transactions = []  # Xóa danh sách giao dịch sau khi block được tạo
        return new_block

# Tạo Blockchain
blockchain = Blockchain()

# Giao diện Streamlit
st.title("🌍 Blockchain Mini App")

# Quản lý phiên đăng nhập
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Đăng ký người dùng mới
def register_user(username):
    try:
        cursor.execute("INSERT INTO users (username, balance) VALUES (?, ?)", (username, 1000))  # Mặc định 1000 coin
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Lấy danh sách người dùng
def get_users():
    cursor.execute("SELECT username FROM users")
    return [row[0] for row in cursor.fetchall()]

# Cập nhật số dư tài khoản
def update_balance(username, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, username))
    conn.commit()

# Lấy số dư người dùng
def get_balance(username):
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] if result else 0

# Giao diện đăng nhập / đăng ký
if not st.session_state.logged_in:
    st.subheader("🔑 Đăng nhập / Đăng ký")
    username_input = st.text_input("Nhập tên người dùng")

    if st.button("Đăng ký"):
        if username_input:
            if register_user(username_input):
                st.success("Đăng ký thành công! Bây giờ bạn có thể đăng nhập.")
            else:
                st.error("Tên người dùng đã tồn tại!")
        else:
            st.error("Vui lòng nhập tên hợp lệ!")

    if st.button("Đăng nhập"):
        if username_input in get_users():
            st.session_state.logged_in = True
            st.session_state.username = username_input
            st.success(f"Chào mừng {username_input}!")
            st.experimental_rerun()
        else:
            st.error("Tài khoản không tồn tại!")

# Khi đã đăng nhập
if st.session_state.logged_in:
    st.subheader(f"👋 Xin chào, {st.session_state.username}")
    st.write(f"💰 Số dư: **{get_balance(st.session_state.username)} coins**")

    # Hiển thị danh sách người dùng
    st.subheader("📜 Danh sách người dùng")
    all_users = get_users()
    st.write(", ".join(all_users))

    # Gửi giao dịch
    st.subheader("📨 Gửi giao dịch")
    recipient = st.selectbox("Chọn người nhận", [user for user in all_users if user != st.session_state.username])
    amount = st.number_input("Số tiền", min_value=0.01, step=0.01)

    if st.button("Gửi tiền"):
        if get_balance(st.session_state.username) >= amount:
            if blockchain.add_transaction(st.session_state.username, recipient, amount):
                update_balance(st.session_state.username, -amount)
                update_balance(recipient, amount)
                st.success(f"Chuyển {amount} coins đến {recipient} thành công!")
            else:
                st.error("Không thể gửi tiền cho chính mình!")
        else:
            st.error("Số dư không đủ!")

    # Đào block
    if st.button("⛏️ Đào block"):
        new_block = blockchain.mine_block()
        if new_block:
            st.success(f"Block #{new_block.index} đã được tạo!")
        else:
            st.warning("Không có giao dịch nào để đào!")

    st.subheader("📜 Blockchain")
    for block in blockchain.chain:
        st.write(f"### Block #{block.index}")
        st.write(f"🕒 Timestamp: {block.timestamp}")
        st.write(f"🔗 Previous Hash: `{block.previous_hash}`")
        st.write(f"🔑 Hash: `{block.hash}`")
        
        st.write("📜 Transactions:")
        if block.transactions:
            st.json(block.transactions)  # Hiển thị danh sách giao dịch dưới dạng JSON
        else:
            st.write("🚫 Không có giao dịch nào trong block này.")

        st.write("---")


    # Nút đăng xuất
    if st.button("🚪 Đăng xuất"):
        st.session_state.logged_in = False
        st.experimental_rerun()
