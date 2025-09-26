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

### 3. `execute_write_operation` (Optional)
Executes SQL write operations (INSERT and UPDATE) safely with the following restrictions:
- Only INSERT and UPDATE statements are allowed
- DELETE, DROP, TRUNCATE, ALTER, CREATE operations are blocked
- Returns affected row count and last insert ID (for INSERT operations)
- Provides transaction safety with automatic commit
- **Note**: This tool is only available when `ENABLE_WRITE_OPERATIONS=true` is set in the configuration

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

# Optional: Database charset and collation settings
DB_CHARSET=utf8mb4
DB_COLLATION=utf8mb4_general_ci

# Optional: Enable write operations (INSERT/UPDATE) - set to true to enable
ENABLE_WRITE_OPERATIONS=false

# Optional: MCP Transport protocol
MCP_TRANSPORT=sse
```

### Configuration Options

- **ENABLE_WRITE_OPERATIONS**: Controls whether the `execute_write_operation` tool is available
  - `false` (default): Only read-only operations are allowed (SELECT queries only)
  - `true`: Enables INSERT and UPDATE operations through the `execute_write_operation` tool
  - For security reasons, DELETE, DROP, TRUNCATE, ALTER, and CREATE operations are always blocked

- **Database Character Set Configuration**:
  - **DB_CHARSET**: Database connection character set (`utf8mb4` by default)
  - **DB_COLLATION**: Database connection collation (`utf8mb4_general_ci` by default)
  - These settings ensure proper handling of Unicode characters including emojis and special symbols
  - Recommended to use `utf8mb4` charset for full UTF-8 support in MySQL

- **MCP_TRANSPORT**: Controls the communication protocol used by the MCP server
  - `sse` (default): Server-Sent Events over HTTP - recommended for most MCP clients and web-based integrations
  - `stdio`: Standard input/output - used for command-line MCP clients and direct process communication
  - When set to `sse`, the server runs on HTTP at `0.0.0.0:8000`
  - When set to `stdio`, the server communicates through standard input/output streams

- **Request Logging Configuration**:
  - **ENABLE_REQUEST_LOGGING**: Enable basic request logging (`true` by default)
  - **ENABLE_DETAILED_REQUEST_LOGGING**: Enable detailed request logging with headers and payloads (`false` by default)
  - **REQUEST_LOG_LEVEL**: Log level for request logging (`INFO` by default)
  - **MAX_PAYLOAD_LOG_LENGTH**: Maximum length of logged payloads (`2000` by default)
  - **LOG_LEVEL**: General application log level (`INFO` by default)

## Usage

### Running the Server

#### HTTP Transport (Default - Recommended)

Start the MCP server with HTTP/SSE transport:
```bash
# Using default transport (sse)
uv run python main.py

# Or explicitly set HTTP transport
export MCP_TRANSPORT=sse
uv run python main.py
```

The server will:
1. Load configuration from environment variables
2. Test the database connection
3. Start the HTTP server on `0.0.0.0:8000`
4. Accept MCP requests via Server-Sent Events

#### Standard I/O Transport

For command-line MCP clients that communicate via stdin/stdout:
```bash
export MCP_TRANSPORT=stdio
uv run python main.py
```

The server will:
1. Load configuration from environment variables
2. Test the database connection
3. Listen for MCP requests on standard input
4. Send responses to standard output

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

The server provides comprehensive logging capabilities:

### Basic Logging
- Connection status and database information
- Query execution results and performance
- Error messages with context
- Server startup and shutdown events

### Request Logging
The server includes advanced request logging middleware to help debug client connection issues:

#### Simple Request Logging (Default)
```bash
# Enabled by default, shows basic request information
ENABLE_REQUEST_LOGGING=true
```

#### Detailed Request Logging (Debug Mode)
```bash
# Enable detailed logging with headers and payloads
ENABLE_DETAILED_REQUEST_LOGGING=true
REQUEST_LOG_LEVEL=DEBUG
MAX_PAYLOAD_LOG_LENGTH=5000
LOG_LEVEL=DEBUG
```

### Docker Debug Environment
For debugging client connection issues, use the debug environment:

```bash
# Start debug environment with detailed logging
make debug

# View debug logs
make logs-debug

# View only MCP server debug logs
make logs-debug-mcp
```

The debug environment enables:
- Detailed request/response logging
- HTTP headers logging
- Request payload logging
- Response payload logging
- Execution timing
- Client information tracking

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