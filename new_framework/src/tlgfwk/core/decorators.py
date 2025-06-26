"""
Sistema de decoradores para comandos e permissões.

Fornece decoradores para facilitar o registro de comandos e controle de acesso.
"""

import functools
import inspect
import time
from typing import Callable, Optional, List, Dict, Any, Union
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CommandRegistry:
    """Registry global para comandos registrados."""
    
    def __init__(self):
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.admin_commands: List[str] = []
        self.user_commands: List[str] = []
    
    def register_command(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        admin_only: bool = False,
        user_only: bool = False,
        aliases: Optional[List[str]] = None,
        hidden: bool = False,
        category: str = "general"
    ):
        """Registra um comando no registry."""
        command_info = {
            "name": name,
            "handler": handler,
            "description": description,
            "admin_only": admin_only,
            "user_only": user_only,
            "aliases": aliases or [],
            "hidden": hidden,
            "category": category,
            "module": handler.__module__ if hasattr(handler, "__module__") else "unknown"
        }
        
        self.commands[name] = command_info
        
        if admin_only:
            self.admin_commands.append(name)
        else:
            self.user_commands.append(name)
        
        logger.debug(f"Comando registrado: {name}")
    
    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um comando."""
        return self.commands.get(name)
    
    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Retorna todos os comandos registrados."""
        return self.commands.copy()
    
    def get_user_commands(self) -> List[str]:
        """Retorna comandos disponíveis para usuários comuns."""
        return [cmd for cmd, info in self.commands.items() 
                if not info["admin_only"] and not info["hidden"]]
    
    def get_admin_commands(self) -> List[str]:
        """Retorna comandos disponíveis para administradores."""
        return [cmd for cmd, info in self.commands.items() 
                if info["admin_only"] and not info["hidden"]]


# Registry global
command_registry = CommandRegistry()


def command(
    name: Optional[str] = None,
    description: str = "",
    admin_only: bool = False,
    user_only: bool = False,
    aliases: Optional[List[str]] = None,
    hidden: bool = False,
    category: str = "general"
):
    """
    Decorador para registrar comandos.
    
    Args:
        name: Nome do comando (padrão: nome da função)
        description: Descrição do comando
        admin_only: Se True, comando disponível apenas para admins
        user_only: Se True, comando disponível apenas para usuários registrados
        aliases: Lista de aliases para o comando
        hidden: Se True, comando não aparece no help
        category: Categoria do comando
    
    Usage:
        @command(name="hello", description="Comando de saudação")
        async def hello_command(self, update, context):
            await update.message.reply_text("Olá!")
    """
    def decorator(func: Callable):
        command_name = name or func.__name__.replace("_command", "").replace("_", "")
        
        # Registrar comando
        command_registry.register_command(
            name=command_name,
            handler=func,
            description=description,
            admin_only=admin_only,
            user_only=user_only,
            aliases=aliases,
            hidden=hidden,
            category=category
        )
        
        # Adicionar metadados à função
        func._command_name = command_name
        func._command_description = description
        func._command_admin_only = admin_only
        func._command_user_only = user_only
        func._command_aliases = aliases or []
        func._command_hidden = hidden
        func._command_category = category
        
        return func
    
    return decorator


def admin_required(func: Callable):
    """
    Decorador que requer permissões de administrador.
    
    Usage:
        @admin_required
        async def admin_command(self, update, context):
            await update.message.reply_text("Comando administrativo!")
    """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Verificar se é admin
        if hasattr(self, 'config') and user_id not in self.config.admin_ids:
            await update.message.reply_text(
                "❌ Você não tem permissão para executar este comando."
            )
            logger.warning(f"Usuário {user_id} tentou executar comando admin: {func.__name__}")
            return
        
        return await func(self, update, context, *args, **kwargs)
    
    wrapper._requires_admin = True
    return wrapper


def user_required(func: Callable):
    """
    Decorador que requer usuário registrado.
    
    Usage:
        @user_required
        async def user_command(self, update, context):
            await update.message.reply_text("Comando para usuários registrados!")
    """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Verificar se usuário está registrado
        if hasattr(self, 'user_manager'):
            user = await self.user_manager.get_user(user_id)
            if not user:
                await update.message.reply_text(
                    "❌ Você precisa estar registrado para usar este comando. Use /start primeiro."
                )
                logger.warning(f"Usuário não registrado {user_id} tentou executar comando: {func.__name__}")
                return
        
        return await func(self, update, context, *args, **kwargs)
    
    wrapper._requires_user = True
    return wrapper


def owner_required(func: Callable):
    """
    Decorador que requer permissões de proprietário.
    
    Usage:
        @owner_required
        async def owner_command(self, update, context):
            await update.message.reply_text("Comando do proprietário!")
    """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Verificar se é o proprietário
        if hasattr(self, 'config') and user_id != self.config.bot_owner_id:
            await update.message.reply_text(
                "❌ Apenas o proprietário do bot pode executar este comando."
            )
            logger.warning(f"Usuário {user_id} tentou executar comando owner: {func.__name__}")
            return
        
        return await func(self, update, context, *args, **kwargs)
    
    wrapper._requires_owner = True
    return wrapper


