from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional
import pymysql

mcp = FastMCP("MySQL Checker")

@mcp.tool()
async def check_mysql_connection(
    host: str,
    user: str,
    password: str,
    database: str,
    port: int = 3306
) -> Dict:
    """
    Check MySQL database connectivity.
    
    Args:
        host: MySQL server hostname
        user: MySQL username
        password: MySQL password
        database: Database name
        port: MySQL port (default: 3306)
    
    Returns:
        Dict containing connection status and details
    """
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text("SELECT VERSION()"))
            version = result.scalar()
            
            # Get server status
            status_result = connection.execute(text("SHOW STATUS"))
            status = {row[0]: row[1] for row in status_result}
            
            return {
                "status": "success",
                "message": "MySQL connection successful",
                "details": {
                    "version": version,
                    "host": host,
                    "database": database,
                    "port": port,
                    "server_status": {
                        "connections": status.get("Threads_connected", "N/A"),
                        "running_queries": status.get("Threads_running", "N/A"),
                        "uptime": status.get("Uptime", "N/A")
                    }
                }
            }
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": f"MySQL connection failed: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "host": host,
                "database": database
            }
        }

@mcp.tool()
async def get_mysql_tables(
    host: str,
    user: str,
    password: str,
    database: str,
    port: int = 3306
) -> Dict:
    """
    Get list of all tables in the MySQL database.
    
    Args:
        host: MySQL server hostname
        user: MySQL username
        password: MySQL password
        database: Database name
        port: MySQL port (default: 3306)
    
    Returns:
        Dict containing list of tables and their details
    """
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            # Get all tables
            tables_query = """
            SELECT 
                table_name,
                table_rows,
                data_length,
                index_length,
                create_time,
                update_time
            FROM information_schema.tables 
            WHERE table_schema = :database
            """
            result = connection.execute(text(tables_query), {"database": database})
            tables = []
            for row in result:
                tables.append({
                    "name": row[0],
                    "rows": row[1],
                    "data_size": row[2],
                    "index_size": row[3],
                    "created_at": row[4],
                    "updated_at": row[5]
                })
            
            return {
                "status": "success",
                "message": f"Found {len(tables)} tables in database {database}",
                "tables": tables
            }
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": f"Failed to get tables: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "database": database
            }
        }

@mcp.tool()
async def check_mysql_processes(
    host: str,
    user: str,
    password: str,
    database: str,
    port: int = 3306
) -> Dict:
    """
    Check running MySQL processes and their status.
    
    Args:
        host: MySQL server hostname
        user: MySQL username
        password: MySQL password
        database: Database name
        port: MySQL port (default: 3306)
    
    Returns:
        Dict containing process information
    """
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            # Get process list
            result = connection.execute(text("SHOW PROCESSLIST"))
            processes = []
            for row in result:
                processes.append({
                    "id": row[0],
                    "user": row[1],
                    "host": row[2],
                    "database": row[3],
                    "command": row[4],
                    "time": row[5],
                    "state": row[6],
                    "info": row[7]
                })
            
            return {
                "status": "success",
                "message": f"Found {len(processes)} active processes",
                "processes": processes
            }
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": f"Failed to get process list: {str(e)}",
            "details": {
                "error_type": type(e).__name__,
                "database": database
            }
        }

if __name__ == "__main__":
    mcp.run(transport="sse") 