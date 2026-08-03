"""AI Financial Insights helpers."""

from typing import Dict, Any


def compute_insights(conn) -> Dict[str, Any]:

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT category, SUM(amount) as total
        FROM transactions
        GROUP BY category
        """
    )

    rows = cursor.fetchall()

    if not rows:
        return {
            "message": "No transaction data available",
            "alerts": [],
            "suggestions": []
        }


    # Category wise spending
    category_sum = {
        category: total
        for category, total in rows
    }


    # Total expense
    total_expense = sum(category_sum.values())


    # Highest spending category
    highest_category = max(
        category_sum,
        key=category_sum.get
    )

    highest_amount = category_sum[highest_category]


    # Percentage calculation
    highest_percentage = round(
        (highest_amount / total_expense) * 100,
        2
    )


    alerts = []
    suggestions = []


    # Overspending detection
    average = total_expense / len(category_sum)


    for category, amount in category_sum.items():

        if amount > average * 1.3:

            alerts.append(
                f"⚠️ High spending detected in {category}"
            )

            suggestions.append(
                f"Try reducing {category} expenses to save money."
            )


    # General suggestions
    if highest_percentage > 40:

        suggestions.append(
            f"{highest_category} is your biggest expense category "
            f"({highest_percentage}% of total spending)."
        )


    return {

        "total_expense": total_expense,

        "top_category": {
            "name": highest_category,
            "amount": highest_amount,
            "percentage": highest_percentage
        },

        "alerts": alerts,

        "suggestions": suggestions
    }