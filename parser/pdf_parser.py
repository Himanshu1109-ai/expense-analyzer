import importlib
import re

_pdf_reader_module = None
if importlib.util.find_spec("pypdf") is not None:
    _pdf_reader_module = importlib.import_module("pypdf")
elif importlib.util.find_spec("PyPDF2") is not None:
    _pdf_reader_module = importlib.import_module("PyPDF2")
else:
    raise ImportError("Install pypdf or PyPDF2 to use pdf_parser")

PdfReader = _pdf_reader_module.PdfReader

from services.categorizer import categorize
from database.db import save_transaction

def parse_pdf(file_path):
    """
    Parse a PDF file and extract transaction details.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        list: List of dictionaries containing transaction data
    """
    transactions = []
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Extract amounts (pattern: numbers with decimal points)
                amounts = re.findall(r'₹?\s?(\d+(?:\.\d{2})?)', text)
                
                # Extract merchant names (pattern: text after 'to' or similar keywords)
                merchants = re.findall(r'(?:to|at|from)\s+([A-Za-z\s]+)', text, re.IGNORECASE)
                
                # Pair amounts with merchants
                for i, (amount, merchant) in enumerate(zip(amounts, merchants)):
                    if merchant.strip() and amount:
                        amount_float = float(amount)
                        merchant_clean = merchant.strip()
                        category = categorize(merchant_clean)
                        
                        transaction = {
                            "amount": amount_float,
                            "merchant": merchant_clean,
                            "category": category,
                            "page": page_num + 1
                        }
                        
                        transactions.append(transaction)
                        # Save to database
                        save_transaction(amount_float, merchant_clean, category)
        
        return transactions
    
    except FileNotFoundError:
        print(f"Error: PDF file not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error parsing PDF: {str(e)}")
        return []
