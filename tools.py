"""
MCP Tools for MySQL Database Operations

This module contains the MCP tools for database operations including
table description retrieval and SQL query execution.
"""

import logging
import os
import re
from typing import List, Dict, Any
from fastmcp import FastMCP
from database import get_db_manager
from request_logging_middleware import DetailedRequestLoggingMiddleware, SimpleRequestLoggingMiddleware

logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("MySQL Database MCP Server")


def _is_dangerous_sql_keyword_present(sql_query: str, dangerous_keywords: List[str]) -> tuple[bool, str]:
    """
    智能检查SQL查询中是否包含危险关键词，避免误判字符串字面量中的关键词

    Args:
        sql_query (str): 要检查的SQL查询
        dangerous_keywords (List[str]): 危险关键词列表

    Returns:
        tuple[bool, str]: (是否包含危险关键词, 发现的关键词或空字符串)
    """
    # 移除SQL注释
    # 移除单行注释 (-- 注释)
    sql_no_comments = re.sub(r'--.*?$', '', sql_query, flags=re.MULTILINE)
    # 移除多行注释 (/* 注释 */)
    sql_no_comments = re.sub(r'/\*.*?\*/', '', sql_no_comments, flags=re.DOTALL)

    # 移除字符串字面量，避免误判字符串内容
    # 处理单引号字符串
    sql_no_strings = re.sub(r"'(?:[^'\\]|\\.)*'", "''", sql_no_comments)
    # 处理双引号字符串
    sql_no_strings = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', sql_no_strings)
    # 处理反引号标识符
    sql_no_strings = re.sub(r'`(?:[^`\\\\]|\\\\.)*`', '``', sql_no_strings)

    # 转换为大写进行关键词检查
    sql_upper = sql_no_strings.upper()

    # 检查每个危险关键词
    for keyword in dangerous_keywords:
        # 使用单词边界确保完整匹配关键词，而不是部分匹配
        pattern = r'\b' + re.escape(keyword.upper()) + r'\b'
        if re.search(pattern, sql_upper):
            return True, keyword

    return False, ""

# 添加请求日志中间件
def _setup_request_logging():
    """设置请求日志中间件"""
    # 从环境变量获取日志配置
    enable_detailed_logging = os.getenv('ENABLE_DETAILED_REQUEST_LOGGING', 'false').lower() in ('true', '1', 'yes', 'on')
    enable_simple_logging = os.getenv('ENABLE_REQUEST_LOGGING', 'true').lower() in ('true', '1', 'yes', 'on')

    if enable_detailed_logging:
        # 详细日志模式（用于调试）
        detailed_middleware = DetailedRequestLoggingMiddleware(
            include_headers=True,
            include_payloads=True,
            max_payload_length=int(os.getenv('MAX_PAYLOAD_LOG_LENGTH', '2000')),
            log_level=os.getenv('REQUEST_LOG_LEVEL', 'INFO')
        )
        mcp.add_middleware(detailed_middleware)
        logger.info("已启用详细请求日志记录中间件")
    elif enable_simple_logging:
        # 简单日志模式（用于生产）
        simple_middleware = SimpleRequestLoggingMiddleware()
        mcp.add_middleware(simple_middleware)
        logger.info("已启用简单请求日志记录中间件")
    else:
        logger.info("请求日志记录中间件已禁用")

# 设置请求日志
_setup_request_logging()

# 获取数据库配置以确定是否启用写操作工具
def _is_write_operations_enabled() -> bool:
    """检查是否启用写操作工具"""
    try:
        db_manager = get_db_manager()
        return db_manager.config.enable_write_operations
    except Exception as e:
        logger.warning(f"Failed to check write operations config: {e}")
        return False


