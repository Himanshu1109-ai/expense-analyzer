try:
    from flask import Flask, request, jsonify, render_template  # type: ignore[import]
except ModuleNotFoundError as e:
    raise RuntimeError(
        "Flask is not installed. Install it with 'pip install flask' and try again."
    ) from e
import re
import sqlite3
from services.categorizer import categorize
from database.db import (
    save_transaction,
    conn,
    get_all_transactions,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
)
from services.insights import compute_insights
from services.score import compute_score
from parser.sms_parser import parse_sms_payload

app = Flask(__name__)

# Database initialization is handled in database/db.py

# 📩 Parse SMS
@app.route("/parse-sms", methods=["POST"])
def parse_sms():
    payload = request.get_json() or {}
    result = parse_sms_payload(payload)
    return jsonify(result), 201


def _validate_tx_payload(payload: dict):
    errors = []
    if "amount" in payload:
        try:
            float(payload["amount"])
        except Exception:
            errors.append("amount must be a number")
    else:
        errors.append("amount is required")

    if "merchant" not in payload or not str(payload.get("merchant")).strip():
        errors.append("merchant is required")

    return errors


@app.route("/transactions", methods=["POST"])
def create_transaction():
    payload = request.get_json() or {}
    errs = _validate_tx_payload(payload)
    if errs:
        return jsonify({"errors": errs}), 400

    amount = float(payload["amount"])
    merchant = payload["merchant"].strip()
    category = payload.get("category") or categorize(merchant)
    tx_id = save_transaction(amount, merchant, category)
    tx = get_transaction_by_id(tx_id)
    return jsonify(tx), 201


@app.route("/transactions/<int:tx_id>", methods=["GET"])
def get_transaction(tx_id: int):
    tx = get_transaction_by_id(tx_id)
    if not tx:
        return jsonify({"message": "Not found"}), 404
    return jsonify(tx)


@app.route("/transactions/<int:tx_id>", methods=["PUT"])
def put_transaction(tx_id: int):
    payload = request.get_json() or {}
    errs = _validate_tx_payload(payload)
    if errs:
        return jsonify({"errors": errs}), 400

    amount = float(payload["amount"])
    merchant = payload["merchant"].strip()
    category = payload.get("category") or categorize(merchant)

    ok = update_transaction(tx_id, amount, merchant, category)
    if not ok:
        return jsonify({"message": "Not found"}), 404
    return jsonify(get_transaction_by_id(tx_id))


@app.route("/transactions/<int:tx_id>", methods=["DELETE"])
def remove_transaction(tx_id: int):
    ok = delete_transaction(tx_id)
    if not ok:
        return jsonify({"message": "Not found"}), 404
    return "", 204

# ⚠️ Insights
@app.route("/insights", methods=["GET"])
def insights():
    return jsonify(compute_insights(conn))

# 🧮 Score
@app.route("/score", methods=["GET"])
def score():
    income = float(request.args.get("income", 0))

    return jsonify(compute_score(conn, income))

# 📊 Home endpoint
def get_dashboard_summary():
    transactions = get_all_transactions()

    total_expense = sum(tx["amount"] for tx in transactions)

    total_income = 50000      # Temporary value

    balance = total_income - total_expense

    return {
        "total_expense": total_expense,
        "total_income": total_income,
        "balance": balance
    }
@app.route("/")
def home():

    summary = get_dashboard_summary()

    return render_template(
        "dashboard.html",
        total_expense=summary["total_expense"],
        total_income=summary["total_income"],
        balance=summary["balance"]
    )
@app.route("/transactions-page")
def transactions_page():

    transactions = get_all_transactions()

    return render_template(
        "transactions.html",
        transactions=transactions
    )


@app.route("/upload-page")
def upload_page():
    return render_template("upload.html")


@app.route("/analytics-page")
def analytics_page():
    return render_template("analytics.html")

@app.route("/transactions", methods=["GET"])
def list_transactions():
    """Return all transactions."""
    txs = get_all_transactions()
    return jsonify({"transactions": txs})


if __name__ == "__main__":
    app.run(debug=True)
