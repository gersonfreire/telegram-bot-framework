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
    name: Optional[Union[str, List[str]]] = None,
    description: str = "",
    admin_only: bool = False,
    user_only: bool = False,
    aliases: Optional[List[str]] = None,
    hidden: bool = False,
    category: str = "general",
    framework = None
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
        framework: Framework instance to register the command with
    
    Usage:
        @command(name="hello", description="Comando de saudação")
        async def hello_command(self, update, context):
            await update.message.reply_text("Olá!")
    """
    def decorator(func: Callable):
        # Handle list of command names
        command_names = []
        if isinstance(name, list):
            command_names = name
            primary_name = command_names[0] if command_names else func.__name__
        else:
            primary_name = name or func.__name__.replace("_command", "").replace("_", "")
            command_names = [primary_name]
            
        # Register command with framework if provided
        if framework:
            for cmd_name in command_names:
                framework.add_command_handler(cmd_name, func)
        else:
            # Register in global registry
            command_registry.register_command(
                name=primary_name,
                handler=func,
                description=description,
                admin_only=admin_only,
                user_only=user_only,
                aliases=aliases,
                hidden=hidden,
                category=category
            )
        
        # Adicionar metadados à função
        func._command_name = primary_name
        func._command_description = description
        func._command_admin_only = admin_only
        func._command_user_only = user_only
        func._command_aliases = aliases or []
        func._command_hidden = hidden
        func._command_category = category
        
        return func
    
    return decorator


def admin_required(user_manager=None):
    """
    Decorador que requer permissões de administrador.
    
    Args:
        user_manager: Optional user_manager instance to check admin status
        
    Usage:
        @admin_required(user_manager)
        async def admin_command(update, context):
            await update.message.reply_text("Comando administrativo!")
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not update.effective_user:
                if hasattr(update, 'message') and update.message:
                    await update.message.reply_text("❌ Erro de autenticação: usuário não identificado.")
                logger.warning(f"Tentativa de acesso admin sem usuário identificado: {func.__name__}")
                return None
                
            user_id = update.effective_user.id
            
            # Verificar se é admin
            is_admin = False
            if user_manager and hasattr(user_manager, 'is_admin'):
                is_admin = user_manager.is_admin(user_id)
            elif hasattr(context, 'bot_data') and context.bot_data.get('user_manager'):
                is_admin = context.bot_data['user_manager'].is_admin(user_id)
            elif hasattr(context, 'application') and hasattr(context.application, 'user_manager'):
                is_admin = context.application.user_manager.is_admin(user_id)
                
            if not is_admin:
                if hasattr(update, 'message') and update.message:
                    await update.message.reply_text(
                        "❌ Você não tem permissão para executar este comando."
                    )
                logger.warning(f"Usuário {user_id} tentou executar comando admin: {func.__name__}")
                return None
            
            return await func(update, context, *args, **kwargs)
        
        wrapper._requires_admin = True
        return wrapper
        
    # Handle case when decorator is used without arguments @admin_required
    if callable(user_manager):
        func = user_manager
        user_manager = None
        return decorator(func)
        
    return decorator


def user_required(user_manager=None):
    """
    Decorador que requer usuário registrado e não banido.
    
    Args:
        user_manager: Optional user_manager instance to check user status
        
    Usage:
        @user_required(user_manager)
        async def user_command(update, context):
            await update.message.reply_text("Comando para usuários registrados!")
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not update.effective_user:
                if hasattr(update, 'message') and update.message:
                    await update.message.reply_text("❌ Erro de autenticação: usuário não identificado.")
                logger.warning(f"Tentativa de acesso sem usuário identificado: {func.__name__}")
                return None
                
            user_id = update.effective_user.id
            username = update.effective_user.username
            first_name = update.effective_user.first_name
            last_name = update.effective_user.last_name
            
            if user_manager:
                # Check if user is banned
                is_banned = await user_manager.is_banned(user_id)
                if is_banned:
                    if hasattr(update, 'message') and update.message:
                        await update.message.reply_text(
                            "❌ Você está banido e não pode usar este comando."
                        )
                    logger.warning(f"Usuário banido {user_id} tentou executar comando: {func.__name__}")
                    return None
                
                # Register user if not already registered
                await user_manager.register_user(user_id, username, first_name, last_name)
                
                # Update user activity
                await user_manager.update_user_activity(user_id)
            
            return await func(update, context, *args, **kwargs)
        
        wrapper._requires_user = True
        return wrapper
        
    # Handle case when decorator is used without arguments @user_required
    if callable(user_manager):
        func = user_manager
        user_manager = None
        return decorator(func)
        
    return decorator


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


def log_command(func: Callable) -> Callable:
    """
    Decorator for logging command execution.
    
    Args:
        func: Command handler function
        
    Returns:
        Wrapped function with command logging
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        message = update.effective_message
        
        if user and message:
            command_text = message.text or "(no text)"
            user_info = f"{user.first_name} (@{user.username})" if user.username else f"{user.first_name} (ID: {user.id})"
            chat_info = f"chat {chat.title}" if chat and chat.title else f"private chat"
            
            logger.info(f"Command {command_text} from {user_info} in {chat_info}")
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def permission_required(permission_key: str):
    """
    Decorator to check if user has a specific permission.
    
    Args:
        permission_key: Key identifying the required permission
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id if update and update.effective_user else None
            
            if not user_id:
                await update.effective_message.reply_text("Authentication error: User not identified.")
                return
            
            # Access user manager through context.bot_data if available
            user_manager = context.bot_data.get('user_manager', None)
            
            if not user_manager:
                logger.error("UserManager not found in context.bot_data")
                await update.effective_message.reply_text("Error: User management system not available.")
                return
            
            # Check if user has the required permission
            if not await user_manager.has_permission(user_id, permission_key):
                logger.warning(f"Permission denied: User {user_id} tried to access {permission_key}")
                await update.effective_message.reply_text("Permission denied: You don't have access to this feature.")
                return
            
            return await func(update, context, *args, **kwargs)
            
        return wrapper
    
    return decorator


def get_command_registry() -> CommandRegistry:
    """Retorna o registry global de comandos."""
    return command_registry
