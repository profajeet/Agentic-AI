from typing import Annotated, TypedDict
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# Define the state
class AgentState(TypedDict):
    messages: Annotated[list[HumanMessage | AIMessage], "The messages in the conversation"]
    next: Annotated[str, "The next node to route to"]
    should_continue: Annotated[bool, "Whether to continue the conversation"]

# Define the nodes
def route_based_on_topic(state: AgentState) -> AgentState:
    """Route to different nodes based on the topic of the last message."""
    last_message = state["messages"][-1].content.lower()
    
    if "weather" in last_message:
        state["next"] = "weather_agent"
    elif "news" in last_message:
        state["next"] = "news_agent"
    elif "joke" in last_message:
        state["next"] = "joke_agent"
    else:
        state["next"] = "general_agent"
    
    return state

def weather_agent(state: AgentState) -> AgentState:
    """Handle weather-related queries."""
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    state["should_continue"] = True
    return state

def news_agent(state: AgentState) -> AgentState:
    """Handle news-related queries."""
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    state["should_continue"] = True
    return state

def joke_agent(state: AgentState) -> AgentState:
    """Handle joke requests."""
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    state["should_continue"] = True
    return state

def general_agent(state: AgentState) -> AgentState:
    """Handle general queries."""
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    state["should_continue"] = True
    return state

def should_continue(state: AgentState) -> bool:
    """Determine if the conversation should continue."""
    return state["should_continue"]

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("router", route_based_on_topic)
workflow.add_node("weather_agent", weather_agent)
workflow.add_node("news_agent", news_agent)
workflow.add_node("joke_agent", joke_agent)
workflow.add_node("general_agent", general_agent)

# Add edges
workflow.add_edge("router", "weather_agent")
workflow.add_edge("router", "news_agent")
workflow.add_edge("router", "joke_agent")
workflow.add_edge("router", "general_agent")

# Add conditional edges
workflow.add_conditional_edges(
    "weather_agent",
    should_continue,
    {
        True: "router",
        False: "end"
    }
)
workflow.add_conditional_edges(
    "news_agent",
    should_continue,
    {
        True: "router",
        False: "end"
    }
)
workflow.add_conditional_edges(
    "joke_agent",
    should_continue,
    {
        True: "router",
        False: "end"
    }
)
workflow.add_conditional_edges(
    "general_agent",
    should_continue,
    {
        True: "router",
        False: "end"
    }
)

# Set entry point
workflow.set_entry_point("router")

# Compile the graph
app = workflow.compile()

# Example usage
if __name__ == "__main__":
    # Initialize the state
    initial_state = AgentState(
        messages=[HumanMessage(content="Tell me a joke")],
        next="",
        should_continue=True
    )
    
    # Run the graph
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"Node: {key}")
            print(f"Output: {value['messages'][-1].content}\n") 