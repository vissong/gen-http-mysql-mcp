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

## 2025-08-22 - 修改 query_monthly_details 方法添加翻页拉取和进度提示

### 变更描述
修改了 `cost_import.py` 文件中的 `query_monthly_details` 方法，添加了翻页拉取逻辑和详细的进度提示功能，提升了数据导入的用户体验和可靠性。

### 修改的文件

1. **cost_import.py**
   - 重构了 `query_monthly_details` 方法，支持自动翻页拉取所有数据
   - 添加了详细的进度提示，包括页面进度和记录处理进度
   - 改进了错误处理机制，支持单条记录错误时继续处理其他记录
   - 优化了数据库事务管理，确保数据一致性

### 功能特性

#### 翻页拉取逻辑
- **自动翻页**: 自动检测总页数并循环拉取所有页面的数据
- **页面状态跟踪**: 实时显示当前处理的页面和总页数
- **断点续传**: 单个页面失败不影响其他页面的处理

#### 进度提示功能
- **页面级进度**: 显示当前处理的页面数和总页数
- **记录级进度**: 每处理100条记录显示一次进度提示
- **实时统计**: 显示每页处理的记录数和总处理记录数
- **错误跟踪**: 详细记录处理过程中的错误信息

#### 错误处理改进
- **页面级错误处理**: 单个页面请求失败时记录错误并继续处理下一页
- **记录级错误处理**: 单条记录处理失败时跳过该记录继续处理其他记录
- **事务管理**: 所有页面处理完成后统一提交事务，失败时回滚所有操作

#### 代码质量提升
- **函数文档**: 添加了详细的函数文档字符串
- **代码注释**: 增加了关键逻辑的注释说明
- **变量命名**: 使用更清晰的变量命名提高代码可读性

### 主要改进点

1. **翻页逻辑实现**
   ```python
   while True:
       # 构建当前页的请求参数
       payload = base_payload.copy()
       payload["page"] = current_page

       # 处理当前页数据...

       # 检查是否还有下一页
       if current_page >= total_pages:
           break
       current_page += 1
   ```

2. **进度提示实现**
   ```python
   # 页面级进度
   print(f"正在请求第 {current_page} 页数据...")
   print(f"成功获取第 {current_page_num}/{total_pages} 页数据，本页记录数: {len(details)}")

   # 记录级进度
   if total_records_processed % 100 == 0:
       print(f"  已处理 {total_records_processed} 条记录...")
   ```

3. **错误处理改进**
   ```python
   try:
       # 处理单条记录
       insert_bill_data(connection, bill_data)
   except Exception as e:
       print(f"  处理第 {i} 条记录时出错: {str(e)}")
       continue  # 跳过错误记录，继续处理
   ```

### 使用效果

- **用户体验**: 用户可以实时看到数据导入的进度，了解处理状态
- **可靠性**: 单个记录或页面的错误不会中断整个导入过程
- **性能**: 支持大量数据的分页处理，避免内存溢出
- **可维护性**: 代码结构更清晰，便于后续维护和扩展

## 2025-08-22 - 添加月份参数支持和数据清理功能

### 变更描述
进一步改进了 `cost_import.py` 文件中的 `query_monthly_details` 方法，添加了月份参数支持和自动数据清理功能，确保数据的准确性和一致性。

### 修改的文件

1. **cost_import.py**
   - 为 `query_monthly_details` 方法添加了 `year_month` 参数支持
   - 新增了 `delete_monthly_data` 函数用于删除指定月份的现有数据
   - 改进了命令行参数处理，支持通过命令行指定查询月份
   - 添加了参数验证和错误处理机制
   - 优化了用户提示信息，使用表情符号增强可读性

### 功能特性

#### 月份参数支持
- **灵活的月份指定**: 支持通过函数参数或命令行参数指定要查询的月份
- **参数验证**: 验证月份格式是否正确 (YYYYMM 格式)
- **默认值处理**: 未指定月份时使用默认值 202507
- **命令行支持**: 支持通过命令行参数传入月份

#### 数据清理功能
- **自动删除**: 导入新数据前自动删除该月份的现有数据
- **删除统计**: 显示删除的记录数量
- **事务安全**: 删除操作独立提交，确保数据一致性
- **错误处理**: 删除操作失败时提供详细错误信息

