from datetime import datetime

def validate_amount(amount_str):
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        return amount
    except ValueError:
        raise ValueError("Invalid amount. Please enter a positive number.")


def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")


def validate_type(txn_type):
    txn_type = txn_type.lower()
    if txn_type not in ["income", "expense"]:
        raise ValueError("Type must be 'income' or 'expense'.")
    return txn_type.capitalize()