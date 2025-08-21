# 写操作工具配置示例

本文档展示如何使用新的 `ENABLE_WRITE_OPERATIONS` 配置来控制写操作工具的可用性。

## 配置说明

`ENABLE_WRITE_OPERATIONS` 环境变量控制是否启用 `execute_write_operation` 工具：

- **默认值**: `false` (禁用写操作)
- **启用值**: `true`, `1`, `yes`, `on` (不区分大小写)
- **禁用值**: `false`, `0`, `no`, `off` 或任何其他值

## 使用示例

### 1. 只读模式（默认）

```bash
# 不设置环境变量或显式禁用
export ENABLE_WRITE_OPERATIONS=false
uv run python main.py
```

在此模式下，只有以下工具可用：
- `get_database_schema` - 获取数据库架构信息
- `execute_sql_query` - 执行 SELECT 查询
- `test_database_connection` - 测试数据库连接

### 2. 启用写操作模式

```bash
# 启用写操作工具
export ENABLE_WRITE_OPERATIONS=true
uv run python main.py
```

在此模式下，除了只读工具外，还可以使用：
- `execute_write_operation` - 执行 INSERT 和 UPDATE 操作

### 3. 使用 .env 文件配置

创建或编辑 `.env` 文件：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database

# 启用写操作（可选）
ENABLE_WRITE_OPERATIONS=true
```

### 4. Docker 环境配置

#### 开发环境
编辑 `docker-compose.yml` 文件：

```yaml
services:
  mcp-server:
    environment:
      # ... 其他配置 ...
      ENABLE_WRITE_OPERATIONS: true  # 启用写操作
```

#### 生产环境
在 `.env` 文件中设置：

```env
ENABLE_WRITE_OPERATIONS=true
```

然后使用生产配置启动：

```bash
make prod
```

## 安全注意事项

1. **默认安全**: 写操作工具默认是禁用的，确保意外启动时的安全性
2. **有限权限**: 即使启用写操作，也只允许 INSERT 和 UPDATE 操作
3. **禁止危险操作**: DELETE, DROP, TRUNCATE, ALTER, CREATE 等操作始终被阻止
4. **生产环境**: 建议在生产环境中谨慎启用写操作功能

## 日志记录

服务器启动时会记录写操作工具的状态：

```
# 禁用时
INFO - Write operations are disabled, execute_write_operation tool will not be available

# 启用时  
INFO - Write operations are enabled, registering execute_write_operation tool
```

## 故障排除

如果写操作工具没有按预期工作：

1. 检查环境变量设置：
   ```bash
   echo $ENABLE_WRITE_OPERATIONS
   ```

2. 查看服务器启动日志，确认工具注册状态

3. 确认环境变量值是否正确（支持的启用值：`true`, `1`, `yes`, `on`）
