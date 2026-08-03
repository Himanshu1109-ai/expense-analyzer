import os

from openpyxl import Workbook
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

from parser.pdf_parser import parse_pdf
try:
   from flask import Flask, request, jsonify, render_template, redirect, url_for # type: ignore[import]
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
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
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

    transactions = get_all_transactions()

    recent_transactions = transactions[-5:]

    insights = compute_insights(conn)

    health = compute_score(
        conn,
        summary["total_income"]
    )

    return render_template(
        "dashboard.html",
        total_expense=summary["total_expense"],
        total_income=summary["total_income"],
        balance=summary["balance"],
        recent_transactions=recent_transactions,
        insights=insights,
        health_score=health["score"]
    )
@app.route("/transactions-page")
def transactions_page():

    transactions = get_all_transactions()

    # Search value
    search = request.args.get("search", "").lower()

    # Category value
    category = request.args.get("category", "").lower()

    # Search filter
    if search:
        transactions = [
            tx for tx in transactions
            if search in tx["merchant"].lower()
        ]

    # Category filter
    if category:
        transactions = [
            tx for tx in transactions
            if tx["category"].lower() == category
        ]

    return render_template(
        "transactions.html",
        transactions=transactions,
        search=search,
        category=category
    )

@app.route("/edit-transaction/<int:tx_id>")
def edit_transaction(tx_id):
    transaction = get_transaction_by_id(tx_id)
    if transaction is None:
        return "Transaction not found", 404
    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )

@app.route("/update-transaction/<int:tx_id>", methods=["POST"])
def update_transaction_page(tx_id):

    merchant = request.form["merchant"]

    amount = float(request.form["amount"])

    category = request.form["category"]

    update_transaction(
        tx_id,
        amount,
        merchant,
        category
    )

    return redirect("/transactions-page")

    transaction = get_transaction_by_id(tx_id)

    if transaction is None:
        return "Transaction not found", 404

    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )

@app.route("/add-transaction", methods=["POST"])
def add_transaction():

    merchant = request.form["merchant"]

    amount = float(request.form["amount"])

    category = request.form.get("category")

    if not category:
        category = categorize(merchant)

    save_transaction(amount, merchant, category)

    return redirect("/transactions-page")

@app.route("/delete-transaction/<int:tx_id>", methods=["POST"])
def delete_transaction_page(tx_id):

    delete_transaction(tx_id)

    return redirect("/transactions-page")

@app.route("/upload-page")
def upload_page():
    return render_template("upload.html")


@app.route("/upload-bill", methods=["POST"])
def upload_bill():

    file = request.files.get("bill")

    if file is None or file.filename == "":
        return "No PDF selected", 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

    file.save(filepath)

    parse_pdf(filepath)

    return redirect(url_for("transactions_page"))


@app.route("/analytics-page")
def analytics_page():

    transactions = get_all_transactions()

    category_data = {}

    for tx in transactions:

        category = tx["category"]
        amount = tx["amount"]

        if category in category_data:
            category_data[category] += amount
        else:
            category_data[category] = amount

    return render_template(
        "analytics.html",
        labels=list(category_data.keys()),
        values=list(category_data.values())
    )

@app.route("/export-excel")
def export_excel():

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Transactions"

    # Header Row
    sheet.append(["ID", "Merchant", "Amount", "Category"])

    # Get all transactions
    transactions = get_all_transactions()

    # Add data
    for tx in transactions:

        sheet.append([
            tx["id"],
            tx["merchant"],
            tx["amount"],
            tx["category"]
        ])

    # Save Excel file
    filename = "transactions.xlsx"

    workbook.save(filename)

    # Download file
    return send_file(
        filename,
        as_attachment=True
    )
@app.route("/export-pdf")
def export_pdf():

    filename = "transactions.pdf"

    document = SimpleDocTemplate(filename)

    data = []

    # Table Heading
    data.append(["ID", "Merchant", "Amount", "Category"])

    # Get all transactions
    transactions = get_all_transactions()

    # Add transaction data
    for tx in transactions:

        data.append([
            tx["id"],
            tx["merchant"],
            f"₹{tx['amount']}",
            tx["category"]
        ])

    # Create table
    table = Table(data)

    # Style the table
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    document.build([table])

    return send_file(
        filename,
        as_attachment=True
    )
    # Save Excel file
    filename = "transactions.xlsx"

    workbook.save(filename)

    return send_file(
        filename,
        as_attachment=True
    )

@app.route("/transactions", methods=["GET"])
def list_transactions():
    """Return all transactions."""
    txs = get_all_transactions()
    return jsonify({"transactions": txs})


if __name__ == "__main__":
    app.run(debug=True)