def rate_limit(max_calls: int = 5, window: int = 60):
    """
    Decorador para limitar taxa de chamadas.
    
    Args:
        max_calls: Máximo de chamadas permitidas
        window: Janela de tempo em segundos
    
    Usage:
        @rate_limit(max_calls=3, window=60)
        async def limited_command(self, update, context):
            await update.message.reply_text("Comando com rate limit!")
    """
    def decorator(func: Callable):
        # Armazenar histórico de chamadas por usuário
        call_history: Dict[int, List[float]] = {}
        
        @functools.wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            import time
            
            user_id = update.effective_user.id
            current_time = time.time()
            
            # Inicializar histórico do usuário
            if user_id not in call_history:
                call_history[user_id] = []
            
            # Remover chamadas antigas
            call_history[user_id] = [
                call_time for call_time in call_history[user_id]
                if current_time - call_time < window
            ]
            
            # Verificar limite
            if len(call_history[user_id]) >= max_calls:
                await update.message.reply_text(
                    f"⚠️ Você está fazendo muitas solicitações. "
                    f"Tente novamente em {window} segundos."
                )
                logger.warning(f"Rate limit atingido para usuário {user_id}")
                return
            
            # Registrar chamada atual
            call_history[user_id].append(current_time)
            
            return await func(self, update, context, *args, **kwargs)
        
        wrapper._rate_limited = True
        wrapper._rate_limit_config = {"max_calls": max_calls, "window": window}
        return wrapper
    
    return decorator


def typing_action(func: Callable):
    """
    Decorador que mostra ação "digitando" durante execução do comando.
    
    Usage:
        @typing_action
        async def slow_command(self, update, context):
            # Comando que demora para executar
            await asyncio.sleep(2)
            await update.message.reply_text("Concluído!")
    """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        import asyncio
        from telegram.constants import ChatAction
        
        # Iniciar ação de digitação
        typing_task = asyncio.create_task(
            context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
        )
        
        try:
            result = await func(self, update, context, *args, **kwargs)
            return result
        finally:
            # Cancelar ação de digitação
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass
    
    wrapper._shows_typing = True
    return wrapper


def log_command_usage(func: Callable):
    """
    Decorador que registra uso de comandos.
    
    Usage:
        @log_command_usage
        async def tracked_command(self, update, context):
            await update.message.reply_text("Comando rastreado!")
    """
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        command_name = getattr(func, '_command_name', func.__name__)
        
        logger.info(
            f"Comando executado: {command_name} por {user.full_name} (ID: {user.id})"
        )
        
        # Registrar no histórico se disponível
        if hasattr(self, 'user_manager'):
            await self.user_manager.log_command_usage(user.id, command_name)
        
        return await func(self, update, context, *args, **kwargs)
    
    wrapper._logs_usage = True
    return wrapper


def validate_args(min_args: int = 0, max_args: Optional[int] = None, usage_text: str = ""):
    """
    Decorador para validar argumentos de comando.
    
    Args:
        min_args: Número mínimo de argumentos
        max_args: Número máximo de argumentos (None = ilimitado)
        usage_text: Texto de uso para mostrar em caso de erro
    
    Usage:
        @validate_args(min_args=1, usage_text="Uso: /comando <argumento>")
        async def command_with_args(self, update, context):
            arg = context.args[0]
            await update.message.reply_text(f"Argumento: {arg}")
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            args_count = len(context.args)
            
            # Validar número mínimo de argumentos
            if args_count < min_args:
                error_msg = f"❌ Argumentos insuficientes. Mínimo: {min_args}, fornecidos: {args_count}"
                if usage_text:
                    error_msg += f"\n\n{usage_text}"
                await update.message.reply_text(error_msg)
                return
            
            # Validar número máximo de argumentos
            if max_args is not None and args_count > max_args:
                error_msg = f"❌ Muitos argumentos. Máximo: {max_args}, fornecidos: {args_count}"
                if usage_text:
                    error_msg += f"\n\n{usage_text}"
                await update.message.reply_text(error_msg)
                return
            
            return await func(self, update, context, *args, **kwargs)
        
        wrapper._validates_args = True
        wrapper._validation_config = {
            "min_args": min_args,
            "max_args": max_args,
            "usage_text": usage_text
        }
        return wrapper
    
    return decorator


def log_execution(func: Callable) -> Callable:
    """
    Decorator for logging function execution time and parameters.
    
    Args:
        func: The function to be decorated
        
    Returns:
        Wrapped function with logging
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        func_name = func.__name__
        
        logger.debug(f"Executing {func_name} with args: {args}, kwargs: {kwargs}")
        
        try:
            result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"Completed {func_name} in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in {func_name} after {execution_time:.3f}s: {str(e)}")
            raise
    
    return wrapper


def get_command_registry() -> CommandRegistry:
    """Retorna o registry global de comandos."""
    return command_registry
