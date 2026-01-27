"""
全局错误处理中间件和自定义异常
"""
import uuid
import traceback
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette import status

logger = logging.getLogger(__name__)


class AppError(Exception):
    """应用自定义异常基类"""
    
    def __init__(self, 
                 message: str = "应用错误",
                 status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
                 error_code: str = "INTERNAL_ERROR",
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """数据验证错误"""
    def __init__(self, message: str = "数据验证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(AppError):
    """资源未找到错误"""
    def __init__(self, message: str = "资源未找到", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class UnauthorizedError(AppError):
    """未授权错误"""
    def __init__(self, message: str = "未授权访问", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            details=details
        )


class ForbiddenError(AppError):
    """禁止访问错误"""
    def __init__(self, message: str = "禁止访问", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            details=details
        )


class RateLimitError(AppError):
    """速率限制错误"""
    def __init__(self, message: str = "请求过于频繁", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class ErrorResponse:
    """统一错误响应模型"""
    
    @staticmethod
    def create(
        request_id: str,
        message: str,
        error_code: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None,
        method: Optional[str] = None,
        timestamp: Optional[str] = None,
        stack_trace: Optional[str] = None,
        include_stack_trace: bool = False
    ) -> Dict[str, Any]:
        """创建标准错误响应"""
        response = {
            "request_id": request_id,
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {},
            },
            "timestamp": timestamp or datetime.now().isoformat(),
        }
        
        if path:
            response["path"] = path
        if method:
            response["method"] = method
        
        # 仅开发环境包含堆栈跟踪
        if include_stack_trace and stack_trace:
            response["error"]["stack_trace"] = stack_trace
        
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局请求ID和404处理中间件"""
    
    def __init__(self, app, is_development: bool = False):
        super().__init__(app)
        self.is_development = is_development
    
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 将请求ID存储在请求状态中
        request.state.request_id = request_id
        
        try:
            # 继续处理请求
            response = await call_next(request)
            
            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            
            # 检查是否是404响应，如果是则替换为自定义格式
            # 注意：这只会处理由Starlette生成的默认404响应
            # 由异常处理器生成的404响应不会被替换
            if response.status_code == 404:
                # 检查响应体是否为FastAPI默认的404响应体
                try:
                    # 读取响应体（注意：这可能会消耗响应体，但因为我们只在此处使用，所以没问题）
                    body = response.body
                    # 记录响应体以便调试
                    logger.debug(f"404响应体: {body}")
                    # 如果是FastAPI默认的404响应体（包含'Not Found'），则替换
                    if body and b'Not Found' in body:
                        logger.info(f"替换FastAPI默认404响应: {request.method} {request.url.path}")
                        
                        # 创建自定义404响应
                        error_response = ErrorResponse.create(
                            request_id=request_id,
                            message="资源未找到",
                            error_code="NOT_FOUND",
                            status_code=404,
                            path=str(request.url.path),
                            method=request.method,
                        )
                        
                        # 创建新的JSONResponse
                        from fastapi.responses import JSONResponse
                        new_response = JSONResponse(
                            status_code=404,
                            content=error_response,
                            headers={"X-Request-ID": request_id}
                        )
                        
                        # 复制原始响应的其他头部（如CORS头）
                        for key, value in response.headers.items():
                            if key.lower() not in ('content-length', 'content-type'):
                                new_response.headers[key] = value
                        
                        return new_response
                except Exception as e:
                    logger.error(f"处理404响应时出错: {e}")
            
            return response
            
        except Exception as exc:
            # 这里捕获异常是为了记录日志，然后重新抛出，让异常处理器处理
            logger.error(f"中间件捕获到异常: {type(exc).__name__}: {exc}")
            raise exc
    
    def _handle_http_exception(self, exc: HTTPException, request: Request, request_id: str):
        """处理HTTP异常"""
        error_code = self._get_error_code_from_status(exc.status_code)
        stack_trace = traceback.format_exc() if self.is_development else None
        
        error_response = ErrorResponse.create(
            request_id=request_id,
            message=exc.detail if isinstance(exc.detail, str) else "HTTP异常",
            error_code=error_code,
            status_code=exc.status_code,
            path=str(request.url.path),
            method=request.method,
            stack_trace=stack_trace,
            include_stack_trace=self.is_development
        )
        
        # 记录错误日志
        logger.error(
            f"HTTP异常 [ID:{request_id}] [Status:{exc.status_code}] [Path:{request.url.path}]",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "error_code": error_code,
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    def _handle_app_exception(self, exc: AppError, request: Request, request_id: str):
        """处理应用自定义异常"""
        stack_trace = traceback.format_exc() if self.is_development else None
        
        error_response = ErrorResponse.create(
            request_id=request_id,
            message=exc.message,
            error_code=exc.error_code,
            status_code=exc.status_code,
            details=exc.details,
            path=str(request.url.path),
            method=request.method,
            stack_trace=stack_trace,
            include_stack_trace=self.is_development
        )
        
        # 记录错误日志
        log_level = logging.WARNING if exc.status_code < 500 else logging.ERROR
        logger.log(
            log_level,
            f"应用异常 [ID:{request_id}] [Code:{exc.error_code}] [Status:{exc.status_code}]",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "path": request.url.path,
                "method": request.method,
                "details": exc.details,
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    def _handle_unexpected_exception(self, exc: Exception, request: Request, request_id: str):
        """处理未预期的异常"""
        stack_trace = traceback.format_exc()
        
        error_response = ErrorResponse.create(
            request_id=request_id,
            message="服务器内部错误",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            path=str(request.url.path),
            method=request.method,
            stack_trace=stack_trace,
            include_stack_trace=self.is_development
        )
        
        # 记录严重错误日志
        logger.critical(
            f"未预期异常 [ID:{request_id}] [Type:{type(exc).__name__}]",
            extra={
                "request_id": request_id,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "path": request.url.path,
                "method": request.method,
                "stack_trace": stack_trace,
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    @staticmethod
    def _get_error_code_from_status(status_code: int) -> str:
        """根据HTTP状态码获取错误代码"""
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
            504: "GATEWAY_TIMEOUT",
        }
        return error_codes.get(status_code, "UNKNOWN_ERROR")


def setup_error_handlers(app, is_development: bool = False):
    """设置错误处理中间件和异常处理器"""
    # 添加错误处理中间件
    app.add_middleware(ErrorHandlerMiddleware, is_development=is_development)
    
    # 注册HTTP异常处理器，包括404
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # 获取请求ID
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        
        error_response = ErrorResponse.create(
            request_id=request_id,
            message=exc.detail if isinstance(exc.detail, str) else "HTTP异常",
            error_code=ErrorHandlerMiddleware._get_error_code_from_status(exc.status_code),
            status_code=exc.status_code,
            path=str(request.url.path),
            method=request.method,
        )
        
        # 记录日志
        logger.warning(
            f"HTTP异常 [ID:{request_id}] [Status:{exc.status_code}] [Path:{request.url.path}]",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    # 注册通用异常处理器
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        stack_trace = traceback.format_exc() if is_development else None
        
        error_response = ErrorResponse.create(
            request_id=request_id,
            message="服务器内部错误",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            path=str(request.url.path),
            method=request.method,
            stack_trace=stack_trace,
            include_stack_trace=is_development
        )
        
        logger.critical(
            f"未处理的异常 [ID:{request_id}] [Type:{type(exc).__name__}]",
            extra={
                "request_id": request_id,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "path": request.url.path,
                "method": request.method,
                "stack_trace": stack_trace,
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    print("✅ 全局错误处理中间件和异常处理器已设置")
