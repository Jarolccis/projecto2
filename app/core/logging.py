import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from app.core.config import settings


class HumanReadableFormatter(logging.Formatter):
    """Formatter for human-readable logs in development."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    EMOJIS = {
        'DEBUG': '🐛',
        'INFO': '📋',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Timestamp in readable format
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Color and emoji for level
        color = self.COLORS.get(record.levelname, '')
        emoji = self.EMOJIS.get(record.levelname, '📋')
        reset = self.COLORS['RESET']
        
        # Base message
        message = f"{timestamp} {color}[{record.levelname}]{reset} {emoji} {record.getMessage()}"
        
        # Add extra context if available
        if hasattr(record, 'endpoint') and hasattr(record, 'method'):
            status_emoji = "✅" if hasattr(record, 'status_code') and record.status_code < 400 else "❌"
            duration = f"({record.process_time:.2f}ms)" if hasattr(record, 'process_time') else ""
            message += f"\n  🌐 {record.method} {record.endpoint} → {record.status_code if hasattr(record, 'status_code') else '?'} {status_emoji} {duration}"
            
            if hasattr(record, 'client_ip'):
                message += f"\n  👤 Client: {record.client_ip}"
            if hasattr(record, 'country'):
                message += f" | Country: {record.country}"
        
        # Add extra parameters from kwargs
        excluded_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'funcName', 'lineno', 'created', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process', 'exc_info', 'exc_text', 'stack_info',
            'endpoint', 'method', 'status_code', 'process_time', 'client_ip', 'country'
        }
        
        extra_params = []
        for key, value in record.__dict__.items():
            if key not in excluded_fields and not key.startswith('_'):
                extra_params.append(f"{key}={value}")
        
        if extra_params:
            message += f"\n  📊 Params: {', '.join(extra_params)}"
        
        # Add exception info if present
        if record.exc_info:
            message += f"\n{color}💥 Exception: {record.exc_info[1]}{reset}"
            if settings.debug:
                message += f"\n{self.formatException(record.exc_info)}"
        
        return message


class JSONFormatter(logging.Formatter):
    """Formatter for structured JSON logs in production."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add specific fields for HTTP requests
        if hasattr(record, 'endpoint'):
            log_entry.update({
                "endpoint": record.endpoint,
                "method": getattr(record, 'method', None),
                "status_code": getattr(record, 'status_code', None),
                "duration": getattr(record, 'process_time', None),
                "client_ip": getattr(record, 'client_ip', None),
                "country": getattr(record, 'country', None)
            })
        
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info) if settings.debug else None
            }
        
        # Add extra fields from record (but filter out noise)
        excluded_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'funcName', 'lineno', 'created', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process', 'exc_info', 'exc_text', 'stack_info'
        }
        
        for key, value in record.__dict__.items():
            if key not in log_entry and key not in excluded_fields and not key.startswith('_'):
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))


def setup_logging() -> None:
    """Setup logging configuration based on environment."""
    logger = logging.getLogger("rebate_management")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Choose formatter based on environment
    if settings.debug:
        # Development: Human-readable format with colors and emojis
        console_handler.setFormatter(HumanReadableFormatter())
    else:
        # Production: JSON format for log aggregation
        console_handler.setFormatter(JSONFormatter())
        
        # Also add file handler for production
        file_handler = logging.FileHandler("app.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    logger.addHandler(console_handler)
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the rebate_management prefix."""
    return logging.getLogger(f"rebate_management.{name}")


class LoggerMixin:
    """Mixin class to provide logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message with extra fields."""
        self.logger.info(message, extra=kwargs)
    
    def log_error(self, message: str, error: Exception = None, **kwargs: Any) -> None:
        """Log error message with extra fields."""
        extra_fields = kwargs.copy()
        if error:
            extra_fields["error_type"] = type(error).__name__
            extra_fields["error_message"] = str(error)
        self.logger.error(message, extra=extra_fields, exc_info=error is not None)
    
    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with extra fields."""
        self.logger.warning(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with extra fields."""
        self.logger.debug(message, extra=kwargs)
