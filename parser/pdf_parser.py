import re

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError(
            "Please install pypdf or PyPDF2 using:\n"
            "pip install pypdf"
        )

from services.categorizer import categorize
from database.db import save_transaction


def parse_pdf(file_path):
    """
    Parse a PDF file and extract transaction details.
    """

    transactions = []

    try:
        with open(file_path, "rb") as file:

            pdf_reader = PdfReader(file)

            for page_num, page in enumerate(pdf_reader.pages):

                text = page.extract_text()

                if not text:
                    continue

                amounts = re.findall(r'₹?\s?(\d+(?:\.\d{2})?)', text)

                merchants = re.findall(
                    r'(?:to|at|from)\s+([A-Za-z\s]+)',
                    text,
                    re.IGNORECASE
                )

                for amount, merchant in zip(amounts, merchants):

                    merchant = merchant.strip()

                    amount = float(amount)

                    category = categorize(merchant)

                    save_transaction(
                        amount,
                        merchant,
                        category
                    )

                    transactions.append({
                        "amount": amount,
                        "merchant": merchant,
                        "category": category,
                        "page": page_num + 1
                    })

        return transactions

    except FileNotFoundError:
        print("PDF file not found.")
        return []

    except Exception as e:
        print("PDF Parsing Error:", e)
        return []