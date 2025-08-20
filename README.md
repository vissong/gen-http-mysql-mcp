# MySQL MCP Server

A Model Context Protocol (MCP) server that provides secure, read-only access to MySQL databases. This server enables AI assistants and other MCP clients to interact with MySQL databases through a standardized interface.

## Features

- **Database Schema Inspection**: Get comprehensive information about all tables, columns, indexes, and constraints
- **Safe Query Execution**: Execute SELECT queries with built-in security restrictions
- **Connection Testing**: Verify database connectivity and configuration
- **Environment-based Configuration**: Secure configuration through environment variables
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Tools Provided

### 1. `get_database_schema`
Retrieves comprehensive information about all tables in the database including:
- Table names and comments
- Column definitions with data types, constraints, and comments
- Index information (primary keys, unique indexes, regular indexes)
- Table statistics (estimated row count, storage size)

### 2. `execute_sql_query`
Executes SQL SELECT queries safely with the following restrictions:
- Only SELECT statements are allowed
- Dangerous keywords (DROP, DELETE, UPDATE, etc.) are blocked
- Returns results as structured data with metadata

### 3. `execute_write_operation`
Executes SQL write operations (INSERT and UPDATE) safely with the following restrictions:
- Only INSERT and UPDATE statements are allowed
- DELETE, DROP, TRUNCATE, ALTER, CREATE operations are blocked
- Returns affected row count and last insert ID (for INSERT operations)
- Provides transaction safety with automatic commit

### 4. `test_database_connection`
Tests the database connection to ensure proper configuration and connectivity.

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd gen-http-mysql-mcp
```

2. Install dependencies using uv:
```bash
uv sync
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your MySQL database credentials:
```env
# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database

# Optional: Connection pool settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Optional: Connection timeout settings (in seconds)
DB_CONNECT_TIMEOUT=10
DB_READ_TIMEOUT=30
DB_WRITE_TIMEOUT=30
```

## Usage

### Running the Server

Start the MCP server:
```bash
uv run python main.py
```

The server will:
1. Load configuration from environment variables
2. Test the database connection
3. Start the MCP server and listen for requests

### Using with MCP Clients

This server implements the Model Context Protocol and can be used with any MCP-compatible client. The server provides three tools that can be called by MCP clients.

#### Example Tool Calls

1. **Get Database Schema**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_database_schema"
  }
}
```

2. **Execute SQL Query**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "execute_sql_query",
    "arguments": {
      "sql_query": "SELECT * FROM users LIMIT 10"
    }
  }
}
```

3. **Execute Write Operation**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "execute_write_operation",
    "arguments": {
      "sql_query": "INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')"
    }
  }
}
```

4. **Test Connection**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "test_database_connection"
  }
}
```

## Security Features

- **Controlled Write Access**: Only INSERT and UPDATE operations are permitted for write operations
- **Read Access**: SELECT queries are available through dedicated tool
- **Query Validation**: Dangerous SQL keywords (DELETE, DROP, TRUNCATE, etc.) are blocked
- **Operation Separation**: Read and write operations are handled by separate tools
- **Environment Variables**: Sensitive configuration is stored in environment variables
- **Connection Management**: Proper connection handling with timeouts and cleanup
- **Transaction Safety**: Write operations include automatic commit and error handling

## Project Structure

```
gen-http-mysql-mcp/
├── main.py              # Main server entry point
├── database.py          # Database connection and management
├── tools.py             # MCP tools implementation
├── .env.example         # Environment configuration template
├── pyproject.toml       # Project dependencies and metadata
└── README.md           # This file
```

## Dependencies

- **fastmcp**: FastMCP framework for building MCP servers
- **mysql-connector-python**: Official MySQL driver for Python
- **python-dotenv**: Environment variable loading

## Error Handling

The server includes comprehensive error handling:
- Database connection errors are logged and reported
- Invalid SQL queries are rejected with clear error messages
- Configuration validation ensures required parameters are present
- Graceful shutdown on interruption

## Logging

The server provides detailed logging including:
- Connection status and database information
- Query execution results and performance
- Error messages with context
- Server startup and shutdown events

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify your database configuration
3. Ensure your MySQL server is accessible
4. Create an issue in the repository