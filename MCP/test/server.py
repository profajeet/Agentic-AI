from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Weather Server")

@mcp.tool()
def get_weather(city:str)-> str:
    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text

@mcp.tool()
def add_number(a:int,b:int)->int:
    return a+b