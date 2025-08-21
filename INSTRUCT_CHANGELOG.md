# 指令变更日志 (INSTRUCT_CHANGELOG)

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
