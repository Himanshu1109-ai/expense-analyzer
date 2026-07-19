import re
from typing import Dict, Any

from services.categorizer import categorize
from database.db import save_transaction


def parse_sms_payload(payload: Dict[str, Any]):
    """Parse SMS JSON payload and persist transaction.

    Expects a dict with key `sms`.
    Returns a dict with parsed fields.
    """
    sms = payload.get("sms", "")

    amount_match = re.search(r"(\d+(?:\.\d+)?)", sms)
    merchant_match = re.search(r"to ([A-Za-z\s]+)", sms)

    amount = float(amount_match.group(1)) if amount_match else 0.0
    merchant = merchant_match.group(1).strip() if merchant_match else "Unknown"
    category = categorize(merchant)

    save_transaction(amount, merchant, category)

    return {"merchant": merchant, "amount": amount, "category": category}
