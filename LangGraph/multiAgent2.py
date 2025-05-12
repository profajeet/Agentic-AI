from pprint import pprint
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os
from typing import Dict, List, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
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


# Track necessary params for database operations
class SessionState:
    def __init__(self):
        self.db_params = {
            "db_name": None,
            "db_api": None,
            "db_password": None,
            "db_user": None,
            "db_port": None,
        }
        self.operation_params = {
            "operation": None,
            "table_name": None,
            "data": None
        }
        self.connected = False
        
session_state = SessionState()

# Define a parameter collector function
def collect_missing_params(user_input: str) -> Dict[str, Any]:
    """
    Parse user input for database parameters and identify missing ones
    """
    missing_params = []
    
    # Simple parsing (in production, use NLP or regex for better extraction)
    if not session_state.connected:
        if "db_name" in user_input.lower() or "database name" in user_input.lower():
            # Extract db_name (simplified)
            pass  # Add actual extraction logic
            
        # Add similar extraction for other parameters
        
        # Check which parameters are still missing
        for param, value in session_state.db_params.items():
            if value is None:
                missing_params.append(param)
    else:
        # For operation parameters
        if "operation" in user_input.lower():
            # Extract operation type
            pass
            
        # Add similar extraction for table_name and data
        
        for param, value in session_state.operation_params.items():
            if value is None and param != "data":  # data can be optional for some operations
                missing_params.append(param)
    
    return {"missing_params": missing_params}

# Enhanced database agent with parameter tracking
database_agent = create_react_agent(
    model=model,
    tools=[check_db_connectivity, perform_db_operation],
    prompt="""You are a database assistant. Your job is to assist users with database connectivity and operations.
        
        IMPORTANT INSTRUCTIONS:
        - NEVER assume any database parameters. Always explicitly ask for missing information.
        - Before attempting connection, you MUST have all of these parameters: db_name, db_api, db_password, db_user, and db_port.
        - Before performing operations, you MUST first establish a connection.
        - For operations, you MUST have at minimum: operation type and table_name.
        - If credentials are incorrect, inform the user and ask for updated credentials.
        - Always ask ONE question at a time to gather missing information.
        - NEVER try to connect without all parameters or perform operations without connecting first.
        
        Example dialogue:
        User: "Connect to my database"
        Assistant: "I'll help you connect to your database. Could you please provide the database name?"
        User: "orders_db"
        Assistant: "Thanks. What database API or driver are you using?"
        ...and so on until all parameters are collected.
        
        TOOLS:
        - check_db_connectivity: Verifies database connection using provided credentials
        - perform_db_operation: Executes operations on a connected database""",
    name="database_agent",
    checkpointer=checkpointer  
)

# Create state manager for conversation tracking
def manage_conversation_state(state):
    """Track conversation state and ensure all parameters are collected"""
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    
    if not last_message:
        return {"should_collect_params": True}
        
    # Check if we need to collect parameters
    missing_params = []
    if not session_state.connected:
        missing_params = [p for p, v in session_state.db_params.items() if v is None]
    elif session_state.connected and session_state.operation_params["operation"] is None:
        missing_params = ["operation", "table_name"]
        
    return {
        "should_collect_params": len(missing_params) > 0,
        "missing_params": missing_params
    }

# Enhanced supervisor with state tracking
supervisor = create_supervisor(
    agents=[database_agent],
    model=model,
    prompt=(
        """You are a supervisor managing a database assistant. Your role is to ensure the database operations are performed correctly.
        
        CRITICAL INSTRUCTIONS:
        1. NEVER attempt to connect to a database without ALL required parameters:
           - db_name (database name)
           - db_api (database API/driver)
           - db_password (password for authentication)
           - db_user (username for authentication)
           - db_port (port number)
        
        2. NEVER perform database operations without first establishing a connection.
        
        3. For database operations, require:
           - operation (INSERT, SELECT, UPDATE, etc.)
           - table_name (which table to operate on)
           - data (for operations that require data)
        
        4. When user input is missing information:
           - Ask ONE specific question to gather ONE missing parameter
           - Do not overwhelm the user by asking for everything at once
           - Keep track of what's been provided and what's still needed
        
        5. Always validate parameters before proceeding to the next step.
        
        Example proper interaction:
        User: "I want to connect to my database"
        You: "I'll help you connect. What's the name of your database?"
        User: "orders_db"
        You: "Thanks. What database API or driver are you using?"
        ...and so on until all parameters are collected.
        
        YOUR PRIMARY RESPONSIBILITY: Ensure all required parameters are collected before attempting any database action."""
    ),
    state_manager=manage_conversation_state,
    # checkpointer=checkpointer
).compile()

def chat_with_agent():
    # Initial state setup
    global session_state
    session_state = SessionState()
    
    while True:
        user_input = input("Enter your prompt (type 'quit' to exit): ")
        if user_input.lower() == "quit":
            print("Exiting the chat.")
            break
            
        thread_id = "session_1"  # Use consistent thread ID for state persistence
        
        # First, update session state based on user input (using simple parsing)
        # This would be more sophisticated in production code
        if "db_name" in user_input.lower():
            # Extract value (simplified parsing)
            for part in user_input.split():
                if part.endswith(".db"):
                    session_state.db_params["db_name"] = part
        # Similar parsing for other parameters
            
        # Process the message through the supervisor
        for chunk in supervisor.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                "session_state": session_state  # Pass the current session state
            },
            stream_mode='values',
            config={"configurable": {"thread_id": thread_id}}
        ):
            # Handle tool outputs and update session state based on tool usage
            if "tool" in chunk:
                tool_name = chunk["tool"].get("name")
                tool_output = chunk["tool"].get("output")
                
                if tool_name == "check_db_connectivity":
                    print(f"Database Connection: {tool_output}")
                    if "Connection established" in tool_output:
                        session_state.connected = True
                
                elif tool_name == "perform_db_operation":
                    print(f"Operation Result: {tool_output}")
                    # Reset operation parameters after successful operation
                    session_state.operation_params = {
                        "operation": None,
                        "table_name": None,
                        "data": None
                    }
            elif "messages" in chunk and chunk["messages"]:
                print(chunk["messages"][-1].pretty_print())


# Call the function to start the loop
if __name__ == "__main__":
    chat_with_agent()