"""
Gerenciador de usuários do framework.

Responsável por registrar, rastrear e gerenciar usuários que interagem com o bot.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from telegram import User

from ..utils.logger import LoggerMixin


class UserManager(LoggerMixin):
    """Gerenciador de usuários do bot."""
    
    def __init__(self, config, persistence_manager=None):
        """
        Inicializa o gerenciador de usuários.
        
        Args:
            config: Configuração do framework
            persistence_manager: Gerenciador de persistência
        """
        self.config = config
        self.persistence_manager = persistence_manager
        self.users_cache = {}
        self.command_history = {}
    
    async def register_user(self, user: User) -> Dict[str, Any]:
        """
        Registra um novo usuário ou atualiza dados existentes.
        
        Args:
            user: Objeto User do Telegram
            
        Returns:
            Dados do usuário registrado
        """
        user_id = user.id
        current_time = datetime.now()
        
        # Verificar se usuário já existe
        existing_user = await self.get_user(user_id)
        
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "language_code": user.language_code,
            "is_bot": user.is_bot,
            "is_premium": getattr(user, 'is_premium', False),
            "updated_at": current_time.isoformat(),
            "is_admin": user_id in self.config.admin_ids,
            "is_owner": user_id == self.config.bot_owner_id,
        }
        
        if existing_user:
            # Atualizar usuário existente
            user_data.update({
                "registered_at": existing_user.get("registered_at", current_time.isoformat()),
                "command_count": existing_user.get("command_count", 0),
                "last_activity": current_time.isoformat(),
                "settings": existing_user.get("settings", {}),
                "plugins": existing_user.get("plugins", {}),
            })
        else:
            # Novo usuário
            user_data.update({
                "registered_at": current_time.isoformat(),
                "command_count": 0,
                "last_activity": current_time.isoformat(),
                "settings": {},
                "plugins": {},
            })
            
            self.log_info(f"Novo usuário registrado: {user.full_name} (ID: {user.id})")
        
        # Salvar no cache e persistência
        self.users_cache[user_id] = user_data
        await self.save_user(user_id, user_data)
        
        return user_data
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados do usuário ou None se não encontrado
        """
        # Verificar cache primeiro
        if user_id in self.users_cache:
            return self.users_cache[user_id]
        
        # Buscar na persistência
        if self.persistence_manager:
            user_data = await self.persistence_manager.get_user_data(user_id)
            if user_data:
                self.users_cache[user_id] = user_data
                return user_data
        
        return None
    
    async def save_user(self, user_id: int, user_data: Dict[str, Any]):
        """
        Salva dados de usuário.
        
        Args:
            user_id: ID do usuário
            user_data: Dados a serem salvos
        """
        self.users_cache[user_id] = user_data
        
        if self.persistence_manager:
            await self.persistence_manager.save_user_data(user_id, user_data)
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os usuários registrados.
        
        Returns:
            Lista de usuários
        """
        if self.persistence_manager:
            return await self.persistence_manager.get_all_users()
        
        return list(self.users_cache.values())
    
    async def get_user_count(self) -> int:
        """
        Retorna número total de usuários.
        
        Returns:
            Contagem de usuários
        """
        if self.persistence_manager:
            return await self.persistence_manager.get_user_count()
        
        return len(self.users_cache)
    
    async def update_user_setting(self, user_id: int, key: str, value: Any):
        """
        Atualiza configuração específica do usuário.
        
        Args:
            user_id: ID do usuário
            key: Chave da configuração
            value: Valor da configuração
        """
        user_data = await self.get_user(user_id)
        if user_data:
            if "settings" not in user_data:
                user_data["settings"] = {}
            
            user_data["settings"][key] = value
            user_data["updated_at"] = datetime.now().isoformat()
            
            await self.save_user(user_id, user_data)
    
    async def get_user_setting(self, user_id: int, key: str, default=None):
        """
        Obtém configuração específica do usuário.
        
        Args:
            user_id: ID do usuário
            key: Chave da configuração
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração
        """
        user_data = await self.get_user(user_id)
        if user_data and "settings" in user_data:
            return user_data["settings"].get(key, default)
        
        return default
    
    async def log_command_usage(self, user_id: int, command: str):
        """
        Registra uso de comando pelo usuário.
        
        Args:
            user_id: ID do usuário
            command: Nome do comando
        """
        current_time = datetime.now()
        
        # Atualizar dados do usuário
        user_data = await self.get_user(user_id)
        if user_data:
            user_data["command_count"] = user_data.get("command_count", 0) + 1
            user_data["last_activity"] = current_time.isoformat()
            user_data["last_command"] = command
            
            await self.save_user(user_id, user_data)
        
        # Registrar no histórico de comandos
        if user_id not in self.command_history:
            self.command_history[user_id] = []
        
        self.command_history[user_id].append({
            "command": command,
            "timestamp": current_time.isoformat()
        })
        
        # Manter apenas os últimos 100 comandos por usuário
        if len(self.command_history[user_id]) > 100:
            self.command_history[user_id] = self.command_history[user_id][-100:]
    
    async def get_user_command_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém histórico de comandos do usuário.
        
        Args:
            user_id: ID do usuário
            limit: Limite de comandos a retornar
            
        Returns:
            Lista de comandos executados
        """
        if user_id in self.command_history:
            return self.command_history[user_id][-limit:]
        
        return []
    
    async def add_admin(self, user_id: int) -> bool:
        """
        Adiciona usuário como administrador.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se adicionado com sucesso
        """
        if user_id not in self.config.admin_ids:
            self.config.admin_ids.append(user_id)
            
            # Atualizar dados do usuário
            user_data = await self.get_user(user_id)
            if user_data:
                user_data["is_admin"] = True
                user_data["updated_at"] = datetime.now().isoformat()
                await self.save_user(user_id, user_data)
            
            # Salvar configuração
            self.config.save_to_env()
            
            self.log_info(f"Usuário {user_id} adicionado como admin")
            return True
        
        return False
    
    async def remove_admin(self, user_id: int) -> bool:
        """
        Remove usuário dos administradores.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se removido com sucesso
        """
        # Não permitir remoção do owner
        if user_id == self.config.bot_owner_id:
            return False
        
        if user_id in self.config.admin_ids:
            self.config.admin_ids.remove(user_id)
            
            # Atualizar dados do usuário
            user_data = await self.get_user(user_id)
            if user_data:
                user_data["is_admin"] = False
                user_data["updated_at"] = datetime.now().isoformat()
                await self.save_user(user_id, user_data)
            
            # Salvar configuração
            self.config.save_to_env()
            
            self.log_info(f"Usuário {user_id} removido dos admins")
            return True
        
        return False
    
    async def get_admins(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de administradores.
        
        Returns:
            Lista de administradores
        """
        admins = []
        
        for admin_id in self.config.admin_ids:
            user_data = await self.get_user(admin_id)
            if user_data:
                admins.append(user_data)
        
        return admins
    
    async def is_admin(self, user_id: int) -> bool:
        """
        Verifica se usuário é administrador.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se é administrador
        """
        return user_id in self.config.admin_ids
    
    async def is_owner(self, user_id: int) -> bool:
        """
        Verifica se usuário é o proprietário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se é proprietário
        """
        return user_id == self.config.bot_owner_id
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de usuários.
        
        Returns:
            Dicionário com estatísticas
        """
        all_users = await self.get_all_users()
        
        stats = {
            "total_users": len(all_users),
            "admin_count": len(self.config.admin_ids),
            "active_users_24h": 0,
            "active_users_7d": 0,
            "total_commands": 0,
        }
        
        current_time = datetime.now()
        
        for user in all_users:
            # Contar comandos totais
            stats["total_commands"] += user.get("command_count", 0)
            
            # Verificar atividade recente
            last_activity = user.get("last_activity")
            if last_activity:
                try:
                    activity_time = datetime.fromisoformat(last_activity)
                    time_diff = current_time - activity_time
                    
                    if time_diff.days < 1:
                        stats["active_users_24h"] += 1
                    if time_diff.days < 7:
                        stats["active_users_7d"] += 1
                        
                except (ValueError, TypeError):
                    pass
        
        return stats
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Obtém dados do usuário (método síncrono para compatibilidade).
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados do usuário
        """
        return self.users_cache.get(user_id, {})
    
    def save_user_data(self, user_id: int, data: Dict[str, Any]):
        """
        Salva dados do usuário (método síncrono para compatibilidade).
        
        Args:
            user_id: ID do usuário
            data: Dados a serem salvos
        """
        self.users_cache[user_id] = data
