import streamlit as st
import streamlit.components.v1 as components
import os
import json
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PaySure",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background-color: #f7f8fa;
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 35px;
        padding-bottom: 60px;
    }


    /* ======================================================
       FORCE DARK TEXT
       ====================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: #1a1f36 !important;
    }

    p {
        color: #1a1f36 !important;
    }

    label {
        color: #1a1f36 !important;
    }

    [data-testid="stWidgetLabel"] {
        color: #1a1f36 !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: #1a1f36 !important;
    }

    .stMarkdown {
        color: #1a1f36 !important;
    }

    .stMarkdown p {
        color: #1a1f36 !important;
    }

    .stCaption {
        color: #4f566b !important;
    }

    .stText {
        color: #1a1f36 !important;
    }


    /* ======================================================
       HEADER
       ====================================================== */

    .brand {
        font-size: 32px;
        font-weight: 700;
        color: #1a1f36 !important;
        letter-spacing: -0.8px;
        margin-bottom: 5px;
    }

    .tagline {
        font-size: 15px;
        color: #4f566b !important;
        margin-bottom: 30px;
    }


    /* ======================================================
       INPUTS
       ====================================================== */

    input {
        color: #1a1f36 !important;
    }

    textarea {
        color: #1a1f36 !important;
    }

    [data-baseweb="input"] {
        color: #1a1f36 !important;
    }

    [data-baseweb="input"] input {
        color: #1a1f36 !important;
    }


    /* ======================================================
       FILE UPLOADER
       ====================================================== */

    [data-testid="stFileUploader"] {
        background-color: white;
        border: 1px dashed #c7ced8;
        border-radius: 10px;
        padding: 12px;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        width: 100%;
        height: 46px;
        border-radius: 7px;
        border: none;
        background-color: #528ff0;
        color: white !important;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #3d7fe5;
        color: white !important;
    }


    /* ======================================================
       SUCCESS
       ====================================================== */

    .verified-box {
        background: #f0faf5;
        border: 1px solid #b7e4ce;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .verified-title {
        color: #0b6b43 !important;
        font-size: 20px;
        font-weight: 700;
    }

    .verified-text {
        color: #315d4b !important;
        font-size: 14px;
        margin-top: 6px;
    }


    /* ======================================================
       REVIEW
       ====================================================== */

    .review-box {
        background: #fff8ed;
        border: 1px solid #f2d29c;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .review-title {
        color: #9a5b00 !important;
        font-size: 20px;
        font-weight: 700;
    }

    .review-text {
        color: #725321 !important;
        font-size: 14px;
        margin-top: 6px;
    }


    /* ======================================================
       HIGH RISK
       ====================================================== */

    .danger-box {
        background: #fff2f2;
        border: 1px solid #efb5b5;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .danger-title {
        color: #b42318 !important;
        font-size: 20px;
        font-weight: 700;
    }

    .danger-text {
        color: #7a271a !important;
        font-size: 14px;
        margin-top: 6px;
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {
        text-align: center;
        color: #8792a2 !important;
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
    '<div class="brand">PaySure</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tagline">Know your merchant before you pay</div>',
    unsafe_allow_html=True
)


# ============================================================
# MERCHANT INPUT
# ============================================================

st.header("Check a merchant before paying")

st.write(
    "Analyze publicly available merchant information and identify "
    "potential trust and fraud signals before making a payment."
)


merchant_name = st.text_input(
    "Merchant / Seller",
    placeholder="e.g. ABC Fashion Store"
)


merchant_url = st.text_input(
    "Website or Instagram URL",
    placeholder="https://example.com"
)


payment_amount = st.number_input(
    "Amount you intend to pay",
    min_value=0.0,
    step=1.0,
    format="%.2f"
)


# ============================================================
# ANALYZE MERCHANT
# ============================================================

if st.button("Analyze Merchant"):

    if not merchant_name.strip():

        st.warning(
            "Please enter the merchant or seller name."
        )

    elif not merchant_url.strip():

        st.warning(
            "Please enter the merchant website or Instagram URL."
        )

    elif payment_amount <= 0:

        st.warning(
            "Please enter a valid payment amount."
        )

    elif not GEMINI_API_KEY:

        st.error(
            "Gemini API key is not configured."
        )

    else:

        with st.spinner(
            "Analyzing merchant trust signals..."
        ):

            try:

                client = genai.Client(
                api_key=GEMINI_API_KEY
)

            except Exception as e:

                st.error(
                    f"Unable to initialize Gemini client: {e}"
                )

                st.stop()

prompt = f"""
You are PaySure's merchant risk analysis engine.

The user wants to know whether they should trust this merchant
before making a payment.

Merchant:
{merchant_name}

Website / social profile:
{merchant_url}

Amount:
₹{payment_amount}

Research this merchant using current PUBLIC information on the web.

Look specifically for:
1. How long the business appears to have existed.
2. Official website / business presence.
3. Customer reviews and reputation signals.
4. Scam, fraud, complaint, or warning reports.
5. Consistency of business/contact information.
6. Any suspicious patterns or red flags.
7. Whether the available evidence is sufficient or limited.

IMPORTANT:
- Use actual information found through Google Search.
- Do NOT invent facts.
- Do NOT assume a merchant is trustworthy merely because a website exists.
- Do NOT claim certainty that a merchant is legitimate or fraudulent.
- Clearly distinguish evidence from missing information.
- Base the trust score on the strength and quality of available evidence.

Return ONLY valid JSON:

{{
    "trust_score": 0,
    "risk": "LOW",
    "merchant_summary": "Short evidence-based summary",
    "positive_signals": [
        "Evidence-based signal"
    ],
    "warning_signals": [
        "Evidence-based warning"
    ],
    "recommendation": "Practical recommendation",
    "sources": [
        {{
            "title": "Source title",
            "url": "https://example.com"
        }}
    ]
}}

trust_score must be an integer from 0 to 100.

risk must be exactly one of:
LOW
MEDIUM
HIGH
"""

response = client.models.generate_content(
    model="gemini-3.7-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                google_search=types.GoogleSearch()
            )
        ]
    )
)

