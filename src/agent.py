from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from src.logger_setup import logger
from dotenv import load_dotenv
load_dotenv()
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Annotated
from typing import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
import subprocess
import os

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        error : Binary flag for control flow to indicate whether test error was tripped
        messages : With user question, error messages, reasoning
        generation : Code solution
        iterations : Number of tries
    """

    error: str
    messages: Annotated[list[AnyMessage], add_messages]
    generation: str
    iterations: int

class code(BaseModel):
    """Code output"""
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")
    description = "Schema for code solutions to questions about LCEL."


class TestCode:

    def __init__(self, path_of_test_file: str):
        self.path_of_test_file = path_of_test_file
        self.code_file_path = "src/code_solution.py"

    def run_tests(self):

        result = subprocess.run(["pytest", "-v", self.path_of_test_file], capture_output=True, text=True)

        captured_output = result.stdout

        all_tests_passed = (result.returncode == 0)

        logger.info(f'\n{captured_output}')
            
        # Return the captured output and the result as a dictionary
        return {
            "message": captured_output,
            "all_tests_passed": all_tests_passed
    }

    def code_check(self, state: GraphState):
        """
        Check code

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, error
        """

        logger.info("---CHECKING CODE---")

        # State
        messages = state["messages"]
        code_solution = state["generation"]
        iterations = state["iterations"]

        # Get solution components
        prefix = code_solution.prefix
        imports = code_solution.imports
        code = code_solution.code

        # Check imports
        try:
            exec(imports)
        except Exception as e:
            logger.info("---CODE IMPORT CHECK: FAILED---")
            error_message = [("user", f"Your solution failed the import test. Here is the error: {e}. Reflect on this error and your prior attempt to solve the problem. (1) State what you think went wrong with the prior solution and (2) try to solve this problem again. Return the FULL SOLUTION. Use the code tool to structure the output with a prefix, imports, and code block:")]
            messages += error_message
            return {
                "generation": code_solution,
                "messages": messages,
                "iterations": iterations,
                "error": "yes",
            }

        # Check execution
        try:
            combined_code = f"{imports}\n{code}"
            # Use a shared scope for exec
            global_scope = {}
            exec(combined_code, global_scope)
        except Exception as e:
            logger.info("---CODE BLOCK CHECK: FAILED---")
            error_message = [("user", f"Your solution failed the code execution test: {e}) Reflect on this error and your prior attempt to solve the problem. (1) State what you think went wrong with the prior solution and (2) try to solve this problem again. Return the FULL SOLUTION. Use the code tool to structure the output with a prefix, imports, and code block:")]
            messages += error_message
            return {
                "generation": code_solution,
                "messages": messages,
                "iterations": iterations,
                "error": "yes",
            }
        
        with open(self.code_file_path, "w") as file:
            file.write(combined_code)

        # Run tests
        test_result = self.run_tests()
        if test_result['all_tests_passed']:
            logger.info("All tests passed!")
        else:
            logger.info(f"Some tests failed.")
            error_message = [("user", f"Your solution failed the unit test: {test_result['message']}). Reflect on this error and your prior attempt to solve the problem. (1) State what you think went wrong with the prior solution and (2) try to solve this problem again. Return the FULL SOLUTION. Use the code tool to structure the output with a prefix, imports, and code block:")]
            messages += error_message
            
            return {
                "generation": code_solution,
                "messages": messages,
                "iterations": iterations,
                "error": "yes",
            } 


        # No errors
        logger.info("---NO CODE TEST FAILURES---")
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": "no",
        }

class Agent:
    def __init__(self, path_of_test_file: str):
        self.openai_model = os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-2024-08-06"
        self.llm = ChatOpenAI(model=self.openai_model, temperature=0)
        self.max_iterations = 5
        self.path_of_test_file = path_of_test_file
        self.code_gen_prompt_claude = ChatPromptTemplate.from_messages(
            [
                (
                    "system", 
                    """You are a coding assistant. Ensure any code you provide can be executed with all required imports and variables \n
                    defined. Structure your answer: 1) a prefix describing the code solution, 2) the imports, 3) the functioning code block.
                    \n Here is the user question:""",
                ),
                ("placeholder", "{messages}"),
            ]
        )

        self.code_gen_chain = self.llm.with_structured_output(code, include_raw=False)

    def generate(self, state: GraphState):
        """
        Generate a code solution

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation
        """

        logger.info("---GENERATING CODE SOLUTION---")

        # State
        messages = state["messages"]
        iterations = state["iterations"]
        error = state["error"]

        # Solution
        code_solution = self.code_gen_chain.invoke(messages)
        messages += [
            (
                "assistant",
                f"Here is my attempt to solve the problem: {code_solution.prefix} \n Imports: {code_solution.imports} \n Code: {code_solution.code}",
            )
        ]

        # Increment
        iterations = iterations + 1
        return {"generation": code_solution, "messages": messages, "iterations": iterations}
    
    def code_check(self, state: GraphState):

        results = TestCode(self.path_of_test_file).code_check(state)
        return results
        
    
    ### Conditional edges
    def decide_to_finish(self, state: GraphState):
        """
        Determines whether to finish.

        Args:
            state (dict): The current graph state

        Returns:
            str: Next node to call
        """
        error = state["error"]
        iterations = state["iterations"]

        if error == "no" or iterations == self.max_iterations:
            logger.info("---DECISION: FINISH---")
            return "end"
        else:
            logger.info("---DECISION: RE-TRY SOLUTION---")
            return "generate"

class AgentHandler:
    def __init__(self):
        self.builder = StateGraph(GraphState)
        self.agent = Agent(path_of_test_file="src/unit_test_folder/test_unit_test.py")
        self.build_graph()

    def build_graph(self):
        # Define the nodes
        self.builder.add_node("generate", self.agent.generate)  # generation solution
        self.builder.add_node("check_code", self.agent.code_check)  # check code

        # Build graph
        self.builder.set_entry_point("generate")
        self.builder.add_edge("generate", "check_code")
        self.builder.add_conditional_edges(
            "check_code",
            self.agent.decide_to_finish,
            {
                "end": END,
                "generate": "generate",
            },
        )

        self.graph = self.builder.compile(checkpointer=MemorySaver())

        from IPython.display import Image

        # Save the image to a file instead of displaying it
        image_data = self.graph.get_graph(xray=True).draw_mermaid_png()
        with open("output_image.png", "wb") as f:
            f.write(image_data)
        print("Image saved as output_image.png")


