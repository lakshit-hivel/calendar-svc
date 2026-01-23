"""
Centralized logging configuration for the Google Calendar Sync application.
Supports console logging with JSON formatting.

Usage:
    from app.core.logger import get_logger, setup_logging
    
    # Initialize logging (call once at app startup)
    setup_logging()
    
    # Get a logger instance
    logger = get_logger(__name__)
    logger.info("This is an info message")
    logger.warning("This is a warning")
    logger.error("This is an error")
    logger.debug("This is a debug message")
"""
import json
import logging
import platform
import sys
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for better parsing and monitoring."""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger_name": record.name,
            "file": record.filename,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "tags") and isinstance(record.tags, list):
            log_data["tags"] = record.tags
        
        # Add org_id if available
        if hasattr(record, "org_id"):
            log_data["org_id"] = record.org_id

        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter with colors."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Format: timestamp - level - logger - message
        formatted = (
            f"{self.formatTime(record, self.datefmt)} - "
            f"{color}{record.levelname}{self.RESET} - "
            f"{record.name} - "
            f"{record.getMessage()}"
        )
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(level: int = logging.INFO, json_format: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        level: Logging level (default: INFO)
        json_format: If True, use JSON formatter (for production). 
                    If False, use human-readable format (for development).
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Choose formatter based on environment
    if json_format:
        formatter = JSONFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
    else:
        formatter = ConsoleFormatter(
            "%(asctime)s"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that can add context (like org_id) to all log messages.
    
    Usage:
        from app.core.logger import get_logger, LoggerAdapter
        
        base_logger = get_logger(__name__)
        logger = LoggerAdapter(base_logger, {"org_id": 261004})
        logger.info("Processing...")  # Will include org_id in context
    """
    def process(self, msg, kwargs):
        # Add extra context to the message
        context = " ".join([f"{k}={v}" for k, v in self.extra.items()])
        return f"[{context}] {msg}", kwargs


# Default logger instance for convenience
# This allows: from app.core.logger import logger
logger = get_logger("gcal_sync")
