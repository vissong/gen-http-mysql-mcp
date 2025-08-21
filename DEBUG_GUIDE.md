# MySQL MCP Server 调试指南

本指南帮助您调试客户端连接问题和请求处理问题。

## 🔍 启用详细日志记录

### 方法 1: 使用调试环境（推荐）

```bash
# 启动调试环境
make debug

# 查看详细日志
make logs-debug

# 只查看 MCP 服务器日志
make logs-debug-mcp
```

### 方法 2: 手动配置环境变量

```bash
# 设置详细日志环境变量
export ENABLE_DETAILED_REQUEST_LOGGING=true
export REQUEST_LOG_LEVEL=DEBUG
export LOG_LEVEL=DEBUG
export MAX_PAYLOAD_LOG_LENGTH=5000

# 启动服务器
uv run python main.py
```

### 方法 3: 修改 .env 文件

```env
# 启用详细请求日志
ENABLE_DETAILED_REQUEST_LOGGING=true
REQUEST_LOG_LEVEL=DEBUG
LOG_LEVEL=DEBUG
MAX_PAYLOAD_LOG_LENGTH=5000
```

## 📋 日志内容说明

### 基本请求日志
```
2024-01-01 10:00:00 - mcp.requests.simple - INFO - ✅ tools/list - 15.23ms
2024-01-01 10:00:01 - mcp.requests.simple - INFO - ✅ tools/call - 125.45ms
2024-01-01 10:00:02 - mcp.requests.simple - ERROR - ❌ tools/call - 89.12ms - ValueError: Invalid query
```

### 详细请求日志
```
2024-01-01 10:00:00 - mcp.requests - INFO - 🔵 请求开始 [tools/call] - ID: req_123456
2024-01-01 10:00:00 - mcp.requests - INFO - 📋 客户端信息 - IP: 192.168.1.100, User-Agent: MCP-Client/1.0
2024-01-01 10:00:00 - mcp.requests - INFO - 🔧 工具调用 - 名称: execute_sql_query, 参数: {"sql_query": "SELECT * FROM users LIMIT 5"}
2024-01-01 10:00:00 - mcp.requests - INFO - 🟢 请求成功 [tools/call] - ID: req_123456, 耗时: 125.45ms
```

## 🔧 常见问题诊断

### 1. 客户端连接问题

**症状**: 客户端无法连接到服务器

**检查步骤**:
```bash
# 1. 检查服务器是否运行
curl http://localhost:8000/health

# 2. 查看服务器日志
make logs-debug

# 3. 检查端口是否被占用
netstat -an | grep 8000
```

**日志中查找**:
- 服务器启动消息
- 端口绑定信息
- 连接错误信息

### 2. 认证问题

**症状**: 客户端连接被拒绝

**日志中查找**:
```
🔴 请求失败 [initialize] - 认证失败
📋 客户端信息 - IP: xxx.xxx.xxx.xxx, User-Agent: Unknown
```

**检查**:
- HTTP 头中的认证信息
- 客户端 User-Agent
- 请求来源 IP

### 3. 请求格式问题

**症状**: 请求被服务器拒绝

**日志中查找**:
```
🔧 工具调用 - 名称: unknown_tool, 参数: {...}
🔴 请求失败 [tools/call] - ToolError: Tool not found
```

**检查**:
- 工具名称是否正确
- 参数格式是否正确
- 请求体结构

### 4. 数据库连接问题

**症状**: 工具调用失败

**日志中查找**:
```
🔴 请求失败 [tools/call] - Database connection error
ERROR - Database connection error: Can't connect to MySQL server
```

**检查**:
- 数据库配置
- 网络连接
- 数据库服务状态

## 📊 日志分析技巧

### 1. 过滤特定请求
```bash
# 只查看工具调用日志
make logs-debug | grep "工具调用"

# 只查看错误日志
make logs-debug | grep "🔴"

# 查看特定客户端的请求
make logs-debug | grep "IP: 192.168.1.100"
```

### 2. 监控性能
```bash
# 查看执行时间超过 1 秒的请求
make logs-debug | grep -E "耗时: [0-9]{4,}\.[0-9]+ms"

# 查看最慢的请求
make logs-debug | grep "耗时:" | sort -k6 -nr
```

### 3. 分析请求模式
```bash
# 统计请求类型
make logs-debug | grep "请求开始" | awk '{print $6}' | sort | uniq -c

# 统计客户端
make logs-debug | grep "客户端信息" | awk -F'IP: ' '{print $2}' | awk '{print $1}' | sort | uniq -c
```

## 🛠️ 配置调优

### 生产环境日志配置
```env
# 生产环境推荐配置
ENABLE_REQUEST_LOGGING=true
ENABLE_DETAILED_REQUEST_LOGGING=false
REQUEST_LOG_LEVEL=INFO
LOG_LEVEL=INFO
MAX_PAYLOAD_LOG_LENGTH=1000
```

### 开发环境日志配置
```env
# 开发环境推荐配置
ENABLE_REQUEST_LOGGING=true
ENABLE_DETAILED_REQUEST_LOGGING=true
REQUEST_LOG_LEVEL=DEBUG
LOG_LEVEL=DEBUG
MAX_PAYLOAD_LOG_LENGTH=5000
```

### 性能测试日志配置
```env
# 性能测试时的配置
ENABLE_REQUEST_LOGGING=true
ENABLE_DETAILED_REQUEST_LOGGING=false
REQUEST_LOG_LEVEL=WARNING
LOG_LEVEL=WARNING
```

## 🚨 故障排除清单

1. **服务器启动检查**
   - [ ] 数据库连接成功
   - [ ] 端口绑定成功
   - [ ] 中间件加载成功

2. **客户端连接检查**
   - [ ] 网络连通性
   - [ ] 端口访问权限
   - [ ] HTTP 协议版本

3. **请求处理检查**
   - [ ] 请求格式正确
   - [ ] 工具名称存在
   - [ ] 参数类型正确

4. **数据库操作检查**
   - [ ] SQL 语法正确
   - [ ] 权限充足
   - [ ] 连接池状态

## 📞 获取帮助

如果问题仍然存在：

1. 收集完整的日志信息
2. 记录重现步骤
3. 提供环境配置信息
4. 在项目仓库中创建 Issue