@mcp.tool()
def get_database_schema() -> List[Dict[str, Any]]:
    """
    Get basic information about all tables in the database.

    Returns only table names and comments for a quick overview of the database structure.
    For detailed table schema including columns and indexes, use get_table_schema tool.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing:
            - table_name: Name of the table
            - table_comment: Comment/description of the table
    """
    try:
        db_manager = get_db_manager()

        # 直接查询表名和注释，不获取详细信息
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            # 只获取表名和注释
            cursor.execute("""
                SELECT
                    TABLE_NAME as table_name,
                    TABLE_COMMENT as table_comment
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """, (db_manager.config.database,))

            tables = cursor.fetchall()
            cursor.close()

        # 格式化响应，只包含表名和注释
        formatted_tables = []
        for table in tables:
            formatted_table = {
                "table_name": table["table_name"],
                "table_comment": table["table_comment"] or "No comment"
            }
            formatted_tables.append(formatted_table)

        logger.info(f"Successfully retrieved basic schema for {len(formatted_tables)} tables")
        return formatted_tables

    except Exception as e:
        error_msg = f"Failed to retrieve database schema: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


@mcp.tool()
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """
    Get the complete schema information for a specific table including the CREATE TABLE statement.

    This tool provides detailed information about a specific table including:
    - The complete CREATE TABLE statement
    - Table comment and metadata

    Args:
        table_name (str): Name of the table to get schema information for

    Returns:
        Dict[str, Any]: Dictionary containing:
            - success: Boolean indicating if operation was successful
            - table_name: Name of the table
            - create_statement: Complete CREATE TABLE statement
            - message: Success or error message
    """
    try:
        # 验证输入参数
        if not table_name or not table_name.strip():
            return {
                "success": False,
                "table_name": table_name,
                "create_statement": "",
                "message": "Table name cannot be empty"
            }

        table_name = table_name.strip()

        # 获取数据库管理器并执行查询
        db_manager = get_db_manager()
        create_statement = db_manager.get_table_create_statement(table_name)

        response = {
            "success": True,
            "table_name": table_name,
            "create_statement": create_statement,
            "message": f"Successfully retrieved schema for table '{table_name}'"
        }

        logger.info(f"Successfully retrieved schema for table '{table_name}'")
        return response

    except ValueError as e:
        # 处理表名验证错误或表不存在的情况
        error_msg = str(e)
        logger.warning(f"Table schema request failed for '{table_name}': {error_msg}")
        return {
            "success": False,
            "table_name": table_name,
            "create_statement": "",
            "message": error_msg
        }

    except Exception as e:
        # 处理其他数据库错误
        error_msg = f"Failed to retrieve schema for table '{table_name}': {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "table_name": table_name,
            "create_statement": "",
            "message": error_msg
        }


@mcp.tool()
def execute_sql_query(sql_query: str) -> Dict[str, Any]:
    """
    Execute a SQL SELECT query and return the results.
    
    This tool only allows SELECT statements for security reasons.
    The query will be executed against the configured MySQL database.
    
    Args:
        sql_query (str): The SQL SELECT query to execute
        
    Returns:
        Dict[str, Any]: Dictionary containing:
            - success: Boolean indicating if query was successful
            - data: List of dictionaries representing query results
            - row_count: Number of rows returned
            - message: Success or error message
    """
    try:
        # Validate input
        if not sql_query or not sql_query.strip():
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "message": "SQL query cannot be empty"
            }
        
        # Additional validation for SELECT only
        query_stripped = sql_query.strip().upper()
        if not query_stripped.startswith('SELECT'):
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "message": "Only SELECT queries are allowed for security reasons"
            }
        
        # Check for potentially dangerous keywords using intelligent parsing
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        has_dangerous_keyword, found_keyword = _is_dangerous_sql_keyword_present(sql_query, dangerous_keywords)
        if has_dangerous_keyword:
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "message": f"Query contains forbidden keyword: {found_keyword}"
            }
        
        db_manager = get_db_manager()
        results = db_manager.execute_query(sql_query)
        
        response = {
            "success": True,
            "data": results,
            "row_count": len(results),
            "message": f"Query executed successfully. Returned {len(results)} rows."
        }
        
        logger.info(f"SQL query executed successfully: {len(results)} rows returned")
        return response
        
    except Exception as e:
        error_msg = f"Failed to execute SQL query: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "data": [],
            "row_count": 0,
            "message": error_msg
        }


