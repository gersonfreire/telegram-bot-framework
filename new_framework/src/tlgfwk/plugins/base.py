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
    def author(self) -> str:
        """Autor do plugin."""
        return ""
    
    @property
    def dependencies(self) -> List[str]:
        """Lista de dependências do plugin."""
        return []
    
    @property
    def min_framework_version(self) -> str:
        """Versão mínima do framework requerida."""
        return "1.0.0"
    
    def initialize(self, framework):
        """
        Inicializa o plugin com referência ao framework.
        
        Args:
            framework: Instância do framework
        """
        self.framework = framework
        self.config = self.load_config()
        self.on_load()
        self.enabled = True
        self.log_info(f"Plugin {self.name} v{self.version} carregado")
    
    def shutdown(self):
        """Finaliza o plugin."""
        if self.enabled:
            self.on_unload()
            self.enabled = False
            self.log_info(f"Plugin {self.name} descarregado")
    
    def on_load(self):
        """Executado quando o plugin é carregado."""
        pass
    
    def on_unload(self):
        """Executado quando o plugin é descarregado."""
        pass
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carrega configuração específica do plugin.
        
        Returns:
            Dicionário com configurações do plugin
        """
        # Tentar carregar do arquivo de configuração do plugin
        config_file = Path(f"config/{self.name}.json")
        if config_file.exists():
            import json
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.log_warning(f"Erro ao carregar config do plugin: {e}")
        
        return {}
    
    def save_config(self):
        """Salva configuração do plugin."""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / f"{self.name}.json"
        
        try:
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_error(f"Erro ao salvar config do plugin: {e}")
    
    def get_commands(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de comandos fornecidos pelo plugin.
        
        Returns:
            Lista de informações dos comandos
        """
        commands = []
        
        # Buscar métodos decorados com @command
        for method_name in dir(self):
            method = getattr(self, method_name)
            
            if (callable(method) and 
                hasattr(method, '_command_name')):
                
                commands.append({
                    'name': method._command_name,
                    'handler': method,
                    'description': getattr(method, '_command_description', ''),
                    'admin_only': getattr(method, '_command_admin_only', False),
                    'user_only': getattr(method, '_command_user_only', False),
                    'aliases': getattr(method, '_command_aliases', []),
                    'hidden': getattr(method, '_command_hidden', False),
                    'category': getattr(method, '_command_category', self.name),
                    'plugin': self.name
                })
        
        return commands
    
    def get_handlers(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de handlers fornecidos pelo plugin.
        
        Returns:
            Lista de handlers
        """
        return self._handlers
    
    def register_handler(self, handler_type: str, handler: Callable, **kwargs):
        """
        Registra um handler personalizado.
        
        Args:
            handler_type: Tipo do handler (message, callback_query, etc.)
            handler: Função handler
            **kwargs: Argumentos adicionais para o handler
        """
        self._handlers.append({
            'type': handler_type,
            'handler': handler,
            'kwargs': kwargs,
            'plugin': self.name
        })
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna status atual do plugin.
        
        Returns:
            Dicionário com informações de status
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': self.enabled,
            'dependencies': self.dependencies,
            'min_framework_version': self.min_framework_version,
            'commands_count': len(self.get_commands()),
            'handlers_count': len(self.get_handlers()),
            'config_keys': list(self.config.keys())
        }
    
    def validate_dependencies(self, available_plugins: List[str]) -> List[str]:
        """
        Valida se as dependências do plugin estão disponíveis.
        
        Args:
            available_plugins: Lista de plugins disponíveis
            
        Returns:
            Lista de dependências não atendidas
        """
        missing_deps = []
        for dep in self.dependencies:
            if dep not in available_plugins:
                missing_deps.append(dep)
        
        return missing_deps
    
    def validate_framework_version(self, framework_version: str) -> bool:
        """
        Valida se a versão do framework é compatível.
        
        Args:
            framework_version: Versão atual do framework
            
        Returns:
            True se compatível, False caso contrário
        """
        from packaging import version
        try:
            return version.parse(framework_version) >= version.parse(self.min_framework_version)
        except Exception:
            # Se não conseguir comparar versões, assumir compatível
            return True
    
    def get_help_text(self) -> str:
        """
        Retorna texto de ajuda do plugin.
        
        Returns:
            Texto formatado com ajuda do plugin
        """
        help_lines = [f"**{self.name}** v{self.version}"]
        
        if self.description:
            help_lines.append(f"_{self.description}_")
        
        if self.author:
            help_lines.append(f"Autor: {self.author}")
        
        commands = self.get_commands()
        if commands:
            help_lines.append("\n**Comandos:**")
            for cmd in commands:
                if not cmd.get('hidden', False):
                    cmd_line = f"/{cmd['name']}"
                    if cmd.get('description'):
                        cmd_line += f" - {cmd['description']}"
                    if cmd.get('admin_only'):
                        cmd_line += " (Admin)"
                    help_lines.append(cmd_line)
        
        return "\n".join(help_lines)
    
    async def send_message(self, chat_id: int, text: str, **kwargs):
        """
        Envia mensagem através do framework.
        
        Args:
            chat_id: ID do chat
            text: Texto da mensagem
            **kwargs: Argumentos adicionais
        """
        if self.framework and hasattr(self.framework, 'bot'):
            await self.framework.bot.send_message(
                chat_id=chat_id,
                text=text,
                **kwargs
            )
    
    async def send_admin_message(self, text: str, **kwargs):
        """
        Envia mensagem para administradores.
        
        Args:
            text: Texto da mensagem
            **kwargs: Argumentos adicionais
        """
        if self.framework:
            await self.framework.send_admin_message(text, **kwargs)
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Obtém dados de usuário específicos do plugin.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados do usuário para este plugin
        """
        if self.framework and hasattr(self.framework, 'user_manager'):
            user_data = self.framework.user_manager.get_user_data(user_id)
            return user_data.get('plugins', {}).get(self.name, {})
        return {}
    
    def set_user_data(self, user_id: int, data: Dict[str, Any]):
        """
        Define dados de usuário específicos do plugin.
        
        Args:
            user_id: ID do usuário
            data: Dados a serem salvos
        """
        if self.framework and hasattr(self.framework, 'user_manager'):
            user_data = self.framework.user_manager.get_user_data(user_id)
            if 'plugins' not in user_data:
                user_data['plugins'] = {}
            user_data['plugins'][self.name] = data
            self.framework.user_manager.save_user_data(user_id, user_data)
    
    def __str__(self) -> str:
        """Representação em string do plugin."""
        return f"{self.name} v{self.version}"
    
    def __repr__(self) -> str:
        """Representação para debug do plugin."""
        return f"<Plugin: {self.name} v{self.version} enabled={self.enabled}>"