#### 用户体验改进
- **清晰的提示**: 使用表情符号和颜色化提示增强用户体验
- **进度跟踪**: 详细显示删除和导入的进度信息
- **参数提示**: 提供清晰的使用方法和示例
- **错误友好**: 参数错误时提供有用的错误信息和使用建议

### 主要改进点

1. **新增删除函数**
   ```python
   def delete_monthly_data(connection, year_month):
       """删除指定月份的账单数据"""
       sql = "DELETE FROM bill_data WHERE month = %s"
       with connection.cursor() as cursor:
           cursor.execute(sql, (year_month,))
           deleted_count = cursor.rowcount
           print(f"已删除 {deleted_count} 条 {year_month} 月的历史数据")
           return deleted_count
   ```

2. **参数化函数签名**
   ```python
   def query_monthly_details(year_month=None):
       """
       查询月度明细数据，支持翻页拉取和进度提示

       Args:
           year_month (int, optional): 要查询的年月，格式为 YYYYMM (如 202507)
       """
   ```

3. **参数验证逻辑**
   ```python
   if not isinstance(year_month, int) or year_month < 202001 or year_month > 209912:
       raise ValueError(f"年月参数格式错误: {year_month}，应为 YYYYMM 格式 (如 202507)")
   ```

4. **命令行参数处理**
   ```python
   if len(sys.argv) > 1:
       try:
           year_month = int(sys.argv[1])
           query_monthly_details(year_month)
       except ValueError:
           print("❌ 无效的月份参数")
           print("💡 使用方法: python cost_import.py [YYYYMM]")
   ```

### 使用方法

#### 通过命令行指定月份
```bash
# 导入 2025年7月 的数据
python cost_import.py 202507

# 导入 2025年8月 的数据
python cost_import.py 202508
```

#### 通过函数调用指定月份
```python
# 导入指定月份数据
query_monthly_details(202507)

# 使用默认月份
query_monthly_details()
```

### 安全特性

- **SQL注入防护**: 使用参数化查询防止SQL注入攻击
- **参数验证**: 严格验证输入参数的格式和范围
- **事务管理**: 删除和插入操作分别管理，确保数据一致性
- **错误隔离**: 单条记录错误不影响整体导入过程

### 数据一致性保证

- **先删后插**: 确保每次导入的数据都是最新的，避免重复数据
- **原子操作**: 删除操作独立提交，插入操作批量提交
- **回滚机制**: 插入过程中出错时自动回滚所有插入操作
- **统计信息**: 提供详细的删除和插入统计信息

## 2025-08-22 - 优化事务管理策略

### 变更描述
修改了 `cost_import.py` 文件中的事务管理策略，从统一提交改为分页提交，每处理完一页数据就提交一次事务，提高了数据库性能和数据安全性。

### 修改的文件

1. **cost_import.py**
   - 修改了事务提交策略，从最后统一提交改为每页提交
   - 为每页提交添加了独立的错误处理机制
   - 优化了最终的事务处理逻辑
   - 改进了错误提示信息，使用表情符号增强可读性

### 功能特性

#### 分页事务提交
- **即时提交**: 每页数据处理完成后立即提交事务
- **独立错误处理**: 每页提交都有独立的错误处理和回滚机制
- **进度确认**: 每页提交成功后显示确认信息
- **失败隔离**: 单页提交失败不影响已提交的其他页面数据

#### 性能优化
- **减少锁定时间**: 避免长时间的事务锁定，提高数据库并发性能
- **内存优化**: 及时释放事务资源，减少内存占用
- **故障恢复**: 程序异常中断时，已提交的页面数据不会丢失
- **并发友好**: 减少对其他数据库操作的影响

#### 错误处理改进
- **页面级回滚**: 单页提交失败时只回滚当前页面的数据
- **优雅中断**: 提交失败时优雅地中断处理流程
- **详细日志**: 提供详细的提交成功/失败信息
- **安全回滚**: 程序结束时安全处理未提交的事务

### 主要改进点

