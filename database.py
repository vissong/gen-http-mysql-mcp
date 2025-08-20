"""
MySQL Database Connection Module

This module provides database connection functionality and configuration loading
for the MCP server.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.user = os.getenv('DB_USER', '')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', '')
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
        self.connect_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', '10'))
        self.read_timeout = int(os.getenv('DB_READ_TIMEOUT', '30'))
        self.write_timeout = int(os.getenv('DB_WRITE_TIMEOUT', '30'))
    
    def validate(self) -> bool:
        """Validate required configuration parameters"""
        required_fields = ['host', 'user', 'password', 'database']
        for field in required_fields:
            if not getattr(self, field):
                logger.error(f"Missing required database configuration: {field}")
                return False
        return True
    
    def get_connection_config(self) -> Dict[str, Any]:
        """Get connection configuration dictionary"""
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'connection_timeout': self.connect_timeout,
            'autocommit': True,
            'charset': 'utf8mb4',
            'use_unicode': True,
        }


class DatabaseManager:
    """Database manager class for handling MySQL connections"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        if not self.config.validate():
            raise ValueError("Invalid database configuration")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config.get_connection_config())
            logger.info("Database connection established")
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
                logger.info("Database connection closed")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries

        Args:
            query: SQL SELECT query
            params: Query parameters (optional)

        Returns:
            List of dictionaries representing query results

        Raises:
            ValueError: If query is not a SELECT statement
            mysql.connector.Error: For database errors
        """
        # Validate that this is a SELECT query
        query_stripped = query.strip().upper()
        if not query_stripped.startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                results = cursor.fetchall()
                cursor.close()
                logger.info(f"Query executed successfully, returned {len(results)} rows")
                return results
        except Error as e:
            logger.error(f"Query execution error: {e}")
            raise

    def execute_write_operation(self, query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Execute a write operation (INSERT or UPDATE) and return results

        Args:
            query: SQL INSERT or UPDATE query
            params: Query parameters (optional)

        Returns:
            Dictionary containing:
                - affected_rows: Number of rows affected
                - last_insert_id: Last inserted ID (for INSERT operations)

        Raises:
            ValueError: If query is not an INSERT or UPDATE statement
            mysql.connector.Error: For database errors
        """
        # Validate that this is an allowed write operation
        query_stripped = query.strip().upper()
        allowed_operations = ['INSERT', 'UPDATE']

        if not any(query_stripped.startswith(op) for op in allowed_operations):
            raise ValueError("Only INSERT and UPDATE operations are allowed")

        # Additional safety check for forbidden keywords
        forbidden_keywords = ['DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE']
        for keyword in forbidden_keywords:
            if keyword in query_stripped:
                raise ValueError(f"Query contains forbidden keyword: {keyword}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)

                # Get operation results
                affected_rows = cursor.rowcount
                last_insert_id = cursor.lastrowid if query_stripped.startswith('INSERT') else None

                # Commit the transaction
                conn.commit()
                cursor.close()

                logger.info(f"Write operation executed successfully, {affected_rows} rows affected")

                return {
                    "affected_rows": affected_rows,
                    "last_insert_id": last_insert_id
                }

        except Error as e:
            logger.error(f"Write operation execution error: {e}")
            raise

    def execute_batch_write_operation(self, query: str, params_list: List[tuple]) -> Dict[str, Any]:
        """
        Execute a batch write operation (INSERT/UPDATE) with multiple parameter sets

        Args:
            query: SQL query string (INSERT or UPDATE only)
            params_list: List of parameter tuples for the query

        Returns:
            Dictionary with operation results
        """
        if not params_list:
            return {"success": True, "affected_rows": 0, "message": "No data to insert"}

        # Validate query for safety
        query_stripped = query.strip().upper()
        allowed_operations = ['INSERT', 'UPDATE']

        if not any(query_stripped.startswith(op) for op in allowed_operations):
            raise ValueError("Only INSERT and UPDATE operations are allowed")

        # Additional safety check for forbidden keywords
        forbidden_keywords = ['DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE']
        for keyword in forbidden_keywords:
            if keyword in query_stripped:
                raise ValueError(f"Query contains forbidden keyword: {keyword}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Execute batch operation
                cursor.executemany(query, params_list)

                # Get operation results
                affected_rows = cursor.rowcount

                # Commit the transaction
                conn.commit()
                cursor.close()

                logger.info(f"Batch write operation executed successfully, {affected_rows} rows affected")

                return {
                    "success": True,
                    "affected_rows": affected_rows,
                    "message": f"Batch operation completed successfully"
                }

        except Error as e:
            logger.error(f"Batch write operation execution error: {e}")
            return {
                "success": False,
                "affected_rows": 0,
                "message": f"Batch operation failed: {str(e)}"
            }

    def get_table_descriptions(self) -> List[Dict[str, Any]]:
        """
        Get descriptions of all tables in the database including table comments,
        column information, and index information
        
        Returns:
            List of dictionaries containing table information
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Get all tables with their comments
                cursor.execute("""
                    SELECT 
                        TABLE_NAME as table_name,
                        TABLE_COMMENT as table_comment,
                        ENGINE as engine,
                        TABLE_ROWS as estimated_rows,
                        DATA_LENGTH as data_length,
                        INDEX_LENGTH as index_length
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """, (self.config.database,))
                
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table['table_name']
                    
                    # Get column information
                    cursor.execute("""
                        SELECT 
                            COLUMN_NAME as column_name,
                            DATA_TYPE as data_type,
                            IS_NULLABLE as is_nullable,
                            COLUMN_DEFAULT as column_default,
                            COLUMN_COMMENT as column_comment,
                            COLUMN_KEY as column_key,
                            EXTRA as extra,
                            CHARACTER_MAXIMUM_LENGTH as max_length,
                            NUMERIC_PRECISION as numeric_precision,
                            NUMERIC_SCALE as numeric_scale
                        FROM information_schema.COLUMNS 
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                        ORDER BY ORDINAL_POSITION
                    """, (self.config.database, table_name))
                    
                    table['columns'] = cursor.fetchall()
                    
                    # Get index information
                    cursor.execute("""
                        SELECT 
                            INDEX_NAME as index_name,
                            COLUMN_NAME as column_name,
                            NON_UNIQUE as non_unique,
                            SEQ_IN_INDEX as sequence,
                            INDEX_TYPE as index_type,
                            INDEX_COMMENT as index_comment
                        FROM information_schema.STATISTICS 
                        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                        ORDER BY INDEX_NAME, SEQ_IN_INDEX
                    """, (self.config.database, table_name))
                    
                    indexes = cursor.fetchall()
                    
                    # Group indexes by name
                    index_dict = {}
                    for idx in indexes:
                        idx_name = idx['index_name']
                        if idx_name not in index_dict:
                            index_dict[idx_name] = {
                                'index_name': idx_name,
                                'non_unique': idx['non_unique'],
                                'index_type': idx['index_type'],
                                'index_comment': idx['index_comment'],
                                'columns': []
                            }
                        index_dict[idx_name]['columns'].append({
                            'column_name': idx['column_name'],
                            'sequence': idx['sequence']
                        })
                    
                    table['indexes'] = list(index_dict.values())
                
                cursor.close()
                logger.info(f"Retrieved information for {len(tables)} tables")
                return tables
                
        except Error as e:
            logger.error(f"Error getting table descriptions: {e}")
            raise


# Global database manager instance
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
