"""
Sistema de logging avançado para o framework.

Fornece logging estruturado com suporte a múltiplos destinos incluindo
console, arquivo e Telegram.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import asyncio
from datetime import datetime


class Logger:
    """Simple logger wrapper class."""
    
    def __init__(self, name: str = "tlgfwk", config: Optional[Dict[str, Any]] = None):
        """Initialize logger."""
        self.logger = logging.getLogger(name)
        
        if config:
            level = config.get('logging.level', 'INFO')
            self.logger.setLevel(getattr(logging, level.upper()))
            
            # Add file handler if specified
            log_file = config.get('logging.file')
            if log_file:
                max_size = config.get('logging.max_file_size', 10485760)  # 10MB
                backup_count = config.get('logging.backup_count', 5)
                
                file_handler = RotatingFileHandler(
                    log_file, maxBytes=max_size, backupCount=backup_count
                )
                
                format_str = config.get('logging.format', 
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                formatter = logging.Formatter(format_str)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            
            # Add console handler if no file handler
            if not log_file and not self.logger.handlers:
                console_handler = logging.StreamHandler()
                format_str = config.get('logging.format',
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                formatter = logging.Formatter(format_str)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
        else:
            # Default setup
            if not self.logger.handlers:
                self.logger.setLevel(logging.INFO)
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, *args, **kwargs)


class TelegramLogHandler(logging.Handler):
    """Handler personalizado para enviar logs para o Telegram."""
    
    def __init__(self, bot_instance, chat_id: int, level: int = logging.WARNING):
        super().__init__(level)
        self.bot_instance = bot_instance
        self.chat_id = chat_id
        self.loop = None
    
    def emit(self, record: logging.LogRecord):
        """Envia log para o Telegram."""
        try:
            log_message = self.format(record)
            
            # Executar de forma assíncrona
            if self.loop is None or self.loop.is_closed():
                try:
                    self.loop = asyncio.get_event_loop()
                except RuntimeError:
                    self.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.loop)
            
            if self.loop.is_running():
                asyncio.create_task(self._send_message(log_message))
            else:
                self.loop.run_until_complete(self._send_message(log_message))
        
        except Exception as e:
            # Evitar loop infinito de logs
            print(f"Erro ao enviar log para Telegram: {e}", file=sys.stderr)
    
    async def _send_message(self, message: str):
        """Envia mensagem para o Telegram."""
        try:
            if self.bot_instance and hasattr(self.bot_instance, 'bot'):
                # Truncar mensagem se muito longa
                if len(message) > 4096:
                    message = message[:4090] + "..."
                
                await self.bot_instance.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🔍 **LOG**\n```\n{message}\n```",
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"Erro ao enviar mensagem para Telegram: {e}", file=sys.stderr)


class ColoredFormatter(logging.Formatter):
    """Formatter colorido para console."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        return f"{color}{log_message}{self.COLORS['RESET']}"


def setup_logging(
    config: Optional[Dict[str, Any]] = None,
    bot_instance=None
) -> logging.Logger:
    """
    Configura sistema de logging do framework.
    
    Args:
        config: Configurações de logging
        bot_instance: Instância do bot para logging via Telegram
    
    Returns:
        Logger configurado
    """
    if config is None:
        config = {}
    
    # Configurações padrão
    default_config = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "console_enabled": True,
        "file_enabled": True,
        "file_path": "logs/bot.log",
        "file_max_size": 10 * 1024 * 1024,  # 10MB
        "file_backup_count": 5,
        "telegram_enabled": False,
        "telegram_chat_id": None,
        "telegram_level": "WARNING"
    }
    
    # Merge configurações
    config = {**default_config, **config}
    
    # Configurar logger principal
    logger = logging.getLogger("tlgfwk")
    logger.setLevel(getattr(logging, config["level"].upper()))
    
    # Remover handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter padrão
    formatter = logging.Formatter(config["format"])
    
    # Handler para console
    if config["console_enabled"]:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config["level"].upper()))
        
        # Usar formatter colorido se o terminal suportar
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            console_formatter = ColoredFormatter(config["format"])
        else:
            console_formatter = formatter
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Handler para arquivo
    if config["file_enabled"]:
        # Criar diretório de logs se não existir
        log_path = Path(config["file_path"])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            config["file_path"],
            maxBytes=config["file_max_size"],
            backupCount=config["file_backup_count"],
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, config["level"].upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Handler para Telegram
    if (config["telegram_enabled"] and 
        config["telegram_chat_id"] and 
        bot_instance):
        
        telegram_handler = TelegramLogHandler(
            bot_instance,
            config["telegram_chat_id"],
            getattr(logging, config["telegram_level"].upper())
        )
        telegram_handler.setFormatter(formatter)
        logger.addHandler(telegram_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtém logger configurado.
    
    Args:
        name: Nome do logger (padrão: tlgfwk)
    
    Returns:
        Logger configurado
    """
    if name is None:
        name = "tlgfwk"
    
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin para adicionar funcionalidade de logging a classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Retorna logger da classe."""
        class_name = self.__class__.__name__
        return get_logger(f"tlgfwk.{class_name}")
    
    def log_info(self, message: str, **kwargs):
        """Log de informação."""
        self.logger.info(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log de aviso."""
        self.logger.warning(message, **kwargs)
    
    def log_error(self, message: str, exc_info=None, **kwargs):
        """Log de erro."""
        self.logger.error(message, exc_info=exc_info, **kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log de debug."""
        self.logger.debug(message, **kwargs)
    
    def log_critical(self, message: str, **kwargs):
        """Log crítico."""
        self.logger.critical(message, **kwargs)


class PerformanceLogger:
    """Logger para métricas de performance."""
    
    def __init__(self):
        self.logger = get_logger("tlgfwk.performance")
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Inicia timer para operação."""
        self.metrics[operation] = {
            "start_time": datetime.now(),
            "end_time": None,
            "duration": None
        }
    
    def end_timer(self, operation: str):
        """Finaliza timer para operação."""
        if operation in self.metrics:
            end_time = datetime.now()
            self.metrics[operation]["end_time"] = end_time
            duration = end_time - self.metrics[operation]["start_time"]
            self.metrics[operation]["duration"] = duration.total_seconds()
            
            self.logger.info(
                f"Performance: {operation} took {duration.total_seconds():.3f}s"
            )
    
    def log_metric(self, metric_name: str, value: Any):
        """Log de métrica customizada."""
        self.logger.info(f"Metric: {metric_name} = {value}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna todas as métricas coletadas."""
        return self.metrics.copy()


# Logger global para o framework
framework_logger = get_logger("tlgfwk")
performance_logger = PerformanceLogger()
