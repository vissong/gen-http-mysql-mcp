# 请求日志记录功能说明

## 🎯 功能概述

为了帮助调试客户端连接问题，我们添加了详细的请求日志记录中间件，可以记录：

- 📡 **HTTP 头信息** - 完整的请求头，包括 User-Agent、Content-Type 等
- 📝 **请求体内容** - MCP 请求的完整 JSON 内容
- 📤 **响应体内容** - 服务器返回的完整响应
- ⏱️ **执行时间** - 精确到毫秒的请求处理时间
- 🌐 **客户端信息** - IP 地址、User-Agent、来源等
- ❌ **错误详情** - 详细的错误信息和异常类型

## 🔧 配置选项

### 环境变量配置

```env
# 基本请求日志（生产环境推荐）
ENABLE_REQUEST_LOGGING=true

# 详细请求日志（调试时使用）
ENABLE_DETAILED_REQUEST_LOGGING=false

# 日志级别
REQUEST_LOG_LEVEL=INFO
LOG_LEVEL=INFO

# 载荷日志最大长度
MAX_PAYLOAD_LOG_LENGTH=2000
```

### 配置级别说明

1. **禁用日志** - 所有请求日志都关闭
   ```env
   ENABLE_REQUEST_LOGGING=false
   ENABLE_DETAILED_REQUEST_LOGGING=false
   ```

2. **简单日志** - 只记录基本的成功/失败信息（生产环境推荐）
   ```env
   ENABLE_REQUEST_LOGGING=true
   ENABLE_DETAILED_REQUEST_LOGGING=false
   ```

3. **详细日志** - 记录完整的请求/响应内容（调试时使用）
   ```env
   ENABLE_REQUEST_LOGGING=true
   ENABLE_DETAILED_REQUEST_LOGGING=true
   ```

## 🚀 快速开始

### 方法 1: 使用调试环境（推荐）

```bash
# 启动调试环境（自动启用详细日志）
make debug

# 查看实时日志
make logs-debug

# 只查看 MCP 服务器日志
make logs-debug-mcp
```

### 方法 2: 手动配置

```bash
# 设置环境变量
export ENABLE_DETAILED_REQUEST_LOGGING=true
export REQUEST_LOG_LEVEL=DEBUG
export LOG_LEVEL=DEBUG

# 启动服务器
uv run python main.py
```

### 方法 3: 修改配置文件

编辑 `.env` 文件：
```env
ENABLE_DETAILED_REQUEST_LOGGING=true
REQUEST_LOG_LEVEL=DEBUG
LOG_LEVEL=DEBUG
MAX_PAYLOAD_LOG_LENGTH=5000
```

## 📋 日志输出示例

### 简单日志模式
```
2024-08-21 10:00:00 - mcp.requests.simple - INFO - ✅ tools/list - 15.23ms
2024-08-21 10:00:01 - mcp.requests.simple - INFO - ✅ tools/call - 125.45ms
2024-08-21 10:00:02 - mcp.requests.simple - ERROR - ❌ tools/call - 89.12ms - ValueError: Invalid query
```

### 详细日志模式
```
2024-08-21 10:00:00 - mcp.requests - INFO - 🔵 请求开始 [tools/call] - ID: req_123456
2024-08-21 10:00:00 - mcp.requests - INFO - 📋 客户端信息 - IP: 192.168.1.100, User-Agent: MCP-Client/1.0
2024-08-21 10:00:00 - mcp.requests - INFO - 🔧 工具调用 - 名称: execute_sql_query, 参数: {
  "sql_query": "SELECT * FROM users LIMIT 5"
}
2024-08-21 10:00:00 - mcp.requests - INFO - 🟢 请求成功 [tools/call] - ID: req_123456, 耗时: 125.45ms
```

### 错误日志示例
```
2024-08-21 10:00:00 - mcp.requests - ERROR - 🔴 请求失败 [tools/call] - ID: req_123456, 耗时: 89.12ms, 错误: ValueError: Invalid SQL query
```

## 🔍 调试技巧

### 1. 过滤特定类型的日志

```bash
# 只查看错误日志
make logs-debug | grep "🔴"

# 只查看工具调用
make logs-debug | grep "🔧"

# 只查看客户端信息
make logs-debug | grep "📋"
```

### 2. 分析性能问题

```bash
# 查看执行时间超过 1 秒的请求
make logs-debug | grep -E "耗时: [0-9]{4,}\.[0-9]+ms"

# 按执行时间排序
make logs-debug | grep "耗时:" | sort -k6 -nr
```

### 3. 统计请求模式

```bash
# 统计请求类型
make logs-debug | grep "请求开始" | awk '{print $6}' | sort | uniq -c

# 统计客户端 IP
make logs-debug | grep "客户端信息" | awk -F'IP: ' '{print $2}' | awk '{print $1}' | sort | uniq -c
```

## 🛠️ 常见问题诊断

### 客户端连接问题
**查找日志**：
- 是否有 "请求开始" 日志？
- 客户端 IP 和 User-Agent 是什么？
- 是否有认证相关的错误？

### 请求格式问题
**查找日志**：
- 工具名称是否正确？
- 参数格式是否符合预期？
- 是否有 JSON 解析错误？

### 性能问题
**查找日志**：
- 哪些请求耗时最长？
- 是否有数据库连接超时？
- 是否有重复的慢查询？

## ⚡ 性能影响

### 简单日志模式
- **性能影响**: 极小（< 1ms）
- **存储需求**: 低
- **适用场景**: 生产环境

### 详细日志模式
- **性能影响**: 小（1-5ms）
- **存储需求**: 中等
- **适用场景**: 开发和调试环境

### 建议配置

**生产环境**:
```env
ENABLE_REQUEST_LOGGING=true
ENABLE_DETAILED_REQUEST_LOGGING=false
REQUEST_LOG_LEVEL=INFO
MAX_PAYLOAD_LOG_LENGTH=1000
```

**开发环境**:
```env
ENABLE_REQUEST_LOGGING=true
ENABLE_DETAILED_REQUEST_LOGGING=true
REQUEST_LOG_LEVEL=DEBUG
MAX_PAYLOAD_LOG_LENGTH=5000
```

**性能测试**:
```env
ENABLE_REQUEST_LOGGING=false
ENABLE_DETAILED_REQUEST_LOGGING=false
```

## 📚 相关文档

- [DEBUG_GUIDE.md](DEBUG_GUIDE.md) - 详细的调试指南
- [README.md](README.md) - 项目主要文档
- [INSTRUCT_CHANGELOG.md](INSTRUCT_CHANGELOG.md) - 变更记录
