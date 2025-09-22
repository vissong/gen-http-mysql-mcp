"""
MySQL MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with MySQL databases.
This server offers secure read-only access to database schema information and query execution.

Features:
- Get comprehensive database schema information (tables, columns, indexes)
- Execute SELECT queries safely
- Test database connectivity
- Environment-based configuration

Usage:
    python main.py

Environment Variables:
    DB_HOST: MySQL host (default: localhost)
    DB_PORT: MySQL port (default: 3306)
    DB_USER: MySQL username
    DB_PASSWORD: MySQL password
    DB_NAME: Database name
"""

import logging
import sys
import os
from tools import mcp

# Configure logging level from environment variable
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the MCP server"""
    try:
        logger.info("Starting MySQL MCP Server...")

        # Test database connection on startup
        from database import get_db_manager
        db_manager = get_db_manager()

        if not db_manager.test_connection():
            logger.error("Failed to connect to database. Please check your configuration.")
            sys.exit(1)

        logger.info(f"Successfully connected to database: {db_manager.config.database}")
        logger.info("MySQL MCP Server is ready to serve requests")

        # Run the MCP server
        # 从环境变量读取 transport 值，默认为 'sse'
        transport = os.getenv("MCP_TRANSPORT", "sse")
        if transport == "stdio":
            mcp.run()
        else:
            mcp.run(transport=transport, host="0.0.0.0", port=8000)

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
