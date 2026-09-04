import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

key_id = os.getenv("RAZORPAY_KEY_ID")
key_secret = os.getenv("RAZORPAY_KEY_SECRET")

if not key_id or not key_secret:
    raise ValueError("Razorpay credentials are missing from .env")

client = razorpay.Client(
    auth=(key_id, key_secret)
)


def create_order(amount):

    order = client.order.create(
        data={
            "amount": int(amount * 100),
            "currency": "INR",
            "receipt": "paysure_demo"
        }
    )

    return order


def verify_payment_signature(
    order_id,
    payment_id,
    signature
):

    try:

        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            }
        )

        return True

    except Exception:

        return False