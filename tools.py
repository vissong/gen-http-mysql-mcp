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
    Get comprehensive information about all tables in the database.
    
    Returns detailed information including:
    - Table names and comments
    - Column definitions with data types, constraints, and comments
    - Index information including primary keys, unique indexes, and regular indexes
    - Table statistics like estimated row count and storage size
    
    Returns:
        List[Dict[str, Any]]: List of table information dictionaries
    """
    try:
        db_manager = get_db_manager()
        tables = db_manager.get_table_descriptions()
        
        # Format the response for better readability
        formatted_tables = []
        for table in tables:
            formatted_table = {
                "table_name": table["table_name"],
                "table_comment": table["table_comment"] or "No comment",
                "engine": table["engine"],
                "estimated_rows": table["estimated_rows"],
                "data_size_bytes": table["data_length"],
                "index_size_bytes": table["index_length"],
                "columns": [],
                "indexes": []
            }
            
            # Format column information
            for col in table["columns"]:
                column_info = {
                    "name": col["column_name"],
                    "type": col["data_type"],
                    "nullable": col["is_nullable"] == "YES",
                    "default": col["column_default"],
                    "comment": col["column_comment"] or "No comment",
                    "key": col["column_key"],
                    "extra": col["extra"]
                }
                
                # Add length/precision information if available
                if col["max_length"]:
                    column_info["max_length"] = col["max_length"]
                if col["numeric_precision"]:
                    column_info["precision"] = col["numeric_precision"]
                if col["numeric_scale"]:
                    column_info["scale"] = col["numeric_scale"]
                
                formatted_table["columns"].append(column_info)
            
            # Format index information
            for idx in table["indexes"]:
                index_info = {
                    "name": idx["index_name"],
                    "unique": idx["non_unique"] == 0,
                    "type": idx["index_type"],
                    "comment": idx["index_comment"] or "No comment",
                    "columns": [col["column_name"] for col in sorted(idx["columns"], key=lambda x: x["sequence"])]
                }
                formatted_table["indexes"].append(index_info)
            
            formatted_tables.append(formatted_table)
        
        logger.info(f"Successfully retrieved schema for {len(formatted_tables)} tables")
        return formatted_tables
        
    except Exception as e:
        error_msg = f"Failed to retrieve database schema: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


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