raw_result = response.text.strip()
# ============================================================
# MERCHANT RESULT
# ============================================================

if "merchant_analysis" in st.session_state:

    analysis = st.session_state[
        "merchant_analysis"
    ]


    score = analysis.get(
        "trust_score",
        0
    )

    risk = analysis.get(
        "risk",
        "MEDIUM"
    )

    summary = analysis.get(
        "merchant_summary",
        "No summary available."
    )

    positive_signals = analysis.get(
        "positive_signals",
        []
    )

    warning_signals = analysis.get(
        "warning_signals",
        []
    )

    recommendation = analysis.get(
        "recommendation",
        "Review the available information before paying."
    )


    st.divider()

    st.header(
        "Merchant Trust Assessment"
    )


    # ========================================================
    # LOW RISK
    # ========================================================

    if risk == "LOW":

        st.success(
            "LOW RISK — Merchant appears trustworthy"
        )

        st.write(
            "PaySure found generally positive trust signals "
            "based on the available information."
        )


    # ========================================================
    # MEDIUM RISK
    # ========================================================

    elif risk == "MEDIUM":

        st.warning(
            "CAUTION — Review before paying"
        )

        st.write(
            "PaySure found some signals that require "
            "additional caution."
        )


    # ========================================================
    # HIGH RISK
    # ========================================================

    else:

        st.error(
            "HIGH RISK — Payment not recommended"
        )

        st.write(
            "PaySure detected potentially concerning signals "
            "associated with this merchant."
        )


    # ========================================================
    # SCORE
    # ========================================================

    st.subheader(
        "Trust Score"
    )

    st.metric(
        "Merchant Trust Score",
        f"{score}/100"
    )

    st.caption(
        f"Risk level: {risk}"
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    st.subheader(
        "Assessment"
    )

    st.write(
        summary
    )


    # ========================================================
    # POSITIVE SIGNALS
    # ========================================================

    if positive_signals:

        st.subheader(
            "Positive signals"
        )

        for signal in positive_signals:

            st.write(
                f"✓ {signal}"
            )


    # ========================================================
    # WARNING SIGNALS
    # ========================================================

    if warning_signals:

        st.subheader(
            "Warning signals"
        )

        for signal in warning_signals:

            st.write(
                f"⚠ {signal}"
            )


    # ========================================================
    # RECOMMENDATION
    # ========================================================

    st.subheader(
        "PaySure Recommendation"
    )

    st.write(
        recommendation
    )


    # ========================================================
    # PAYMENT
    # ========================================================

    st.divider()

    if risk == "HIGH":

        st.error(
            "Payment is paused because the merchant has been "
            "classified as high risk."
        )

    else:

        st.subheader(
            "Proceed to payment"
        )

        st.write(
            "PaySure has completed the merchant assessment. "
            "You can continue to Razorpay if you choose to proceed."
        )


        if st.button(
            "Continue to payment"
        ):

            with st.spinner(
                "Preparing secure payment..."
            ):

                try:

                    response = requests.post(
                        "http://127.0.0.1:8000/create-order",
                        params={
                            "amount": st.session_state[
                                "payment_amount"
                            ]
                        },
                        timeout=10
                    )


                    response.raise_for_status()

                    order = response.json()


                    st.session_state[
                        "razorpay_order"
                    ] = order


                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Unable to create payment order: {e}"
                    )

                except Exception as e:

                    st.error(
                        f"Unable to create payment order: {e}"
                    )


# ============================================================
# RAZORPAY CHECKOUT
# ============================================================

if "razorpay_order" in st.session_state:

    order = st.session_state[
        "razorpay_order"
    ]


    order_id = order.get(
        "id"
    )

    amount = order.get(
        "amount"
    )


    if not RAZORPAY_KEY_ID:

        st.error(
            "Razorpay Key ID is not configured."
        )

    else:

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

                    "key": "{RAZORPAY_KEY_ID}",

                    "amount": "{amount}",

                    "currency": "INR",

                    "name": "PaySure",

                    "description": "Merchant verified by PaySure",

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
            height=320
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">PaySure · AI-powered merchant risk verification · Test Mode</div>',
    unsafe_allow_html=True
)
