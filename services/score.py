"""Score computation helpers."""
from typing import Dict, Any

def compute_score(conn, income: float) -> Dict[str, Any]:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    row = cursor.fetchone()
    if not row or row[0] == 0:
        return {"score": 0, "total_spent": 0.0, "savings": income}

    cursor.execute("SELECT SUM(amount) FROM transactions")
    total_spent = float(cursor.fetchone()[0] or 0.0)

    savings = income - total_spent
    ratio = savings / income if income > 0 else 0

    if ratio > 0.4:
        score = 90
    elif ratio > 0.2:
        score = 70
    else:
        score = 40

    return {"total_spent": total_spent, "savings": savings, "score": score}