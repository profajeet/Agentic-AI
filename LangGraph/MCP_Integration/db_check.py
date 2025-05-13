from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional

mcp = FastMCP("Database Checker")

@mcp.tool()
async def check_database_connection(connection_string: str) -> Dict:
    """
    Check database connectivity using the provided connection string.
    
    Args:
        connection_string: Database connection string (e.g., 'postgresql://user:password@localhost:5432/dbname')
    
    Returns:
        Dict containing connection status and details
    """
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {
                "status": "success",
                "message": "Database connection successful",
                "details": {
                    "database_type": engine.dialect.name,
                    "connection_string": connection_string
                }
            }
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "connection_string": connection_string
            }
        }

@mcp.tool()
async def execute_query(connection_string: str, query: str) -> Dict:
    """
    Execute a SQL query and return the results.
    
    Args:
        connection_string: Database connection string
        query: SQL query to execute
    
    Returns:
        Dict containing query results or error information
    """
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = [dict(row) for row in result]
            return {
                "status": "success",
                "message": "Query executed successfully",
                "results": rows,
                "row_count": len(rows)
            }
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": f"Query execution failed: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "query": query
            }
        }

@mcp.tool()
async def check_table_exists(connection_string: str, table_name: str) -> Dict:
    """
    Check if a table exists in the database.
    
    Args:
        connection_string: Database connection string
        table_name: Name of the table to check
    
    Returns:
        Dict containing table existence status
    """
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            # This query works for most SQL databases
            query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            )
            """
            result = connection.execute(text(query))
            exists = result.scalar()
            return {
                "status": "success",
                "table_exists": bool(exists),
                "table_name": table_name
            }
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": f"Failed to check table existence: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "table_name": table_name
            }
        }

if __name__ == "__main__":
    mcp.run(transport="sse") 