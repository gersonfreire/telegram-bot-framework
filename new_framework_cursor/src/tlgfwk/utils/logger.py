"""
Logging utilities for the Telegram Bot Framework.
"""

import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime


class LoggerMixin:
    """Mixin for logging functionality."""
    
    def log_info(self, message: str):
        """Log info message."""
        print(f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
    
    def log_error(self, message: str):
        """Log error message."""
        print(f"[ERROR] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
    
    def log_debug(self, message: str):
        """Log debug message."""
        print(f"[DEBUG] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
    
    def log_warning(self, message: str):
        """Log warning message."""
        print(f"[WARNING] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")


def setup_logging(config: Dict[str, Any], framework=None):
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.DEBUG if config.get("debug", True) else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/bot.log"),
            logging.StreamHandler()
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name) 