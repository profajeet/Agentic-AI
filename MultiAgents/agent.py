from pprint import pprint
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os
import asyncio
import nest_asyncio


load_dotenv("Learning-Research-Development/Agentic-AI/.env")
API=os.getenv('OPENAI_API_KEY')


model = ChatOllama(model="llama3.2")
# model = ChatOpenAI(api_key=API)
checkpointer = InMemorySaver()


async def postgres_db(db_name: str, db_host: str, db_password: str, db_user: str, user_query: str):
    """
    postgresql database function to interact with a postgresql database server.

    Args:
        db_name (str): The name of the database to connect to.
        db_host (str): The host address of the database server.
        db_password (str): The password for authenticating with the database.
        db_user (str): The username for authenticating with the database.
        user_query (str): The user query or input to process using the database server.

    Returns:
        str: The response from the database server after processing the query.
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient
    client =  MultiServerMCPClient(
            {
                "postgresql": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@executeautomation/database-server",
                        "--postgresql", 
                        "--host",
                        db_host,
                        "--database",
                        db_name,
                        "--user",
                        db_user,
                        "--password",
                        db_password
                    ],
                    "transport":"stdio"
                }
            }
        ) 
    tools = await client.get_tools()
    agent = create_react_agent(
        model,
        tools,
        prompt="You are an AI assistant that strictly responds only based on the available tools. If the input requires information or actions beyond the capabilities of the tools, ask the user for the necessary details until you have complete input to proceed.",
        checkpointer=checkpointer
    )

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_query}]},
        config={"configurable": {"thread_id": "1"}}
    )
    return response['messages'][-1].content

async def mysql_db(db_name: str, db_host: str, db_password: str, db_user: str, user_query: str):
    """
    mysql database function to interact with a mysql database server.

    Args:
        db_name (str): The name of the database to connect to.
        db_host (str): The host address of the database server.
        db_password (str): The password for authenticating with the database.
        db_user (str): The username for authenticating with the database.
        user_query (str): The user query or input to process using the database server.

    Returns:
        str: The response from the database server after processing the query.
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient
    client =  MultiServerMCPClient(
            {
                "mysql": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@executeautomation/database-server",
                        "--mysql", 
                        "--host",
                        db_host,
                        "--database",
                        "--port", 
                        "3306",
                        db_name,
                        "--user",
                        db_user,
                        "--password",
                        db_password
                    ],
                    "transport":"stdio"
                }
            }
        ) 
    tools = await client.get_tools()
    agent = create_react_agent(
        model,
        tools,
        prompt="You are an AI assistant that strictly responds only based on the available tools. If the input requires information or actions beyond the capabilities of the tools, ask the user for the necessary details until you have complete input to proceed.",
        checkpointer=checkpointer
    )

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_query}]},
        config={"configurable": {"thread_id": "1"}}
    )
    return response['messages'][-1].content



database_agent = create_react_agent(
    model=model,
    tools=[postgres_db, mysql_db],
    prompt="""You are a database assistant. Your job is to assist users with database connectivity and operations. 
        - Always ask for required details (e.g., credentials, database type, etc.) before performing any operation.
        - If credentials are incorrect, inform the user and ask for updated credentials.
        - Once connected, ask for the operation details (e.g., data to store, table name, etc.).
        - Respond only based on tool outputs and do not make assumptions.
        - Ensure the user provides all necessary information before proceeding.""",
    name="database_agent",
)

supervisor_system_prompt = """
You are a Supervisor Agent responsible for orchestrating and coordinating tasks between the user and various specialized agents/tools. Follow these steps meticulously:

1. Understand and Clarify User Query:
Begin by carefully interpreting the user's instruction or query. If any critical information or context is missing, ask follow-up questions to ensure you have complete clarity before proceeding.

2. Check Tool Availability and Status:
Coordinate with the available agents to check the list of tools and their current statuses. Ensure that the required tools for the task are online, functional, and accessible.

3. Gather Required Parameters for Tools:
Once the target tool is identified, consult the respective agent to determine the required input parameters for the operation. Then, collect these parameters either from the user or from available data.

4. Trigger the Operation Using the Respective Agent:
After gathering all necessary inputs and confirming tool readiness, initiate the operation by directing the appropriate agent to execute the task. Monitor the result and confirm its success or handle errors if they occur.

5. Loop for Next Instruction:
Once the task is completed and results are delivered to the user, ask the user if they would like to perform another operation or have any further instructions.

Important Rules:
- Always ensure complete information is collected before initiating any task.
- Maintain a clear and logical flow of communication between the user, supervisor agent (yourself), and specialized agents.
- Handle missing tool statuses or unavailable tools gracefully by notifying the user and suggesting alternatives if applicable.
- Your goal is to provide a seamless, efficient, and accurate task orchestration experience.
"""

def call_supervisor():
    supervisor = create_supervisor(
        agents=[database_agent],
        model=model,
        prompt=(supervisor_system_prompt),
    ).compile(checkpointer=checkpointer)
    return supervisor