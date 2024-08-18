from datetime import datetime

class BankAccount:
    def __init__(self):
        self.balance = 0.0
        self.transactions = []

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        transaction = {
            'type': 'deposit',
            'amount': amount,
            'date': datetime.now()
        }
        self.transactions.append(transaction)

    def withdraw(self, amount: float) -> bool:
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            return False
        self.balance -= amount
        transaction = {
            'type': 'withdrawal',
            'amount': amount,
            'date': datetime.now()
        }
        self.transactions.append(transaction)
        return True

    def get_balance(self) -> float:
        return self.balance

    def get_transaction_history(self) -> list:
        return self.transactions