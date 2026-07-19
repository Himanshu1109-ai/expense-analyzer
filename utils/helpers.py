# ---------------- HELPERS ----------------
import importlib
import re
from datetime import datetime

pdfplumber = None
if importlib.util.find_spec("pdfplumber") is not None:
    pdfplumber = importlib.import_module("pdfplumber")

def extract_text_from_pdf(file):
    if pdfplumber is None:
        raise ImportError("pdfplumber is not installed. Install it with pip install pdfplumber")
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text


def extract_amount(text):
    match = re.search(r'(\d+[.,]?\d*)', text)
    return float(match.group(1)) if match else 0


def extract_merchant(text):
    lines = text.split("\n")
    return lines[0] if lines else "Unknown"


def categorize(merchant):
    merchant = merchant.lower()

    if any(x in merchant for x in ["zomato", "swiggy", "restaurant"]):
        return "Food"
    elif any(x in merchant for x in ["uber", "ola"]):
        return "Travel"
    elif any(x in merchant for x in ["amazon", "flipkart"]):
        return "Shopping"
    elif any(x in merchant for x in ["electric", "bill", "recharge", "jio", "airtel"]):
        return "Bills"
    else:
        return "Other"


def save_transaction(amount, merchant, category, cursor, conn):
    cursor.execute("""
    INSERT INTO transactions (amount, merchant, category, date)
    VALUES (?, ?, ?, ?)
    """, (amount, merchant, category, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
