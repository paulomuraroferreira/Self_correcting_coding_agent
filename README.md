# README

This repository implements an LLM agent that receives a user's prompt and corresponding unit tests. The agent generates the code, tests it for correct execution, and ensures it passes the unit tests. If the code fails to execute or fails any unit test, the agent regenerates the code until it succeeds.

This project builds upon the code from LangChain's Notebook (https://github.com/mistralai/cookbook/blob/main/third_party/langchain/langgraph_code_assistant_mistral.ipynb), where an agent generates code based on the user's prompt and checks if the execution works.

The main contribution of this project is the integration of unit tests into the code execution process.

Additionally, the original Jupyter notebook code has been refactored into a structured Python project suitable for deployment. By adhering to best coding practices, the code has been modularized, reusable functions have been created, and proper documentation and testing have been ensured. The result is a well-organized .py project that is maintainable and ready for production.


## Setup Instructions

1. Clone the repository:


```python
git clone https://github.com/paulomuraroferreira/Self_correcting_coding_agent.git
cd Self_correcting_coding_agent
```

2. Install Dependencies:

```python
$pip install -e .
```

3. Environment Configuration:

Create a .env file and fill the following environment variables:

```python
OPENAI_API_KEY=your_openai_api_key
OPENAI_CHAT_MODEL="gpt-4o-2024-08-06"
```

4. Run the Application:

Input the code's prompt in the main.py file. The prompt should be descriptive and specify the name of the classes.

For example:

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

5. Add the unit test code in a .py file in the the src/unit_test_folder. Also, import the corresponding class from the 
code_solution.py file. For example, for the above prompt, the LLM will generate a class called BankAccount. Therefore, the 
src/unit_test_folder/test_unit_test.py should include:

    from src.code_solution import BankAccount

6. Run the main.py file. 

    ```python
    python main.py
    ```
