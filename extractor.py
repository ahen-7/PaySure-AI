import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)


def extract_payment_details(file_bytes, mime_type):

    prompt = """
You are PaySure AI, a payment verification assistant.

Analyze this invoice or payment request.

Extract:

1. merchant_name
2. amount
3. currency
4. invoice_id
5. purpose
6. due_date
7. payment_identifier

Return ONLY valid JSON:

{
    "merchant_name": null,
    "amount": null,
    "currency": null,
    "invoice_id": null,
    "purpose": null,
    "due_date": null,
    "payment_identifier": null
}

If information is not present, use null.
Do not guess missing information.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": file_bytes
                    }
                },
                prompt
            ]
        )

        return response.text

    except errors.ClientError as e:

        if e.code == 429:
            raise RuntimeError(
                "AI verification is temporarily unavailable "
                "because the Gemini API request limit has been reached. "
                "Please try again later."
            )

        raise RuntimeError(
            f"Gemini API error: {e}"
        )


def verify_payment(invoice_data, requested_amount, requested_merchant):

    prompt = f"""
You are PaySure AI.

Compare the invoice information with the user's payment request.

INVOICE:
{invoice_data}

PAYMENT REQUEST:
Merchant: {requested_merchant}
Amount: ₹{requested_amount}

Determine whether there are important mismatches.

Check:
- amount
- merchant name
- invoice information
- suspicious unexplained differences

Return ONLY valid JSON:

{{
    "status": "VERIFIED" or "REVIEW REQUIRED",
    "risk": "LOW" or "MEDIUM" or "HIGH",
    "reasons": []
}}

Do not call something fraudulent merely because there is a mismatch.
Explain the specific inconsistency.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except errors.ClientError as e:

        if e.code == 429:
            raise RuntimeError(
                "AI verification is temporarily unavailable "
                "because the Gemini API request limit has been reached. "
                "Please try again later."
            )

        raise RuntimeError(
            f"Gemini API error: {e}"
        )