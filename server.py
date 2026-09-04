from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from payment import (
    create_order,
    verify_payment_signature
)


app = FastAPI(
    title="PaySure Payment Server"
)


# Allow our Streamlit app to communicate
# with this local backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Orders created by our server.
# This lets us verify the original order ID
# rather than trusting a browser-provided order ID.
orders = set()


class PaymentVerificationRequest(BaseModel):

    payment_id: str
    order_id: str
    signature: str


@app.get("/")
def home():

    return {
        "status": "PaySure payment server running"
    }


@app.post("/create-order")
def create_payment_order(amount: float):

    order = create_order(amount)

    orders.add(order["id"])

    return {
        "id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"]
    }


@app.post("/verify-payment")
def verify_payment(data: PaymentVerificationRequest):

    # The order must have been created by our server.
    if data.order_id not in orders:

        return {
            "verified": False,
            "message": "Unknown order."
        }


    verified = verify_payment_signature(
        data.order_id,
        data.payment_id,
        data.signature
    )


    if verified:

        return {
            "verified": True,
            "message": "Payment signature verified."
        }


    return {
        "verified": False,
        "message": "Payment signature verification failed."
    }