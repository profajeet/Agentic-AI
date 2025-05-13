from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
import asyncio
import importlib
import sys
from pathlib import Path

class MCPManager:
    def __init__(self):
        self.servers = {}
        self.server_status = {}

    def register_server(self, name: str, server: FastMCP):
        """Register a new MCP server."""
        self.servers[name] = server
        self.server_status[name] = {
            "status": "registered",
            "started": False,
            "error": None
        }

    def get_server(self, name: str) -> Optional[FastMCP]:
        """Get a registered MCP server by name."""
        return self.servers.get(name)

    def get_all_servers(self) -> Dict[str, FastMCP]:
        """Get all registered MCP servers."""
        return self.servers

    def get_server_status(self, name: str) -> Dict:
        """Get the status of a specific server."""
        return self.server_status.get(name, {"status": "not_found"})

    def get_all_server_statuses(self) -> Dict[str, Dict]:
        """Get status of all servers."""
        return self.server_status

    def update_server_status(self, name: str, status: str, error: Optional[str] = None):
        """Update the status of a server."""
        if name in self.server_status:
            self.server_status[name].update({
                "status": status,
                "error": error
            })

# Create the master MCP server
master_mcp = FastMCP("Master MCP")
mcp_manager = MCPManager()

@master_mcp.tool()
async def register_mcp_server(
    name: str,
    module_path: str,
    class_name: str = "mcp"
) -> Dict:
    """
    Register a new MCP server from a Python module.
    
    Args:
        name: Unique name for the MCP server
        module_path: Path to the Python module containing the MCP server
        class_name: Name of the FastMCP instance in the module (default: 'mcp')
    
    Returns:
        Dict containing registration status
    """
    try:
        # Add the parent directory to Python path if needed
        module_dir = str(Path(module_path).parent)
        if module_dir not in sys.path:
            sys.path.append(module_dir)

        # Import the module
        module_name = Path(module_path).stem
        module = importlib.import_module(module_name)
        
        # Get the MCP server instance
        server = getattr(module, class_name)
        
        if not isinstance(server, FastMCP):
            return {
                "status": "error",
                "message": f"Invalid MCP server in module {module_path}"
            }

        # Register the server
        mcp_manager.register_server(name, server)
        
        return {
            "status": "success",
            "message": f"Successfully registered MCP server '{name}'",
            "details": {
                "module": module_path,
                "class": class_name
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to register MCP server: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "module_path": module_path
            }
        }

@master_mcp.tool()
async def list_registered_servers() -> Dict:
    """
    List all registered MCP servers and their status.
    
    Returns:
        Dict containing list of servers and their statuses
    """
    servers = mcp_manager.get_all_servers()
    statuses = mcp_manager.get_all_server_statuses()
    
    return {
        "status": "success",
        "servers": {
            name: {
                "status": statuses[name],
                "tools": [tool.__name__ for tool in server.tools]
            }
            for name, server in servers.items()
        }
    }

@master_mcp.tool()
async def get_server_tools(server_name: str) -> Dict:
    """
    Get all tools available in a specific MCP server.
    
    Args:
        server_name: Name of the registered MCP server
    
    Returns:
        Dict containing list of tools and their details
    """
    server = mcp_manager.get_server(server_name)
    if not server:
        return {
            "status": "error",
            "message": f"Server '{server_name}' not found"
        }
    
    tools = []
    for tool in server.tools:
        tools.append({
            "name": tool.__name__,
            "doc": tool.__doc__,
            "signature": str(tool.__annotations__)
        })
    
    return {
        "status": "success",
        "server": server_name,
        "tools": tools
    }

@master_mcp.tool()
async def execute_server_tool(
    server_name: str,
    tool_name: str,
    **kwargs
) -> Dict:
    """
    Execute a tool from a specific MCP server.
    
    Args:
        server_name: Name of the registered MCP server
        tool_name: Name of the tool to execute
        **kwargs: Arguments to pass to the tool
    
    Returns:
        Dict containing tool execution results
    """
    server = mcp_manager.get_server(server_name)
    if not server:
        return {
            "status": "error",
            "message": f"Server '{server_name}' not found"
        }
    
    tool = next((t for t in server.tools if t.__name__ == tool_name), None)
    if not tool:
        return {
            "status": "error",
            "message": f"Tool '{tool_name}' not found in server '{server_name}'"
        }
    
    try:
        result = await tool(**kwargs)
        return {
            "status": "success",
            "server": server_name,
            "tool": tool_name,
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Tool execution failed: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "server": server_name,
                "tool": tool_name
            }
        }

if __name__ == "__main__":
    # Example: Register the MySQL checker server
    asyncio.run(register_mcp_server(
        name="mysql_checker",
        module_path="mysql_check.py"
    ))
    
    # Run the master MCP server
    master_mcp.run(transport="sse") 