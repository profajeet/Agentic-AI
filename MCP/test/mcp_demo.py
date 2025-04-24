from agents import Agent, mcp_server
# from agents.mcp

agent = Agent(
    name = "Assistant",
    instructions = "You are a helpful assistant and would use given tools to help the user."
    mcp_servers = [mcp_server]
)