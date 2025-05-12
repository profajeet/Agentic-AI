from pprint import pprint
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os
load_dotenv("Learning-Research-Development/Agentic-AI/.env")
API=os.getenv('OPENAI_API_KEY')
checkpointer = InMemorySaver()

# model = ChatOllama(model="llama3.2")
model = ChatOpenAI(api_key=API)


def check_db_connectivity(db_name: str, db_api: str, db_password: str, db_user: str, db_port: int):
    """
    Check database connectivity.

    Args:
        db_name (str): The name of the database to connect to.
        db_api (str): The database API or driver to use for the connection.
        db_password (str): The password for authenticating with the database.
        db_user (str): The username for authenticating with the database.
        db_port (int): The port number on which the database is running.

    Returns:
        str: A message indicating the success of the database connection.
    """
    if db_password and db_user:  # Simulating a successful connection
        return f"Connection established to the database: {db_name}."
    else:
        return "I am not able to establish database connectivity, either password or user ID is incorrect. Please reshare your credentials."


def perform_db_operation(operation: str, table_name: str, data: dict = None):
    """Perform a database operation"""
    if operation.lower() == "insert" and data:
        return f"Data {data} stored in table '{table_name}'."
    return f"Successfully performed '{operation}' on table '{table_name}'."


database_agent = create_react_agent(
    model=model,
    tools=[check_db_connectivity, perform_db_operation],
    prompt="""You are a database assistant. Your job is to assist users with database connectivity and operations. 
        - Always ask for required details (e.g., credentials, database type, etc.) before performing any operation.
        - If credentials are incorrect, inform the user and ask for updated credentials.
        - Once connected, ask for the operation details (e.g., data to store, table name, etc.).
        - Respond only based on tool outputs and do not make assumptions.
        - Ensure the user provides all necessary information before proceeding.""",
    name="database_agent",
    checkpointer=checkpointer  
)

supervisor = create_supervisor(
    agents=[database_agent],
    model=model,
    prompt=(
        "You are a supervisor managing a database assistant. Your role is to ensure the assistant performs tasks "
        "like checking connectivity and executing database operations. "
        "- Guide the assistant to ask clarifying questions until all required details are provided by the user. "
        "- Ensure the assistant does not respond without proper tool outputs. "
        "- Do not provide answers outside the scope of database operations."
    ),
    # checkpointer=checkpointer
).compile()

def chat_with_agent():
    while True:
        user_input = input("Enter your prompt (type 'quit' to exit): ")
        if user_input.lower() == "quit":
            print("Exiting the chat.")
            break

        for chunk in supervisor.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            },
            stream_mode='values',
            config={"configurable": {"thread_id": "1"}}
        ):
            # Ensure the tool outputs are properly validated
            if "tool" in chunk and chunk["tool"]["name"] == "check_db_connectivity":
                print(chunk["tool"]["output"])
            else:
                print(chunk["messages"][-1].pretty_print())


# Call the function to start the loop
chat_with_agent()