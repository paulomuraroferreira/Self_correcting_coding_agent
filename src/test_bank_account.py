import pytest
from datetime import datetime
from 

@pytest.fixture
def account():
    """Fixture to create a BankAccount instance for testing."""
    return BankAccount()

def test_initial_balance(account):
    """Test that a new account starts with a balance of 0."""
    assert account.get_balance() == 0.0

def test_deposit(account):
    """Test depositing money into the account."""
    account.deposit(100)
    assert account.get_balance() == 100.0
    assert len(account.get_transaction_history()) == 1
    assert account.get_transaction_history()[0]['type'] == 'deposit'

def test_withdrawal_successful(account):
    """Test withdrawing money when funds are sufficient."""
    account.deposit(100)
    result = account.withdraw(50)
    assert result == True
    assert account.get_balance() == 50.0
    assert len(account.get_transaction_history()) == 2
    assert account.get_transaction_history()[-1]['type'] == 'withdrawal'

def test_withdrawal_insufficient_funds(account):
    """Test attempting to withdraw more than the available balance."""
    account.deposit(50)
    result = account.withdraw(100)
    assert result == False
    assert account.get_balance() == 50.0
    assert len(account.get_transaction_history()) == 1  # No withdrawal recorded

def test_transaction_history(account):
    """Test the transaction history records all transactions correctly."""
    account.deposit(100)
    account.withdraw(40)
    history = account.get_transaction_history()
    assert len(history) == 2
    assert history[0]['type'] == 'deposit'
    assert history[1]['type'] == 'withdrawal'

def test_invalid_deposit(account):
    """Test that depositing a negative amount raises ValueError."""
    with pytest.raises(ValueError):
        account.deposit(-100)

def test_invalid_withdrawal(account):
    """Test that withdrawing a negative amount raises ValueError."""
    with pytest.raises(ValueError):
        account.withdraw(-50)