1. **每页提交逻辑**
   ```python
   # 每页处理完成后提交事务
   try:
       connection.commit()
       print(f"✅ 第 {current_page_num} 页数据已提交到数据库")
   except Exception as commit_error:
       print(f"❌ 第 {current_page_num} 页数据提交失败: {str(commit_error)}")
       connection.rollback()
       print(f"🔄 第 {current_page_num} 页数据已回滚")
       break
   ```

2. **优化的最终处理**
   ```python
   print(f"\n🎉 数据导入完成！总共成功处理 {total_records_processed} 条记录")

   except Exception as e:
       # 回滚当前未提交的事务（如果有的话）
       try:
           connection.rollback()
           print(f"🔄 已回滚未提交的事务")
       except:
           pass
       print(f"❌ 数据库操作失败: {str(e)}")
   ```

### 优势对比

#### 修改前（统一提交）
- ❌ 长时间事务锁定
- ❌ 内存占用较高
- ❌ 程序中断时数据全部丢失
- ❌ 影响数据库并发性能
- ❌ 单点故障风险高

#### 修改后（分页提交）
- ✅ 短时间事务锁定
- ✅ 内存占用优化
- ✅ 程序中断时已处理数据保留
- ✅ 提高数据库并发性能
- ✅ 故障影响范围小

### 使用场景优化

#### 大数据量导入
- **渐进式提交**: 大量数据分批提交，避免超时
- **断点续传**: 程序异常中断后可以从未处理的页面继续
- **资源友好**: 不会长时间占用数据库连接和锁

#### 并发环境
- **锁竞争减少**: 短事务减少与其他操作的锁竞争
- **响应时间**: 其他查询操作响应更快
- **系统稳定性**: 提高整体系统的稳定性

### 安全保障

- **数据一致性**: 每页数据作为一个完整的事务单元
- **原子性保证**: 单页内的所有记录要么全部成功，要么全部回滚
- **故障隔离**: 单页失败不影响其他页面的数据
- **恢复能力**: 提高了系统的故障恢复能力

### 监控和日志

- **实时反馈**: 每页提交后立即显示结果
- **进度跟踪**: 清楚地知道哪些页面已成功提交
- **错误定位**: 快速定位到具体失败的页面
- **统计准确**: 提供准确的处理和提交统计信息

## 2025-08-22 - 添加交互确认和安全控制功能

### 变更描述
为 `cost_import.py` 脚本添加了交互确认功能，在执行删除操作前要求用户确认，同时提供命令行参数来跳过确认步骤，提高了数据安全性和使用灵活性。

### 修改的文件

1. **cost_import.py**
   - 为 `query_monthly_details` 函数添加了 `skip_confirmation` 参数
   - 实现了交互式删除确认功能
   - 添加了命令行参数解析，支持 `--skip-confirm` 等参数
   - 改进了使用说明和错误处理
   - 添加了键盘中断处理

### 功能特性

#### 交互确认机制
- **二次确认**: 删除数据前要求用户明确确认操作
- **详细警告**: 显示操作的具体影响和风险提示
- **操作说明**: 清楚说明将要执行的步骤
- **用户友好**: 支持多种确认输入格式 (yes/y, no/n)

#### 安全控制
- **防误操作**: 避免意外删除重要数据
- **可逆选择**: 用户可以在确认阶段取消操作
- **清晰提示**: 明确告知操作的不可逆性
- **操作日志**: 记录用户的确认选择

#### 灵活控制
- **跳过确认**: 支持 `--skip-confirm` 参数跳过确认步骤
- **批处理友好**: 适合自动化脚本和批处理场景
- **多种参数格式**: 支持 `--skip-confirm`, `-y`, `--yes` 等参数
- **参数验证**: 严格验证命令行参数的有效性

### 主要改进点

1. **交互确认逻辑**
   ```python
   if not skip_confirmation:
       print(f"\n⚠️  警告：即将删除 {year_month} 月的所有现有数据！")
       print("🔍 这个操作将会：")
       print("   1. 删除数据库中该月份的所有账单记录")
       print("   2. 重新从API拉取该月份的最新数据")
       print("   3. 该操作不可逆转")

       while True:
           confirm = input(f"\n❓ 确认要删除 {year_month} 月的数据并重新导入吗？(yes/no): ").strip().lower()
           if confirm in ['yes', 'y']:
               break
           elif confirm in ['no', 'n']:
               print("❌ 用户取消操作，程序退出")
               return
           else:
               print("⚠️  请输入 'yes' 或 'no'")
   ```

