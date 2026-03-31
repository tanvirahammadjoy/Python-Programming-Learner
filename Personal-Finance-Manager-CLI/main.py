from storage import StorageHandler
from utils import validate_amount, validate_date, validate_type

class FinanceManager:
    def __init__(self):
        self.storage = StorageHandler("json")  # change to "csv" if needed
        self.transactions = self.storage.load()

    def add_transaction(self):
        try:
            amount = validate_amount(input("Amount: "))
            category = input("Category: ").strip()
            txn_type = validate_type(input("Type (income/expense): "))
            date = validate_date(input("Date (YYYY-MM-DD): "))

            transaction = {
                "amount": amount,
                "category": category,
                "type": txn_type,
                "date": date
            }

            self.transactions.append(transaction)
            self.storage.save(self.transactions)

            print("✅ Transaction added!")

        except ValueError as e:
            print("❌ Error:", e)

    def view_transactions(self):
        if not self.transactions:
            print("No transactions found.")
            return

        print("\n📜 Transaction History:")
        for i, txn in enumerate(self.transactions, 1):
            print(f"{i}. {txn}")

    def show_balance(self):
        balance = 0
        for txn in self.transactions:
            amount = float(txn["amount"])
            if txn["type"] == "Income":
                balance += amount
            else:
                balance -= amount

        print(f"\n💰 Current Balance: {balance:.2f}")

    def export(self):
        choice = input("Export as (json/csv): ").lower()
        if choice not in ["json", "csv"]:
            print("Invalid format.")
            return

        exporter = StorageHandler(choice, "exported_data")
        exporter.save(self.transactions)

        print(f"✅ Data exported as {choice.upper()}!")

    def run(self):
        while True:
            print("\n==== Personal Finance Manager ====")
            print("1. Add Transaction")
            print("2. View History")
            print("3. Show Balance")
            print("4. Export Data")
            print("5. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                self.add_transaction()
            elif choice == "2":
                self.view_transactions()
            elif choice == "3":
                self.show_balance()
            elif choice == "4":
                self.export()
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")


if __name__ == "__main__":
    app = FinanceManager()
    app.run()