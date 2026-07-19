"""Insights helpers (pure functions)."""
from typing import Dict, Any

def compute_insights(conn) -> Dict[str, Any]:
    """Compute alert insights from a sqlite `conn`.

    Returns a dict suitable for JSON serialization.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) as total FROM transactions GROUP BY category")
    rows = cursor.fetchall()

    if not rows:
        return {"message": "No data"}

    category_sum = {category: total for category, total in rows}
    if not category_sum:
        return {"message": "No data"}

    avg = sum(category_sum.values()) / len(category_sum)
    alerts = [f"Overspending in {cat}" for cat, value in category_sum.items() if value > avg * 1.3]

    return {"alerts": alerts}