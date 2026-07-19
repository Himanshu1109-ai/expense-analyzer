import sqlite3
from datetime import datetime
from typing import List, Dict
from models.transaction import Transaction

# ---------------- DATABASE ----------------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    merchant TEXT,
    category TEXT,
    date TEXT
)
""")
conn.commit()

def save_transaction(amount, merchant, category):
    """
    Save a transaction to the database.
    
    Args:
        amount (float): The expense amount
        merchant (str): The merchant/seller name
        category (str): The category of expense
    """
    cursor.execute("""
    INSERT INTO transactions (amount, merchant, category, date)
    VALUES (?, ?, ?, ?)
    """, (amount, merchant, category, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    return cursor.lastrowid


def get_transaction_by_id(tx_id: int) -> Dict:
    cursor.execute("SELECT id, amount, merchant, category, date FROM transactions WHERE id = ?", (tx_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Transaction.from_db_row(row).to_dict()


def update_transaction(tx_id: int, amount: float, merchant: str, category: str) -> bool:
    cursor.execute(
        "UPDATE transactions SET amount = ?, merchant = ?, category = ? WHERE id = ?",
        (amount, merchant, category, tx_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def delete_transaction(tx_id: int) -> bool:
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    return cursor.rowcount > 0


def get_all_transactions() -> List[Dict]:
    """Return all transactions as list of dicts."""
    cursor.execute("SELECT id, amount, merchant, category, date FROM transactions ORDER BY date DESC")
    rows = cursor.fetchall()
    return [Transaction.from_db_row(row).to_dict() for row in rows]


def get_total_spent() -> float:
    cursor.execute("SELECT SUM(amount) FROM transactions")
    result = cursor.fetchone()
    return float(result[0]) if result and result[0] is not None else 0.0