2. **命令行参数解析**
   ```python
   for i, arg in enumerate(sys.argv[1:], 1):
       if arg in ['--skip-confirm', '-y', '--yes']:
           skip_confirmation = True
           print("🚀 启用跳过确认模式")
       elif arg.startswith('--'):
           print(f"❌ 未知参数: {arg}")
           sys.exit(1)
       else:
           year_month = int(arg)
   ```

3. **键盘中断处理**
   ```python
   try:
       query_monthly_details(year_month, skip_confirmation)
   except KeyboardInterrupt:
       print("\n\n⚠️  用户中断操作，程序退出")
       sys.exit(0)
   ```

### 使用方法

#### 交互式确认模式（默认）
```bash
# 需要用户确认删除操作
python cost_import.py 202507

# 程序会显示警告信息并要求确认
⚠️  警告：即将删除 202507 月的所有现有数据！
🔍 这个操作将会：
   1. 删除数据库中该月份的所有账单记录
   2. 重新从API拉取该月份的最新数据
   3. 该操作不可逆转

❓ 确认要删除 202507 月的数据并重新导入吗？(yes/no):
```

#### 跳过确认模式
```bash
# 跳过确认，直接执行
python cost_import.py 202507 --skip-confirm
python cost_import.py 202507 -y
python cost_import.py 202507 --yes
```

#### 查看使用帮助
```bash
# 不带参数运行显示使用方法
python cost_import.py

💡 使用方法: python cost_import.py [YYYYMM] [--skip-confirm]
💡 参数说明:
   YYYYMM           要导入的月份 (如 202507)
   --skip-confirm   跳过删除确认步骤
💡 示例:
   python cost_import.py 202507
   python cost_import.py 202507 --skip-confirm
```

### 安全特性

#### 数据保护
- **明确警告**: 清楚告知删除操作的影响范围
- **二次确认**: 防止误操作导致的数据丢失
- **操作记录**: 记录用户的确认选择
- **中断支持**: 支持 Ctrl+C 中断操作

#### 输入验证
- **严格验证**: 只接受明确的确认输入
- **循环提示**: 输入无效时重新提示
- **大小写不敏感**: 支持 YES/yes/Y/y 等格式
- **参数检查**: 验证命令行参数的有效性

### 适用场景

#### 生产环境
- **安全第一**: 默认需要确认，防止误操作
- **审计友好**: 记录操作确认过程
- **人工干预**: 允许操作员在关键步骤进行判断

#### 自动化环境
- **批处理支持**: 使用 `--skip-confirm` 参数
- **脚本集成**: 适合集成到自动化脚本中
- **无人值守**: 支持无人值守的自动化执行

### 用户体验改进

- **清晰提示**: 使用表情符号和结构化信息
- **操作指导**: 提供详细的使用说明和示例
- **错误友好**: 参数错误时给出有用的帮助信息
- **进度反馈**: 实时显示操作进度和状态

## 2025-08-25 - 修复SQL安全检查误判问题

### 变更描述
修复了SQL安全检查功能中的误判问题。原有的简单字符串包含检查会将字符串字面量中的关键词误判为危险操作，例如 `'%资源分类%'` 中的 `DELETE` 字符会被误判。现在使用智能解析来避免这种误判。

### 修改的文件

1. **tools.py**
   - 添加了 `re` 模块导入用于正则表达式处理
   - 新增了 `_is_dangerous_sql_keyword_present` 函数，实现智能SQL安全检查
   - 更新了 `execute_sql_query` 函数使用新的安全检查逻辑
   - 更新了 `execute_write_operation` 函数使用新的安全检查逻辑

2. **test_sql_security.py** (新增)
   - 创建了完整的测试脚本验证SQL安全检查功能
   - 包含安全查询和危险查询的测试用例
   - 提供详细的测试结果和统计信息

### 功能特性

