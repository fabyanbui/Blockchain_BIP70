import time
import hashlib
import json
import base64

class PaymentRequest:
    def __init__(self, merchant, amount, memo=""):
        self.merchant = merchant
        self.amount = amount
        self.memo = memo
        self.timestamp = int(time.time())
        self.payment_request_id = self.generate_id()

    def generate_id(self):
        data = f"{self.merchant}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self):
        return {
            "merchant": self.merchant,
            "amount": self.amount,
            "memo": self.memo,
            "timestamp": self.timestamp,
            "payment_request_id": self.payment_request_id,
        }

    def to_base64(self):
        return base64.b64encode(json.dumps(self.to_dict()).encode()).decode()

    @staticmethod
    def from_base64(data):
        decoded = json.loads(base64.b64decode(data).decode())
        return PaymentRequest(
            merchant=decoded["merchant"],
            amount=decoded["amount"],
            memo=decoded["memo"],
        )
