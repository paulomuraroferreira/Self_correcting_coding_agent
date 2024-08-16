from src.agent import AgentHandler
import uuid
from src.utils import _print_event

class Main:

    def __init__(self, question):
        self.question = question
        self.agent_handler = AgentHandler()      
        self._printed = set()
        thread_id = str(uuid.uuid4())
        self.config = {
            "configurable": {
                # Checkpoints are accessed by thread_id
                "thread_id": thread_id,
            }
        }

    def run(self):
        config = self.config
        question = self.question
        events = self.agent_handler.graph.stream(
            {"messages": [("user", question)], "iterations": 0}, config, stream_mode="values"
        )

        for event in events:
            _print_event(event, self._printed)

        
if __name__ == '__main__':

    QUESTION1 = "Write a function for fibonacci."
    QUESTION2 = """Create a Python program that allows two players to play a game of Tic-Tac-Toe. The game should be played on a 3x3 grid. The program should:

- Allow players to take turns to input their moves.
- Check for invalid moves (e.g., placing a marker on an already occupied space).
- Determine and announce the winner or if the game ends in a draw.

Requirements:
- Use a 2D list to represent the Tic-Tac-Toe board.
- Use functions to modularize the code.
- Validate player input.
- Check for win conditions and draw conditions after each move."""


    QUESTION3 = '''
Python Class Description
Class Name: BankAccount

Description:
The BankAccount class represents a user's bank account, allowing for deposits, withdrawals, and viewing the transaction history. The class ensures that withdrawals cannot exceed the current balance and that deposits and withdrawals are properly recorded in the transaction history.

Attributes:

balance (float): The current balance of the account, initialized to 0.
transactions (list): A list to store the history of transactions. Each transaction is stored as a dictionary with keys type (either 'deposit' or 'withdrawal'), amount, and date.
Methods:

deposit(amount: float) -> None: Adds the specified amount to the balance and records the transaction.
withdraw(amount: float) -> bool: Attempts to subtract the specified amount from the balance. Returns True if successful, otherwise returns False. Records the transaction if successful.
get_balance() -> float: Returns the current balance.
get_transaction_history() -> list: Returns a list of all transactions.
'''

    main = Main(QUESTION3)
    main.run()
    
