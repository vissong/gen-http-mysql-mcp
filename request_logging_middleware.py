"""
请求日志中间件

提供详细的请求和响应日志记录，包括：
- HTTP 头信息
- 请求体内容
- 响应内容
- 执行时间
- 错误信息
"""

import json
import time
import logging
from typing import Any, Dict, Optional
from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class DetailedRequestLoggingMiddleware(Middleware):
    """
    详细的请求日志中间件
    
    记录所有 MCP 请求和响应的详细信息，包括：
    - 请求方法和参数
    - HTTP 头信息（如果可用）
    - 执行时间
    - 响应内容
    - 错误信息
    """
    
    def __init__(
        self,
        include_headers: bool = True,
        include_payloads: bool = True,
        max_payload_length: int = 2000,
        log_level: str = "INFO"
    ):
        """
        初始化请求日志中间件
        
        Args:
            include_headers: 是否记录 HTTP 头信息
            include_payloads: 是否记录请求和响应内容
            max_payload_length: 最大记录的内容长度
            log_level: 日志级别
        """
        self.include_headers = include_headers
        self.include_payloads = include_payloads
        self.max_payload_length = max_payload_length
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # 设置专用的请求日志记录器
        self.request_logger = logging.getLogger("mcp.requests")
        self.request_logger.setLevel(self.log_level)
    
    def _format_payload(self, payload: Any) -> str:
        """格式化载荷内容用于日志记录"""
        try:
            if payload is None:
                return "None"
            
            # 尝试序列化为 JSON
            json_str = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
            
            # 如果内容太长，截断并添加省略号
            if len(json_str) > self.max_payload_length:
                json_str = json_str[:self.max_payload_length] + "...[TRUNCATED]"
            
            return json_str
        except Exception as e:
            return f"<无法序列化: {str(e)}>"
    
    def _extract_headers(self, context: MiddlewareContext) -> Dict[str, Any]:
        """提取 HTTP 头信息"""
        headers = {}
        try:
            # 尝试从上下文中提取头信息
            if hasattr(context, 'request') and hasattr(context.request, 'headers'):
                headers = dict(context.request.headers)
            elif hasattr(context, 'headers'):
                headers = dict(context.headers)
            elif hasattr(context, 'fastmcp_context') and context.fastmcp_context:
                # 尝试从 FastMCP 上下文中获取
                if hasattr(context.fastmcp_context, 'request'):
                    request = context.fastmcp_context.request
                    if hasattr(request, 'headers'):
                        headers = dict(request.headers)
        except Exception as e:
            logger.debug(f"无法提取头信息: {e}")
        
        return headers
    
    def _get_client_info(self, context: MiddlewareContext) -> Dict[str, Any]:
        """获取客户端信息"""
        client_info = {}
        try:
            # 尝试获取客户端 IP 和用户代理
            headers = self._extract_headers(context)
            
            if headers:
                client_info['user_agent'] = headers.get('user-agent', 'Unknown')
                client_info['content_type'] = headers.get('content-type', 'Unknown')
                client_info['accept'] = headers.get('accept', 'Unknown')
                
                # 获取客户端 IP（考虑代理）
                client_ip = (
                    headers.get('x-forwarded-for', '').split(',')[0].strip() or
                    headers.get('x-real-ip', '') or
                    headers.get('remote-addr', 'Unknown')
                )
                client_info['client_ip'] = client_ip
            
            # 尝试获取会话信息
            if hasattr(context, 'source'):
                client_info['source'] = context.source
            
        except Exception as e:
            logger.debug(f"无法获取客户端信息: {e}")
        
        return client_info
    
    async def on_message(self, context: MiddlewareContext, call_next):
        """处理所有 MCP 消息的日志记录"""
        start_time = time.perf_counter()
        request_id = getattr(context, 'request_id', 'unknown')
        method = getattr(context, 'method', 'unknown')
        
        # 获取客户端信息
        client_info = self._get_client_info(context)
        
        # 记录请求开始
        log_data = {
            "event": "request_start",
            "request_id": request_id,
            "method": method,
            "timestamp": time.time(),
            "client_info": client_info
        }
        
        if self.include_headers:
            headers = self._extract_headers(context)
            if headers:
                log_data["headers"] = headers
        
        if self.include_payloads and hasattr(context, 'message'):
            log_data["request_payload"] = self._format_payload(context.message)
        
        self.request_logger.log(
            self.log_level,
            f"🔵 请求开始 [{method}] - ID: {request_id}",
            extra={"mcp_request_data": log_data}
        )
        
        # 详细的请求信息日志
        if client_info:
            self.request_logger.info(
                f"📋 客户端信息 - IP: {client_info.get('client_ip', 'Unknown')}, "
                f"User-Agent: {client_info.get('user_agent', 'Unknown')}"
            )
        
        try:
            # 执行请求
            result = await call_next(context)
            
            # 计算执行时间
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # 记录成功响应
            response_log_data = {
                "event": "request_success",
                "request_id": request_id,
                "method": method,
                "duration_ms": round(duration_ms, 2),
                "timestamp": time.time()
            }
            
            if self.include_payloads:
                response_log_data["response_payload"] = self._format_payload(result)
            
            self.request_logger.log(
                self.log_level,
                f"🟢 请求成功 [{method}] - ID: {request_id}, 耗时: {duration_ms:.2f}ms",
                extra={"mcp_response_data": response_log_data}
            )
            
            return result
            
        except Exception as error:
            # 计算执行时间
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # 记录错误响应
            error_log_data = {
                "event": "request_error",
                "request_id": request_id,
                "method": method,
                "duration_ms": round(duration_ms, 2),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": time.time()
            }
            
            self.request_logger.error(
                f"🔴 请求失败 [{method}] - ID: {request_id}, 耗时: {duration_ms:.2f}ms, "
                f"错误: {type(error).__name__}: {str(error)}",
                extra={"mcp_error_data": error_log_data}
            )
            
            # 重新抛出异常
            raise
    
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """专门处理工具调用的详细日志"""
        tool_name = getattr(context.message, 'name', 'unknown') if hasattr(context, 'message') else 'unknown'
        tool_args = getattr(context.message, 'arguments', {}) if hasattr(context, 'message') else {}
        
        self.request_logger.info(
            f"🔧 工具调用 - 名称: {tool_name}, 参数: {self._format_payload(tool_args)}"
        )
        
        return await call_next(context)


class SimpleRequestLoggingMiddleware(Middleware):
    """
    简化的请求日志中间件
    
    提供基本的请求日志记录，适用于生产环境
    """
    
    def __init__(self):
        self.request_logger = logging.getLogger("mcp.requests.simple")
    
    async def on_message(self, context: MiddlewareContext, call_next):
        """记录基本的请求信息"""
        start_time = time.perf_counter()
        method = getattr(context, 'method', 'unknown')
        
        try:
            result = await call_next(context)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            self.request_logger.info(
                f"✅ {method} - {duration_ms:.2f}ms"
            )
            
            return result
            
        except Exception as error:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            self.request_logger.error(
                f"❌ {method} - {duration_ms:.2f}ms - {type(error).__name__}: {str(error)}"
            )
            
            raise
