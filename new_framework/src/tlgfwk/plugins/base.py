"""
Classe base para plugins do framework.

Define a interface padrão que todos os plugins devem implementar.
"""

import abc
import inspect
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from ..utils.logger import Logger


class PluginBase(abc.ABC):
    """Classe base para todos os plugins."""
    
    def __init__(self):
        """Inicializa o plugin."""
        self.framework = None
        self.enabled = False
        self.config = {}
        self._commands = []
        self._handlers = []
    
    def get_commands(self) -> List[Dict[str, Any]]:
        """Return a list of commands supported by this plugin."""
        return self._commands
        
    def get_info(self) -> Dict[str, Any]:
        """Return information about this plugin."""
        return {
            "name": self.name if hasattr(self, 'name') else "Unknown",
            "version": self.version if hasattr(self, 'version') else "0.0.0",
            "enabled": self.enabled,
            "commands": len(self._commands),
            "handlers": len(self._handlers)
        }
        
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
        
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Nome único do plugin."""
        pass
    
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Versão do plugin."""
        pass
    
    @property
    def description(self) -> str:
        """Descrição do plugin."""
        return ""
    
    @property
    def dependencies(self) -> List[str]:
        """Lista de dependências (nome de outros plugins)."""
        return []
    
    @property
    def commands(self) -> List[Dict[str, Any]]:
        """Lista de comandos registrados pelo plugin."""
        return self._commands
    
    @property
    def handlers(self) -> List[Dict[str, Any]]:
        """Lista de handlers registrados pelo plugin."""
        return self._handlers
    
    async def initialize(self, framework, config: Dict[str, Any]) -> bool:
        """
        Inicializa o plugin com configurações.
        
        Args:
            framework: Instância do framework
            config: Configuração do plugin
            
        Returns:
            True se inicializado com sucesso, False caso contrário
        """
        self.framework = framework
        self.config = config or {}
        return True
    
    async def start(self) -> bool:
        """
        Inicia o plugin.
        
        Returns:
            True se iniciado com sucesso
        """
        self.enabled = True
        return True
    
    async def stop(self) -> bool:
        """
        Para a execução do plugin.
        
        Returns:
            True se parado com sucesso
        """
        self.enabled = False
        return True
    
    async def reload(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Recarrega o plugin com novas configurações.
        
        Args:
            config: Nova configuração para o plugin
            
        Returns:
            True se recarregado com sucesso
        """
        await self.stop()
        
        if config is not None:
            self.config = config
            
        return await self.start()
    
    def register_command(self, command_info: Dict[str, Any]) -> None:
        """
        Registra um comando oferecido pelo plugin.
        
        Args:
            command_info: Informações sobre o comando
        """
        self._commands.append(command_info)
    
    def register_handler(self, handler_info: Dict[str, Any]) -> None:
        """
        Registra um handler oferecido pelo plugin.
        
        Args:
            handler_info: Informações sobre o handler
        """
        self._handlers.append(handler_info)
    
    def get_resource_path(self, filename: str) -> Path:
        """
        Obtém o caminho para um recurso do plugin.
        
        Args:
            filename: Nome do arquivo de recurso
            
        Returns:
            Path para o recurso
        """
        module_dir = Path(inspect.getfile(self.__class__)).parent
        return module_dir / "resources" / filename
    
    async def on_update(self, update: Any, context: Any) -> None:
        """
        Método chamado para cada update recebido.
        
        Args:
            update: Update do Telegram
            context: Contexto do handler
        """
        pass
    
    async def get_periodic_tasks(self) -> List[Dict[str, Any]]:
        """
        Retorna tarefas periódicas para o agendador.
        
        Returns:
            Lista de definições de tarefas periódicas
        """
        return []
    
    async def get_plugin_status(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o status do plugin.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled
        }


# Alias for backward compatibility
BasePlugin = PluginBase
