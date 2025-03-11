import streamlit as st
from blockchain import Blockchain
from bip70 import PaymentRequest
import time

# Khởi tạo Blockchain
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

blockchain = st.session_state.blockchain

# Khởi tạo biến trạng thái
if "payment_request" not in st.session_state:
    st.session_state.payment_request = None

if "payment_ack" not in st.session_state:
    st.session_state.payment_ack = None

if "customer_info" not in st.session_state:
    st.session_state.customer_info = {}

st.title("🔗 Mô phỏng Blockchain với BIP70")

# ============================
# 1️⃣ CUSTOMER NHẬP THÔNG TIN & NHẤN "PAY NOW"
# ============================
st.header("👤 Customer")
sender = st.text_input("👤 Người gửi:")
amount = st.number_input("💵 Số tiền yêu cầu:", min_value=0.01, format="%.2f")

if st.button("💳 Pay Now"):
    if sender and amount:
        st.session_state.customer_info = {"sender": sender, "amount": amount}
        st.session_state.payment_request = None  # Reset Payment Request
        st.session_state.payment_ack = None  # Reset PaymentACK
        st.session_state.pay_now_clicked = True
        st.success("✅ Đã gửi yêu cầu đến Merchant Server!")
    else:
        st.warning("⚠️ Vui lòng nhập đủ thông tin trước khi nhấn 'Pay Now'!")

# ============================
# 2️⃣ MERCHANT SERVER NHẬN YÊU CẦU VÀ GỬI PAYMENT REQUEST
# ============================
st.sidebar.header("🏦 Merchant Server")
merchant = st.sidebar.text_input("Tên Merchant:")
memo = st.sidebar.text_area("Mô tả giao dịch (tùy chọn)")

if st.sidebar.button("📩 Gửi Payment Request"):
    if merchant and st.session_state.get("pay_now_clicked", False) and st.session_state.customer_info:
        sender_info = st.session_state.customer_info
        payment_request = PaymentRequest(merchant, sender_info["amount"], memo)
        
        # Cập nhật Payment Request mới vào session
        st.session_state.payment_request = payment_request.to_base64()
        st.session_state.customer_info["merchant"] = merchant
        st.session_state.payment_request_id = hash(payment_request.to_base64())  # ID duy nhất cho Payment Request

        st.sidebar.success("✅ Payment Request đã được gửi!")
        st.sidebar.code(payment_request.to_base64(), language="plaintext")
    else:
        st.sidebar.warning("⚠️ Cần nhấn 'Pay Now' trước khi gửi Payment Request!")

# ============================
# 3️⃣ CUSTOMER XÁC NHẬN PAYMENT REQUEST
# ============================
if st.session_state.payment_request:
    st.header("📜 Xác nhận Payment Request")
    st.text("Dán Payment Request nhận được từ Merchant Server:")
    payment_request_input = st.text_area("📜 Payment Request:", value="")

    if st.button("✔ OK - Xác nhận thanh toán"):
        try:
            # Kiểm tra Payment Request có phải mới nhất không
            if payment_request_input != st.session_state.payment_request:
                st.error("❌ Payment Request không hợp lệ hoặc đã cũ! Giao dịch bị từ chối.")
            else:
                payment_request = PaymentRequest.from_base64(st.session_state.payment_request)
                sender = st.session_state.customer_info["sender"]
                amount_paid = st.session_state.customer_info["amount"]
                merchant = st.session_state.customer_info["merchant"]

                if amount_paid == payment_request.amount:
                    blockchain.add_transaction(sender, merchant, amount_paid)
                    st.session_state.payment_ack = f"✅ Giao dịch {amount_paid} BTC từ {sender} đến {merchant} thành công!"
                    st.success("✅ Thanh toán đã được xác nhận!")

                    # Sau khi thanh toán thành công, xóa Payment Request cũ để ngăn lạm dụng
                    st.session_state.payment_request = None
                    st.session_state.payment_request_id = None
                else:
                    st.warning("⚠️ Số tiền thanh toán không khớp với Payment Request!")
        except Exception as e:
            st.error(f"Lỗi xử lý Payment Request: {e}")

# ============================
# 4️⃣ MINING & CẬP NHẬT BLOCKCHAIN
# ============================
st.header("⛏️ Mining Block")
if st.button("🚀 Mine giao dịch"):
    blockchain.mine_pending_transactions()
    st.success("✅ Block mới đã được thêm vào blockchain!")

# ============================
# 5️⃣ MERCHANT NHẬN PAYMENTACK
# ============================
st.sidebar.header("📩 PaymentACK")
if st.session_state.payment_ack:
    st.sidebar.success(st.session_state.payment_ack)
    st.sidebar.text("📜 Optional message: Cảm ơn bạn đã thanh toán!")

# ============================
# 📜 HIỂN THỊ BLOCKCHAIN (ẨN INDEX HOÀN TOÀN)
# ============================
st.header("📜 Chuỗi Blockchain")
for i, block in enumerate(blockchain.get_chain(), start=1):
    with st.expander(f"🧱 Block #{i}"):
        st.write(f"📅 **Thời gian:** {time.ctime(block['timestamp'])}")
        st.write(f"🔗 **Hash:** {block['hash']}")
        st.write(f"🔗 **Previous Hash:** {block['previous_hash']}")
        st.write(f"📜 **Transactions:** {block['transactions']}")
        st.write(f"⚡ **Nonce:** {block['nonce']}")

