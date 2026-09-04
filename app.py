import streamlit as st
import streamlit.components.v1 as components
import json
import os
import requests


from extractor import (
    extract_payment_details,
    verify_payment
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PaySure",
    page_icon=None,
    layout="centered"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f7f8fa;
    }

    .main .block-container {
        max-width: 850px;
        padding-top: 35px;
        padding-bottom: 60px;
    }

    /* Brand */

    .brand-text {
        font-size: 32px;
        font-weight: 700;
        color: #1a1f36;
        letter-spacing: -0.8px;
    }

    .brand-subtitle {
        color: #4f566b;
        font-size: 15px;
        margin-bottom: 32px;
    }

    /* Headings */

    h1, h2, h3 {
        color: #1a1f36 !important;
    }

    /* Body */

    p {
        color: #4f566b;
    }

    /* Caption */

    .stCaption {
        color: #1a1f36 !important;
        font-size: 14px !important;
    }

    /* Buttons */

    .stButton > button {
        width: 100%;
        height: 45px;
        border-radius: 7px;
        border: none;
        background-color: #528ff0;
        color: white;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #3d7fe5;
        color: white;
    }

    /* Upload */

    [data-testid="stFileUploader"] {
        background-color: white;
        border: 1px dashed #c7ced8;
        border-radius: 10px;
        padding: 12px;
    }

    /* Information boxes */

    .info-card {
        background: white;
        border: 1px solid #e3e8ee;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .info-label {
        color: #697386;
        font-size: 12px;
        margin-bottom: 4px;
    }

    .info-value {
        color: #1a1f36;
        font-size: 16px;
        font-weight: 600;
    }

    /* Verification */

    .verified-card {
        background: #f0faf5;
        border: 1px solid #b7e4ce;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }

    .verified-title {
        color: #0b6b43;
        font-size: 20px;
        font-weight: 700;
    }

    .verified-description {
        color: #315d4b;
        font-size: 14px;
        margin-top: 6px;
    }

    .review-card {
        background: #fff8ed;
        border: 1px solid #f2d29c;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }

    .review-title {
        color: #9a5b00;
        font-size: 20px;
        font-weight: 700;
    }

    .review-description {
        color: #725321;
        font-size: 14px;
        margin-top: 6px;
    }

    /* Footer */

    .footer {
        text-align: center;
        color: #8792a2;
        font-size: 12px;
        margin-top: 45px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="brand-text">PaySure</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="brand-subtitle">AI-powered payment verification</div>',
    unsafe_allow_html=True
)


# ============================================================
# STEP 1 — UPLOAD
# ============================================================

st.header("Verify a payment")

st.write(
    "Upload an invoice or payment request to begin verification."
)


uploaded_file = st.file_uploader(
    "Upload document",
    type=["pdf", "png", "jpg", "jpeg"]
)


# ============================================================
# DOCUMENT ANALYSIS
# ============================================================

if uploaded_file:

    st.success("Document uploaded successfully.")

    if st.button("Analyze document"):

        with st.spinner("Analyzing document..."):

            try:

                file_bytes = uploaded_file.getvalue()

                extracted = extract_payment_details(
                    file_bytes,
                    uploaded_file.type
                )

                st.session_state["invoice_data"] = extracted

                # Clear previous verification/payment state
                st.session_state.pop(
                    "verification",
                    None
                )

                st.session_state.pop(
                    "razorpay_order",
                    None
                )

            except RuntimeError as e:

                st.error(str(e))
                st.stop()

            except Exception:

                st.error(
                    "Unable to analyze the document right now."
                )
                st.stop()


# ============================================================
# STEP 2 — EXTRACTED PAYMENT INFORMATION
# ============================================================

if "invoice_data" in st.session_state:

    st.divider()

    st.header("Extracted payment information")

    extracted = st.session_state["invoice_data"]

    try:

        cleaned_extracted = extracted.strip()

        # Remove markdown code fences if Gemini adds them
        if cleaned_extracted.startswith("```"):

            lines = cleaned_extracted.splitlines()

            lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned_extracted = "\n".join(lines).strip()

        payment_data = json.loads(cleaned_extracted)

        col1, col2 = st.columns(2)

        with col1:

            st.caption("Merchant")
            st.write(
                payment_data.get("merchant_name")
                or "Not available"
            )

            st.caption("Amount")

            invoice_amount = payment_data.get("amount")
            invoice_currency = (
                payment_data.get("currency")
                or "INR"
            )

            if invoice_amount is not None:

                st.write(
                    f"{invoice_currency} {invoice_amount}"
                )

            else:

                st.write("Not available")

            st.caption("Invoice ID")
            st.write(
                payment_data.get("invoice_id")
                or "Not available"
            )

        with col2:

            st.caption("Purpose")
            st.write(
                payment_data.get("purpose")
                or "Not available"
            )

            st.caption("Due date")
            st.write(
                payment_data.get("due_date")
                or "Not available"
            )

            st.caption("Payment identifier")
            st.write(
                payment_data.get("payment_identifier")
                or "Not available"
            )

    except json.JSONDecodeError:

        st.warning(
            "The extracted information could not be displayed as structured data."
        )

        st.code(
            extracted,
            language="json"
        )


# ============================================================
# STEP 3 — PAYMENT REQUEST
# ============================================================

if "invoice_data" in st.session_state:

    st.divider()

    st.header("Payment details")

    st.write(
        "Enter the details you were asked to pay."
    )


    requested_merchant = st.text_input(
        "Merchant / recipient",
        placeholder="e.g. ABC Academy"
    )


    requested_amount = st.number_input(
        "Amount",
        min_value=0.0,
        step=1.0,
        format="%.2f"
    )


    # ========================================================
    # VERIFY PAYMENT
    # ========================================================

    if st.button("Verify payment"):

        if not requested_merchant:

            st.warning(
                "Please enter the merchant or recipient."
            )

        elif requested_amount <= 0:

            st.warning(
                "Please enter a valid amount."
            )

        else:

            with st.spinner(
                "Checking payment details..."
            ):

                try:

                    result = verify_payment(
                        st.session_state["invoice_data"],
                        requested_amount,
                        requested_merchant
                    )

                except RuntimeError as e:

                    st.error(str(e))
                    st.stop()

                except Exception:

                    st.error(
                        "Unable to complete AI verification right now."
                    )
                    st.stop()


            # =================================================
            # PARSE AI RESPONSE
            # =================================================

            try:

                cleaned_result = result.strip()

                if cleaned_result.startswith("```"):

                    lines = cleaned_result.splitlines()

                    lines = lines[1:]

                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]

                    cleaned_result = "\n".join(lines).strip()


                verification = json.loads(
                    cleaned_result
                )


                st.session_state["verification"] = verification

                st.session_state[
                    "requested_amount"
                ] = requested_amount

                st.session_state.pop(
                    "razorpay_order",
                    None
                )


            except json.JSONDecodeError:

                st.error(
                    "AI returned an invalid verification response."
                )

                st.code(
                    result,
                    language="json"
                )


# ============================================================
# STEP 4 — VERIFICATION RESULT
# ============================================================

if "verification" in st.session_state:

    verification = st.session_state["verification"]

    status = verification.get(
        "status",
        ""
    )

    risk = verification.get(
        "risk",
        ""
    )

    reasons = verification.get(
        "reasons",
        []
    )


    st.divider()

    st.header("Verification result")


    # ========================================================
    # VERIFIED
    # ========================================================

    if status == "VERIFIED":

        st.markdown(
            """
            <div class="verified-card">
                <div class="verified-title">
                    Payment verified
                </div>

                <div class="verified-description">
                    The payment details are consistent with
                    the provided invoice.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


        st.caption("Risk level")

        st.write(
            f"**{risk}**"
        )


        if reasons:

            st.write(
                "Verification details"
            )

            for reason in reasons:

                st.write(
                    f"• {reason}"
                )


        st.divider()

        st.subheader("Payment")

        st.write(
            "Your payment has passed PaySure verification."
        )


        # ====================================================
        # CREATE PAYMENT ORDER
        # ====================================================

        if st.button(
            "Continue to payment"
        ):

            with st.spinner(
                "Preparing secure payment..."
            ):

                try:

                    response = requests.post(
                        "http://127.0.0.1:8000/create-order",
                        json={
                            "amount": st.session_state[
                                "requested_amount"
                            ]
                        },
                        timeout=10
                    )


                    response.raise_for_status()

                    order = response.json()


                    if not order.get("success"):

                        st.error(
                            order.get(
                                "message",
                                "Unable to create payment order."
                            )
                        )

                        st.stop()


                    st.session_state[
                        "razorpay_order"
                    ] = order


                except requests.exceptions.RequestException:

                    st.error(
                        "PaySure payment server is not running. "
                        "Start the server with: "
                        "uvicorn server:app --reload --port 8000"
                    )

                    st.stop()


    # ========================================================
    # REVIEW REQUIRED
    # ========================================================

    else:

        st.markdown(
            """
            <div class="review-card">

                <div class="review-title">
                    Payment requires review
                </div>

                <div class="review-description">
                    PaySure detected an inconsistency in
                    the payment details.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.caption("Risk level")

        st.write(
            f"**{risk}**"
        )


        if reasons:

            st.write(
                "Why was this flagged?"
            )

            for reason in reasons:

                st.write(
                    f"• {reason}"
                )


        st.warning(
            "Payment has been paused until the discrepancy is reviewed."
        )


# ============================================================
# STEP 5 — RAZORPAY CHECKOUT
# ============================================================

if "razorpay_order" in st.session_state:

    order = st.session_state[
        "razorpay_order"
    ]

    key_id = os.getenv(
        "RAZORPAY_KEY_ID"
    )

    order_id = order["id"]

    amount = order["amount"]


    st.divider()

    st.subheader(
        "Secure payment"
    )

    st.write(
        f"Amount: ₹{amount / 100:,.2f}"
    )


    checkout_html = f"""
    <html>

    <head>

        <script src="https://checkout.razorpay.com/v1/checkout.js">
        </script>

    </head>

    <body>

        <button
            id="rzp-button"
            style="
                width:100%;
                background:#528ff0;
                color:white;
                border:none;
                padding:13px;
                border-radius:7px;
                font-size:16px;
                font-weight:600;
                cursor:pointer;
            "
        >
            Continue to Razorpay
        </button>


        <div
            id="result"
            style="
                font-family:Arial;
                text-align:center;
                margin-top:15px;
            "
        >
        </div>


        <script>

            var options = {{

                "key": "{key_id}",

                "amount": "{amount}",

                "currency": "INR",

                "name": "PaySure",

                "description": "Verified payment",

                "order_id": "{order_id}",


                "prefill": {{

                    "name": "Test User",

                    "email": "test@example.com",

                    "contact": "+919000090000"

                }},


                "handler": async function(response) {{

                    var resultBox =
                        document.getElementById("result");


                    resultBox.innerHTML =
                        "<p style='color:#4f566b;'>"
                        + "Verifying payment..."
                        + "</p>";


                    try {{

                        const serverResponse =
                            await fetch(
                                "http://127.0.0.1:8000/verify-payment",
                                {{

                                    method: "POST",

                                    headers: {{
                                        "Content-Type":
                                            "application/json"
                                    }},

                                    body: JSON.stringify({{

                                        payment_id:
                                            response.razorpay_payment_id,

                                        order_id:
                                            response.razorpay_order_id,

                                        signature:
                                            response.razorpay_signature

                                    }})

                                }}
                            );


                        const result =
                            await serverResponse.json();


                        if (result.verified) {{

                            resultBox.innerHTML =
                                "<div style='" +
                                "background:#f0faf5;" +
                                "border:1px solid #b7e4ce;" +
                                "border-radius:10px;" +
                                "padding:20px;'>" +

                                "<h3 style='color:#0b6b43;'>"
                                + "Payment confirmed"
                                + "</h3>" +

                                "<p style='color:#315d4b;'>"
                                + "Razorpay payment signature verified successfully."
                                + "</p>" +

                                "<p style='color:#315d4b;'>"
                                + "Payment ID: "
                                + response.razorpay_payment_id
                                + "</p>" +

                                "</div>";

                        }} else {{

                            resultBox.innerHTML =
                                "<div style='" +
                                "background:#fff8ed;" +
                                "border:1px solid #f2d29c;" +
                                "border-radius:10px;" +
                                "padding:20px;'>" +

                                "<h3 style='color:#9a5b00;'>"
                                + "Payment verification failed"
                                + "</h3>" +

                                "<p style='color:#725321;'>"
                                + result.message
                                + "</p>" +

                                "</div>";

                        }}

                    }} catch (error) {{

                        resultBox.innerHTML =
                            "<div style='" +
                            "background:#fff8ed;" +
                            "border:1px solid #f2d29c;" +
                            "border-radius:10px;" +
                            "padding:20px;'>" +

                            "<h3 style='color:#9a5b00;'>"
                            + "Unable to verify payment"
                            + "</h3>" +

                            "<p style='color:#725321;'>"
                            + "PaySure could not contact the payment server."
                            + "</p>" +

                            "</div>";

                    }}

                }},


                "theme": {{

                    "color": "#528ff0"

                }}

            }};


            var rzp =
                new Razorpay(options);


            document.getElementById(
                "rzp-button"
            ).onclick = function(e) {{

                rzp.open();

                e.preventDefault();

            }};

        </script>

    </body>

    </html>
    """


    components.html(
        checkout_html,
        height=300
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">PaySure · AI-powered payment verification · Test Mode</div>',
    unsafe_allow_html=True
)