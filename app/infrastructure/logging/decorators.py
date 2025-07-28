"""
Logging decorators for endpoints and error handling
"""

import functools
import time
import json
import traceback
from typing import Any, Callable, Dict
from fastapi import Request, HTTPException
from app.infrastructure.logging.logger_config import get_logger

logger = get_logger(__name__)


def log_endpoint(func: Callable) -> Callable:
    """
    Decorator to log endpoint entry, exit, and execution time
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        # Extract request info
        request_info = {}
        for arg in args:
            if isinstance(arg, Request):
                request_info = {
                    "method": arg.method,
                    "url": str(arg.url),
                    "headers": dict(arg.headers),
                    "client": arg.client.host if arg.client else "unknown",
                }
                break

        # Log function parameters (excluding sensitive data)
        safe_kwargs = {}
        for key, value in kwargs.items():
            if key.lower() in ["password", "token", "secret", "key"]:
                safe_kwargs[key] = "***REDACTED***"
            elif hasattr(value, "__dict__"):
                safe_kwargs[key] = f"<{type(value).__name__} object>"
            else:
                safe_kwargs[key] = str(value)[:100]  # Limit length

        logger.info(
            f"Endpoint start: {func.__name__}",
            extra={
                "endpoint": func.__name__,
                "endpoint_args": [
                    str(arg)[:100] for arg in args if not isinstance(arg, Request)
                ],
                "endpoint_kwargs": safe_kwargs,
                "request_info": request_info,
            },
        )

        start_time = time.time()

        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time

            logger.info(
                f"Endpoint success: {func.__name__} ({execution_time:.3f}s)",
                extra={
                    "endpoint": func.__name__,
                    "execution_time": execution_time,
                    "result_type": type(result).__name__,
                },
            )

            return result

        except HTTPException as e:
            execution_time = time.time() - start_time
            logger.warning(
                f"Endpoint HTTP error: {func.__name__} ({execution_time:.3f}s)",
                extra={
                    "endpoint": func.__name__,
                    "execution_time": execution_time,
                    "status_code": e.status_code,
                    "detail": e.detail,
                },
            )
            raise

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Endpoint error: {func.__name__} ({execution_time:.3f}s)",
                extra={
                    "endpoint": func.__name__,
                    "execution_time": execution_time,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc(),
                },
            )
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        logger.info(f"Function start: {func.__name__}")
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Function success: {func.__name__} ({execution_time:.3f}s)")
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function error: {func.__name__} ({execution_time:.3f}s)",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc(),
                },
            )
            raise

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def log_errors(func: Callable) -> Callable:
    """
    Decorator to log errors with detailed information
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Unexpected error in {func.__name__}",
                extra={
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "function_args": [str(arg)[:100] for arg in args],
                    "function_kwargs": {k: str(v)[:100] for k, v in kwargs.items()},
                    "traceback": traceback.format_exc(),
                },
                exc_info=True,
            )
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Unexpected error in {func.__name__}",
                extra={
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "function_args": [str(arg)[:100] for arg in args],
                    "function_kwargs": {k: str(v)[:100] for k, v in kwargs.items()},
                    "traceback": traceback.format_exc(),
                },
                exc_info=True,
            )
            raise

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Import asyncio at the end to avoid circular imports
import asyncio
