# 指令变更日志 (INSTRUCT_CHANGELOG)

## 2025-08-21 - 添加详细请求日志记录功能

### 变更描述
为了帮助调试客户端连接问题，添加了详细的请求日志记录中间件，可以记录客户端发送的请求、HTTP 头信息、响应内容等详细信息。

### 新增文件

1. **request_logging_middleware.py**
   - 实现了 `DetailedRequestLoggingMiddleware` 详细请求日志中间件
   - 实现了 `SimpleRequestLoggingMiddleware` 简单请求日志中间件
   - 支持记录 HTTP 头信息、请求体、响应体、执行时间等
   - 支持可配置的日志级别和内容长度限制

2. **docker-compose.debug.yml**
   - 专门用于调试的 Docker Compose 配置
   - 启用详细日志记录和写操作功能
   - 使用独立的数据卷避免与开发环境冲突

3. **DEBUG_GUIDE.md**
   - 详细的调试指南文档
   - 包含常见问题诊断步骤
   - 提供日志分析技巧和配置建议

### 修改的文件

1. **main.py**
   - 添加了 `LOG_LEVEL` 环境变量支持
   - 改进了日志配置，支持动态日志级别

2. **tools.py**
   - 集成了请求日志中间件
   - 添加了 `_setup_request_logging()` 函数来配置日志中间件
   - 支持根据环境变量动态启用不同级别的日志记录

3. **.env.example**
   - 添加了请求日志相关的环境变量配置
   - 添加了通用日志级别配置

4. **docker-compose.yml** 和 **docker-compose.prod.yml**
   - 添加了请求日志相关的环境变量
   - 添加了通用日志级别配置

5. **Makefile**
   - 添加了 `debug` 命令启动调试环境
   - 添加了 `logs-debug`、`logs-debug-mcp`、`logs-debug-mysql` 命令
   - 更新了 `stop` 和 `clean` 命令以支持调试环境

6. **README.md**
   - 添加了请求日志配置选项说明
   - 添加了详细的日志记录功能介绍
   - 添加了调试环境使用说明

### 功能特性

#### 详细请求日志记录
- **HTTP 头信息记录**: 记录客户端发送的所有 HTTP 头
- **请求体记录**: 记录完整的 MCP 请求内容
- **响应体记录**: 记录服务器响应内容
- **客户端信息**: 记录客户端 IP、User-Agent 等信息
- **执行时间**: 精确记录每个请求的处理时间
- **错误详情**: 详细记录错误信息和堆栈

#### 可配置的日志级别
- **简单日志**: 只记录基本的请求成功/失败信息
- **详细日志**: 记录完整的请求/响应内容和头信息
- **可配置长度**: 支持限制日志内容的最大长度

#### 调试环境支持
- **独立调试环境**: 专门的 Docker Compose 配置用于调试
- **便捷命令**: 通过 Makefile 提供简单的调试命令
- **实时日志**: 支持实时查看详细日志

### 环境变量配置

```env
# 请求日志配置
ENABLE_REQUEST_LOGGING=true                    # 启用基本请求日志
ENABLE_DETAILED_REQUEST_LOGGING=false          # 启用详细请求日志
REQUEST_LOG_LEVEL=INFO                         # 请求日志级别
MAX_PAYLOAD_LOG_LENGTH=2000                    # 最大载荷日志长度

# 通用日志配置
LOG_LEVEL=INFO                                 # 应用日志级别
```

### 使用方法

#### 启动调试环境
```bash
# 启动调试环境（启用详细日志）
make debug

# 查看调试日志
make logs-debug

# 只查看 MCP 服务器日志
make logs-debug-mcp
```

#### 手动配置详细日志
```bash
# 设置环境变量
export ENABLE_DETAILED_REQUEST_LOGGING=true
export REQUEST_LOG_LEVEL=DEBUG
export LOG_LEVEL=DEBUG

# 启动服务器
uv run python main.py
```

### 日志输出示例

#### 简单日志
```
2024-08-21 10:00:00 - mcp.requests.simple - INFO - ✅ tools/call - 125.45ms
2024-08-21 10:00:01 - mcp.requests.simple - ERROR - ❌ tools/call - 89.12ms - ValueError: Invalid query
```

#### 详细日志
```
2024-08-21 10:00:00 - mcp.requests - INFO - 🔵 请求开始 [tools/call] - ID: req_123456
2024-08-21 10:00:00 - mcp.requests - INFO - 📋 客户端信息 - IP: 192.168.1.100, User-Agent: MCP-Client/1.0
2024-08-21 10:00:00 - mcp.requests - INFO - 🔧 工具调用 - 名称: execute_sql_query, 参数: {"sql_query": "SELECT * FROM users LIMIT 5"}
2024-08-21 10:00:00 - mcp.requests - INFO - 🟢 请求成功 [tools/call] - ID: req_123456, 耗时: 125.45ms
```

## 2025-08-21 - 添加写操作工具控制配置

### 变更描述
增加了一个配置项 `ENABLE_WRITE_OPERATIONS`，通过该配置可以控制是否提供 `execute_write_operation` 工具。

### 修改的文件

1. **database.py**
   - 在 `DatabaseConfig` 类中添加了 `enable_write_operations` 配置项
   - 从环境变量 `ENABLE_WRITE_OPERATIONS` 读取配置，默认为 `false`
   - 支持多种布尔值格式：'true', '1', 'yes', 'on'

2. **tools.py**
   - 添加了 `_is_write_operations_enabled()` 函数来检查配置状态
   - 移除了 `execute_write_operation` 函数的 `@mcp.tool()` 装饰器
   - 添加了 `_register_write_operation_tool()` 函数来动态注册工具
   - 根据配置决定是否注册 `execute_write_operation` 工具
   - 添加了相应的日志记录

3. **.env.example**
   - 添加了 `ENABLE_WRITE_OPERATIONS=false` 配置项
   - 添加了配置说明注释

4. **docker-compose.yml**
   - 在开发环境配置中添加了 `ENABLE_WRITE_OPERATIONS: false` 环境变量

5. **docker-compose.prod.yml**
   - 在生产环境配置中添加了 `ENABLE_WRITE_OPERATIONS: ${ENABLE_WRITE_OPERATIONS:-false}` 环境变量

6. **README.md**
   - 更新了 `execute_write_operation` 工具的描述，标注为可选工具
   - 在配置示例中添加了新的环境变量
   - 添加了"Configuration Options"部分，详细说明了新配置项的作用

### 功能特性

- **安全性**: 默认情况下写操作工具是禁用的，需要显式启用
- **灵活性**: 可以通过环境变量轻松控制工具的可用性
- **向后兼容**: 现有的只读工具不受影响
- **日志记录**: 启动时会记录写操作工具的启用状态

### 使用方法

要启用写操作工具，需要在环境变量中设置：
```bash
ENABLE_WRITE_OPERATIONS=true
```

或在 `.env` 文件中设置：
```env
ENABLE_WRITE_OPERATIONS=true
```

### 安全考虑

- 即使启用了写操作工具，仍然只允许 INSERT 和 UPDATE 操作
- DELETE, DROP, TRUNCATE, ALTER, CREATE 等危险操作始终被阻止
- 默认配置为禁用状态，确保安全性
