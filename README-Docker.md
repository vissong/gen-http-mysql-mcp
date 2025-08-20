# MySQL MCP Server - Docker 部署指南

本文档介绍如何使用 Docker 部署和运行 MySQL MCP 服务器。

## 📋 文件说明

- `Dockerfile` - 主要的 Docker 镜像构建文件
- `docker-compose.yml` - 开发环境配置（包含 MySQL 数据库）
- `docker-compose.prod.yml` - 生产环境配置（使用外部数据库）
- `.dockerignore` - Docker 构建时忽略的文件

- `Makefile` - 便捷的 Docker 操作命令

## 🚀 快速开始

### 开发环境

1. **启动开发环境**（包含 MySQL 数据库）：
```bash
make dev
# 或者
docker-compose up -d
```

2. **访问服务**：
   - MCP 服务器: http://localhost:8000
   - MySQL 数据库: localhost:3306
     - 用户名: `mcpuser`
     - 密码: `mcppassword`
     - 数据库: `mcp_database`

3. **查看日志**：
```bash
make logs
# 或者
docker-compose logs -f
```

### 生产环境

1. **创建环境配置文件**：
```bash
cp .env.example .env
# 编辑 .env 文件，配置生产数据库连接信息
```

2. **启动生产环境**：
```bash
make prod
# 或者
docker-compose -f docker-compose.prod.yml up -d
```

## 🛠️ 常用命令

### 使用 Makefile（推荐）

```bash
# 查看所有可用命令
make help

# 构建镜像
make build

# 启动开发环境
make dev

# 启动生产环境
make prod

# 停止服务
make stop

# 清理所有容器和数据
make clean

# 查看日志
make logs

# 进入容器 shell
make shell

# 健康检查
make test

# 重启服务
make restart

# 查看容器状态
make status
```

### 数据库操作

```bash
# 进入 MySQL shell
make db-shell

# 备份数据库
make db-backup
```

### 直接使用 Docker Compose

```bash
# 开发环境
docker-compose up -d                    # 启动
docker-compose down                     # 停止
docker-compose logs -f                  # 查看日志
docker-compose ps                       # 查看状态

# 生产环境
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml down
```

## 🔧 配置说明

### 环境变量

开发环境的环境变量在 `docker-compose.yml` 中预设。生产环境需要创建 `.env` 文件：

```bash
# 数据库配置
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database

# 连接池配置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# 超时配置
DB_CONNECT_TIMEOUT=10
DB_READ_TIMEOUT=30
DB_WRITE_TIMEOUT=30
```

### 端口配置

- **MCP 服务器**: 8000 (可在 docker-compose.yml 中修改)
- **MySQL 数据库**: 3306 (仅开发环境)

### 资源限制

生产环境配置了资源限制：
- CPU: 最大 1 核，预留 0.5 核
- 内存: 最大 512MB，预留 256MB

## 🔍 健康检查

服务包含健康检查功能：

```bash
# 检查服务健康状态
curl http://localhost:8000/health

# 使用 make 命令检查
make test
```

## 📊 监控和日志

### 查看日志

```bash
# 所有服务日志
make logs

# 仅 MCP 服务器日志
make logs-mcp

# 仅 MySQL 日志
make logs-mysql
```

### 日志配置

生产环境配置了日志轮转：
- 最大文件大小: 10MB
- 保留文件数: 3 个

## 🔒 安全配置

生产环境包含以下安全配置：
- 非特权用户运行
- 只读文件系统
- 禁用新特权
- 临时文件系统挂载

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**：
   - 检查数据库配置是否正确
   - 确认数据库服务是否运行
   - 检查网络连接

2. **端口冲突**：
   - 修改 docker-compose.yml 中的端口映射
   - 检查本地是否有其他服务占用端口

3. **容器启动失败**：
   - 查看容器日志: `make logs`
   - 检查资源使用情况: `docker stats`

### 调试命令

```bash
# 进入容器调试
make shell

# 查看容器详细信息
docker inspect mysql-mcp-server

# 查看网络配置
docker network ls
docker network inspect gen-http-mysql-mcp_mcp-network
```

## 📝 开发建议

1. **开发时使用开发环境**：包含完整的 MySQL 数据库
2. **生产部署使用生产配置**：连接外部数据库，包含安全和性能优化
3. **定期备份数据**：使用 `make db-backup` 创建数据库备份
4. **监控资源使用**：使用 `docker stats` 监控容器资源使用情况

## 🔄 更新和维护

```bash
# 更新镜像
make build

# 重启服务（保留数据）
make restart

# 完全重建（清除所有数据）
make clean
make dev
```
