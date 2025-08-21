# MySQL MCP Server Makefile
# Provides convenient commands for Docker operations

.PHONY: help build run stop clean logs shell test dev prod debug

# Default target
help:
	@echo "MySQL MCP Server Docker Commands"
	@echo "================================="
	@echo "build     - Build the Docker image"
	@echo "dev       - Run development environment with MySQL"
	@echo "debug     - Run debug environment with detailed logging"
	@echo "prod      - Run production environment (requires external DB)"
	@echo "stop      - Stop all containers"
	@echo "clean     - Stop and remove containers, networks, and volumes"
	@echo "logs      - Show container logs"
	@echo "shell     - Open shell in MCP server container"
	@echo "test      - Run health check test"
	@echo "restart   - Restart the services"

# Build the Docker image
build:
	@echo "Building MySQL MCP Server image..."
	docker build -t mysql-mcp-server .

# Run development environment
dev:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "Services started. MCP Server: http://localhost:8000"
	@echo "MySQL: localhost:3306 (user: mcpuser, password: mcppassword)"

# Run debug environment
debug:
	@echo "Starting debug environment with detailed logging..."
	docker-compose -f docker-compose.debug.yml up -d
	@echo "Debug services started. MCP Server: http://localhost:8000"
	@echo "MySQL: localhost:3306 (user: mcpuser, password: mcppassword)"
	@echo "Detailed request logging is ENABLED"
	@echo "Use 'make logs-debug' to view detailed logs"

# Run production environment
prod:
	@echo "Starting production environment..."
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please create it with production database settings."; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production services started. MCP Server: http://localhost:8000"

# Stop all containers
stop:
	@echo "Stopping all containers..."
	docker-compose down
	docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
	docker-compose -f docker-compose.debug.yml down 2>/dev/null || true

# Clean up everything
clean:
	@echo "Cleaning up containers, networks, and volumes..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
	docker-compose -f docker-compose.debug.yml down -v --remove-orphans 2>/dev/null || true
	docker system prune -f

# Show logs
logs:
	@echo "Showing container logs..."
	docker-compose logs -f

# Open shell in MCP server container
shell:
	@echo "Opening shell in MCP server container..."
	docker-compose exec mcp-server /bin/bash

# Test health check
test:
	@echo "Testing MCP server health..."
	@if curl -f http://localhost:8000/health 2>/dev/null; then \
		echo "✅ MCP Server is healthy"; \
	else \
		echo "❌ MCP Server is not responding"; \
		exit 1; \
	fi

# Restart services
restart: stop dev

# Show container status
status:
	@echo "Container status:"
	docker-compose ps

# View real-time logs for specific service
logs-mcp:
	docker-compose logs -f mcp-server

logs-mysql:
	docker-compose logs -f mysql

# Debug environment logs
logs-debug:
	@echo "Showing debug environment logs..."
	docker-compose -f docker-compose.debug.yml logs -f

logs-debug-mcp:
	docker-compose -f docker-compose.debug.yml logs -f mcp-server

logs-debug-mysql:
	docker-compose -f docker-compose.debug.yml logs -f mysql

# Database operations
db-shell:
	@echo "Opening MySQL shell..."
	docker-compose exec mysql mysql -u mcpuser -pmcppassword mcp_database

# Backup database
db-backup:
	@echo "Creating database backup..."
	docker-compose exec mysql mysqldump -u mcpuser -pmcppassword mcp_database > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created: backup_$(shell date +%Y%m%d_%H%M%S).sql"
