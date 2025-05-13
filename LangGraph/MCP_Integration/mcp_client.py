from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
import asyncio
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
import os
load_dotenv("Learning-Research-Development/Agentic-AI/.env")
API=os.getenv('OPENAI_API_KEY')
checkpointer = InMemorySaver()

# model = ChatOllama(model="deepseek-r1")

model = ChatOpenAI(api_key=API)

async def main():
    async with MultiServerMCPClient(
            {
                "math": {
                    "command": "python",
                    # Replace with absolute path to your math_server.py file
                    "args": ["/Users/ajeet/Data/Development/Learning-Research-Development/Agentic-AI/LangGraph/MCP_Integration/maths_server.py"],
                    "transport": "stdio",
                },
                "weather": {
                    # Ensure your start your weather server on port 8000
                    "url": "http://localhost:8000/sse",
                    "transport": "sse",
                },
                "postgresql": {
            "command": "npx",
            "args": [
                "-y",
                "@executeautomation/database-server",
                "--postgresql", 
                "--host",
                "localhost",
                "--database",
                "postgres",
                "--user",
                "postgres",
                "--password",
                "root"
            ],
            # "transport":"sse"
        }
            }
        ) as client:
            agent = create_react_agent(
                model,
                client.get_tools(),
                prompt="You are an AI assistant that strictly responds only based on the available tools. If the input requires information or actions beyond the capabilities of the tools, ask the user for the necessary details until you have complete input to proceed.",
                checkpointer=checkpointer
            )

            while True:
                user_input = input("Enter your query (type 'quit' to exit): ")
                if user_input.lower() == 'quit':
                    print("Exiting the chatbot. Goodbye!")
                    break

                response = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config={"configurable": {"thread_id": "1"}}

                )

                for message in response['messages']:
                    message.pretty_print()

asyncio.run(main())