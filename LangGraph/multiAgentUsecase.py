from pprint import pprint
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

model = ChatOllama(model="llama3.2")


def check_db_connectivity(db_name: str,db_api:str,db_password:str,db_user:str,db_port:int):
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
    return f"Successfully connected to the database: {db_name}, {db_user}, {db_port}."


def perform_db_operation(operation: str, table_name: str):
    """Perform a database operation"""
    return f"Successfully performed '{operation}' on table '{table_name}'."


database_agent = create_react_agent(
    model=model,
    tools=[check_db_connectivity, perform_db_operation],
    prompt="You are a database assistant. You check database connectivity and perform database operations.",
    name="database_agent",
)

supervisor = create_supervisor(
    agents=[database_agent],
    model=model,
    prompt=(
        "You manage a database assistant. Assign work to it for checking connectivity "
        "and performing database operations."
        ""
        "Note: Do not answer anything other than your expertise."
    ),
).compile()

# for chunk in supervisor.stream(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "Check connectivity to 'CustomerDB' and perform 'INSERT' operation on 'Orders' table"
#             }
#         ]
#     }
# ):
#     pprint(chunk)
#     print("\n")

# response = supervisor.invoke({
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "Check connectivity to 'CustomerDB' and perform 'INSERT' operation on 'Orders' table"
#             }
#         ]
#     })
# for m in response['messages']:
#     m.pretty_print()


def chat_with_agent():
    while True:
        user_input = input("Enter your prompt (type 'quit' to exit): ")
        if user_input.lower() == "quit":
            print("Exiting the chat.")
            break
        # response = supervisor.invoke(
        #     {"messages": [{"role": "user", "content": user_input}]},
        #     # config={"configurable": {"thread_id": "1"}},
        # )
        # for m in response["messages"]:
        #     m.pretty_print()

        for chunk in supervisor.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            },
            stream_mode='values'
        ):
            print(chunk["messages"][-1].pretty_print())

            # pprint(chunk)
            # for m in chunk:
            #     m.pretty_print()
            # print("\n")

        # for chunk in supervisor.stream(
        #     {
        #         "messages": [
        #             {
        #                 "role": "user",
        #                 "content": user_input
        #             }
        #         ]
        #     },
        #     stream_mode='updates'
        # ):
        #     print(chunk)


# Call the function to start the loop
chat_with_agent()