def execute_write_operation(sql_query: str) -> Dict[str, Any]:
    """
    Execute a SQL write operation (INSERT or UPDATE) and return the results.

    This tool allows INSERT and UPDATE statements but blocks DELETE operations for safety.
    The query will be executed against the configured MySQL database.

    Args:
        sql_query (str): The SQL INSERT or UPDATE query to execute

    Returns:
        Dict[str, Any]: Dictionary containing:
            - success: Boolean indicating if query was successful
            - affected_rows: Number of rows affected by the operation
            - last_insert_id: Last inserted ID (for INSERT operations, None for UPDATE)
            - message: Success or error message
    """
    try:
        # Validate input
        if not sql_query or not sql_query.strip():
            return {
                "success": False,
                "affected_rows": 0,
                "last_insert_id": None,
                "message": "SQL query cannot be empty"
            }

        # Validate allowed operations
        query_stripped = sql_query.strip().upper()
        allowed_operations = ['INSERT', 'UPDATE']

        # Check if query starts with allowed operations
        is_allowed = any(query_stripped.startswith(op) for op in allowed_operations)
        if not is_allowed:
            return {
                "success": False,
                "affected_rows": 0,
                "last_insert_id": None,
                "message": "Only INSERT and UPDATE operations are allowed"
            }

        # Check for forbidden keywords using intelligent parsing
        forbidden_keywords = ['DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE']
        has_forbidden_keyword, found_keyword = _is_dangerous_sql_keyword_present(sql_query, forbidden_keywords)
        if has_forbidden_keyword:
            return {
                "success": False,
                "affected_rows": 0,
                "last_insert_id": None,
                "message": f"Query contains forbidden keyword: {found_keyword}"
            }

        # Execute the write operation
        db_manager = get_db_manager()
        result = db_manager.execute_write_operation(sql_query)

        response = {
            "success": True,
            "affected_rows": result["affected_rows"],
            "last_insert_id": result.get("last_insert_id"),
            "message": f"Write operation executed successfully. {result['affected_rows']} rows affected."
        }

        logger.info(f"Write operation executed successfully: {result['affected_rows']} rows affected")
        return response

    except Exception as e:
        error_msg = f"Failed to execute write operation: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "affected_rows": 0,
            "last_insert_id": None,
            "message": error_msg
        }


@mcp.tool()
def test_database_connection() -> Dict[str, Any]:
    """
    Test the database connection to ensure it's working properly.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - success: Boolean indicating if connection test was successful
            - message: Success or error message
            - database_name: Name of the connected database
    """
    try:
        db_manager = get_db_manager()
        is_connected = db_manager.test_connection()

        if is_connected:
            return {
                "success": True,
                "message": "Database connection test successful",
                "database_name": db_manager.config.database
            }
        else:
            return {
                "success": False,
                "message": "Database connection test failed",
                "database_name": db_manager.config.database
            }

    except Exception as e:
        error_msg = f"Database connection test error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "database_name": "Unknown"
        }


# 动态注册写操作工具（根据配置决定是否注册）
def _register_write_operation_tool():
    """根据配置动态注册写操作工具"""
    if _is_write_operations_enabled():
        logger.info("Write operations are enabled, registering execute_write_operation tool")

        # 动态注册工具
        @mcp.tool()
        def execute_write_operation_registered(sql_query: str) -> Dict[str, Any]:
            """
            Execute a SQL write operation (INSERT or UPDATE) and return the results.

            This tool allows INSERT and UPDATE statements but blocks DELETE operations for safety.
            The query will be executed against the configured MySQL database.

            Args:
                sql_query (str): The SQL INSERT or UPDATE query to execute

            Returns:
                Dict[str, Any]: Dictionary containing:
                    - success: Boolean indicating if query was successful
                    - affected_rows: Number of rows affected by the operation
                    - last_insert_id: Last inserted ID (for INSERT operations, None for UPDATE)
                    - message: Success or error message
            """
            return execute_write_operation(sql_query)
    else:
        logger.info("Write operations are disabled, execute_write_operation tool will not be available")


# 在模块加载时执行动态注册
_register_write_operation_tool()
