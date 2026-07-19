from datetime import datetime

class Transaction:
    def __init__(self, amount, merchant, category, date=None, id=None):
        self.id = id
        self.amount = amount
        self.merchant = merchant
        self.category = category
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "merchant": self.merchant,
            "category": self.category,
            "date": self.date
        }

    @staticmethod
    def from_db_row(row):
        return Transaction(
            id=row[0],
            amount=row[1],
            merchant=row[2],
            category=row[3],
            date=row[4]
        )