#### 智能SQL解析
- **注释移除**: 自动移除SQL单行注释 (`--`) 和多行注释 (`/* */`)
- **字符串字面量处理**: 正确处理单引号、双引号和反引号字符串
- **单词边界匹配**: 使用正则表达式的单词边界确保完整关键词匹配
- **大小写不敏感**: 统一转换为大写进行关键词检查

#### 误判修复
- **字符串内容忽略**: 字符串字面量中的关键词不会被误判为危险操作
- **标识符保护**: 反引号包围的数据库标识符中的关键词不会误判
- **注释内容忽略**: SQL注释中的关键词不会影响安全检查
- **部分匹配避免**: 只匹配完整的关键词，避免部分字符串匹配

### 主要改进点

1. **智能解析函数**
   ```python
   def _is_dangerous_sql_keyword_present(sql_query: str, dangerous_keywords: List[str]) -> tuple[bool, str]:
       # 移除SQL注释
       sql_no_comments = re.sub(r'--.*?$', '', sql_query, flags=re.MULTILINE)
       sql_no_comments = re.sub(r'/\*.*?\*/', '', sql_no_comments, flags=re.DOTALL)

       # 移除字符串字面量
       sql_no_strings = re.sub(r"'(?:[^'\\]|\\.)*'", "''", sql_no_comments)
       sql_no_strings = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', sql_no_strings)
       sql_no_strings = re.sub(r'`(?:[^`\\\\]|\\\\.)*`', '``', sql_no_strings)

       # 使用单词边界进行关键词匹配
       for keyword in dangerous_keywords:
           pattern = r'\b' + re.escape(keyword.upper()) + r'\b'
           if re.search(pattern, sql_no_strings.upper()):
               return True, keyword

       return False, ""
   ```

2. **测试用例覆盖**
   - 包含字符串字面量中关键词的安全查询
   - 包含注释中关键词的安全查询
   - 包含反引号标识符的安全查询
   - 真正包含危险关键词的查询

### 测试结果

所有测试用例均通过：
- ✅ 8个安全查询正确识别为安全（无误判）
- ✅ 8个危险查询正确识别为危险（无漏检）

### 解决的问题

#### 修复前的问题
- ❌ `SELECT * FROM table WHERE col LIKE '%资源分类%'` 被误判为包含 DELETE
- ❌ `SELECT * FROM users WHERE name = 'UPDATE_USER'` 被误判为包含 UPDATE
- ❌ `SELECT * FROM logs -- comment with DROP` 被误判为包含 DROP

#### 修复后的效果
- ✅ 字符串字面量中的关键词不再误判
- ✅ SQL注释中的关键词不再误判
- ✅ 数据库标识符中的关键词不再误判
- ✅ 真正的危险关键词仍能正确识别

### 安全保障

- **向后兼容**: 保持原有的安全策略不变
- **误判消除**: 大幅减少因字符串内容导致的误判
- **检测准确**: 提高危险SQL的检测准确性
- **性能优化**: 使用高效的正则表达式处理

### 适用场景

#### 解决的实际问题
- 包含中文关键词搜索的查询不再被误判
- 用户名或数据中包含英文关键词的查询正常执行
- 复杂查询中的注释和字符串处理更准确

#### 提升的用户体验
- 减少因误判导致的查询失败
- 提高SQL工具的可用性和准确性
- 保持安全性的同时提升易用性

## 2025-08-25 - 补充 MCP_TRANSPORT 环境变量说明

### 变更描述
在环境变量配置文件和README文档中补充了 `MCP_TRANSPORT` 变量的详细说明，帮助用户了解不同传输协议的使用场景和配置方法。

### 修改的文件

1. **.env.example**
   - 添加了 `MCP_TRANSPORT=sse` 配置项
   - 添加了详细的注释说明两种传输协议的用途

2. **README.md**
   - 在配置示例中添加了 `MCP_TRANSPORT` 变量
   - 在配置选项部分添加了详细的传输协议说明
   - 在使用方法部分添加了不同传输协议的启动示例
   - 区分了HTTP传输和标准I/O传输的使用场景

3. **docker-compose.yml**
   - 添加了 `MCP_TRANSPORT: sse` 环境变量配置

4. **docker-compose.prod.yml**
   - 添加了 `MCP_TRANSPORT: ${MCP_TRANSPORT:-sse}` 环境变量配置

5. **docker-compose.debug.yml**
   - 添加了 `MCP_TRANSPORT: sse` 环境变量配置

### 功能特性

#### 传输协议支持
- **SSE传输 (默认)**: 使用Server-Sent Events over HTTP，适合大多数MCP客户端
- **标准I/O传输**: 使用标准输入输出流，适合命令行MCP客户端
- **自动协议选择**: 根据环境变量自动选择合适的传输协议
- **向后兼容**: 默认使用SSE传输，保持现有行为不变

#### 配置灵活性
- **环境变量控制**: 通过 `MCP_TRANSPORT` 环境变量轻松切换协议
- **Docker支持**: 所有Docker Compose配置都包含传输协议设置
- **生产环境友好**: 生产环境配置支持通过环境变量覆盖默认值

### 主要改进点

1. **环境变量配置**
   ```env
   # Optional: MCP Transport protocol - controls how the server communicates
   # - "sse" (default): Server-Sent Events over HTTP (recommended for most clients)
   # - "stdio": Standard input/output (for command-line MCP clients)
   MCP_TRANSPORT=sse
   ```

2. **使用方法说明**
   ```bash
   # HTTP传输（默认推荐）
   export MCP_TRANSPORT=sse
   uv run python main.py

   # 标准I/O传输（命令行客户端）
   export MCP_TRANSPORT=stdio
   uv run python main.py
   ```

3. **Docker配置更新**
   - 开发环境: `MCP_TRANSPORT: sse`
   - 生产环境: `MCP_TRANSPORT: ${MCP_TRANSPORT:-sse}`
   - 调试环境: `MCP_TRANSPORT: sse`

### 使用场景说明

#### SSE传输 (sse) - 推荐
- **适用场景**: Web应用、HTTP客户端、大多数MCP集成
- **特点**:
  - 基于HTTP协议，易于调试和监控
  - 支持跨网络通信
  - 服务器运行在 `0.0.0.0:8000`
  - 支持健康检查和负载均衡

#### 标准I/O传输 (stdio)
- **适用场景**: 命令行工具、进程间直接通信、脚本集成
- **特点**:
  - 通过标准输入输出流通信
  - 适合进程管道和脚本调用
  - 无需网络端口，更安全
  - 适合本地集成和自动化脚本

### 向后兼容性

- **默认行为**: 保持使用SSE传输，现有部署不受影响
- **配置兼容**: 未设置 `MCP_TRANSPORT` 时自动使用 `sse` 作为默认值
- **Docker兼容**: 所有现有Docker配置继续正常工作

### 文档完善

- **配置说明**: 详细说明了两种传输协议的区别和适用场景
- **使用示例**: 提供了不同传输协议的启动命令示例
- **最佳实践**: 推荐在不同场景下使用合适的传输协议

## 2025-09-02 - 调整数据库架构工具功能

### 变更描述
根据用户需求调整了数据库架构相关的工具功能，简化了 `get_database_schema` 工具的返回内容，并新增了 `get_table_schema` 工具用于获取指定表的建表语句。

### 修改的文件

1. **tools.py**
   - 重构了 `get_database_schema` 函数，简化返回内容只包含表名和注释
   - 新增了 `get_table_schema` 工具，用于获取指定表的完整建表语句
   - 更新了函数文档和注释，提高代码可读性

2. **database.py**
   - 添加了 `re` 模块导入用于正则表达式处理
   - 新增了 `get_table_create_statement` 方法，用于获取指定表的 CREATE TABLE 语句
   - 实现了表名验证和安全检查，防止SQL注入攻击
   - 添加了详细的错误处理和日志记录

### 功能特性

#### get_database_schema 工具优化
- **简化输出**: 只返回表名和注释，提供数据库结构的快速概览
- **性能提升**: 减少查询复杂度，提高响应速度
- **清晰定位**: 专注于提供数据库表的基本信息
- **使用指导**: 在文档中明确指出详细信息需使用 get_table_schema 工具

#### 新增 get_table_schema 工具
- **完整建表语句**: 返回指定表的完整 CREATE TABLE 语句
- **参数验证**: 严格验证表名格式，防止SQL注入
- **存在性检查**: 验证表是否存在于当前数据库中
- **错误处理**: 提供详细的错误信息和处理机制
- **安全防护**: 使用参数化查询和正则表达式验证

### 主要改进点

1. **简化的 get_database_schema 函数**
   ```python
   @mcp.tool()
   def get_database_schema() -> List[Dict[str, Any]]:
       """
       Get basic information about all tables in the database.

       Returns only table names and comments for a quick overview of the database structure.
       For detailed table schema including columns and indexes, use get_table_schema tool.
       """
       # 直接查询表名和注释，不获取详细信息
       cursor.execute("""
           SELECT
               TABLE_NAME as table_name,
               TABLE_COMMENT as table_comment
           FROM information_schema.TABLES
           WHERE TABLE_SCHEMA = %s
           AND TABLE_TYPE = 'BASE TABLE'
           ORDER BY TABLE_NAME
       """, (db_manager.config.database,))
   ```

2. **新增的 get_table_schema 工具**
   ```python
   @mcp.tool()
   def get_table_schema(table_name: str) -> Dict[str, Any]:
       """
       Get the complete schema information for a specific table including the CREATE TABLE statement.

       Args:
           table_name (str): Name of the table to get schema information for

       Returns:
           Dict[str, Any]: Dictionary containing:
               - success: Boolean indicating if operation was successful
               - table_name: Name of the table
               - create_statement: Complete CREATE TABLE statement
               - message: Success or error message
       """
   ```

3. **数据库层面的建表语句获取方法**
   ```python
   def get_table_create_statement(self, table_name: str) -> str:
       """
       Get the CREATE TABLE statement for a specific table

       Args:
           table_name: Name of the table to get CREATE statement for

       Returns:
           String containing the CREATE TABLE statement
       """
       # 验证表名，防止SQL注入
       if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
           raise ValueError("Table name contains invalid characters")

       # 检查表是否存在并获取建表语句
       cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
   ```

### 安全特性

#### 输入验证
- **表名格式检查**: 只允许字母、数字和下划线
- **SQL注入防护**: 使用正则表达式验证和参数化查询
- **存在性验证**: 确保表在当前数据库中存在
- **错误边界**: 详细的错误处理和用户友好的错误信息

#### 权限控制
- **只读操作**: 所有操作都是只读的，不会修改数据库结构
- **安全查询**: 使用 SHOW CREATE TABLE 等安全的系统命令
- **参数化查询**: 防止SQL注入攻击
- **异常处理**: 完善的异常捕获和处理机制

### 使用方法

#### 获取数据库概览
```python
# 获取所有表的基本信息
tables = get_database_schema()
# 返回: [{"table_name": "users", "table_comment": "用户表"}, ...]
```

#### 获取特定表的详细结构
```python
# 获取指定表的完整建表语句
schema = get_table_schema("users")
# 返回: {
#   "success": True,
#   "table_name": "users",
#   "create_statement": "CREATE TABLE `users` (...)",
#   "message": "Successfully retrieved schema for table 'users'"
# }
```

### 工具分工

#### get_database_schema
- **用途**: 快速了解数据库中有哪些表
- **返回**: 表名和注释的简单列表
- **场景**: 数据库结构探索、表名查找

#### get_table_schema
- **用途**: 获取特定表的完整结构定义
- **返回**: 完整的 CREATE TABLE 语句
- **场景**: 表结构分析、建表语句复制、结构对比

### 性能优化

- **查询简化**: get_database_schema 只查询必要字段，减少数据传输
- **按需获取**: 详细信息只在需要时通过 get_table_schema 获取
- **缓存友好**: 简单的查询结果更容易缓存
- **网络优化**: 减少不必要的数据传输

### 向后兼容

- **工具名称**: 保持 get_database_schema 工具名称不变
- **返回格式**: 保持字典格式，只是简化了内容
- **错误处理**: 保持一致的错误处理模式
- **新增功能**: get_table_schema 作为新工具，不影响现有功能
