"""
Persistence Manager for the Telegram Bot Framework.

Provides abstraction for different data storage backends.
"""

import json
import pickle
import sqlite3
import aiofiles
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Protocol, Union, TypeVar
from datetime import datetime

# Create our own BasePersistence class since importing from telegram.ext.persistence may not be available
class BasePersistence(Protocol):
    """Protocol for persistence classes that can be used by the framework."""
    def get_data(self) -> Dict[str, Any]:
        """Get stored data."""
        ...
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """Update stored data."""
        ...
        
from ..utils.logger import LoggerMixin


class PersistenceError(Exception):
    """Exception raised for persistence errors."""
    pass


T = TypeVar('T')


class PersistenceManager(LoggerMixin):
    """Gerenciador de persistência de dados."""
    
    def __init__(self, config):
        """
        Inicializa o gerenciador de persistência.
        
        Args:
            config: Configuração do framework
        """
        self.config = config
        self.backend = config.persistence_backend
        self.database_url = config.database_url
        self._persistence = None
        
        # Criar diretórios necessários
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Cria diretórios necessários para persistência."""
        Path("data").mkdir(exist_ok=True)
        Path("backups").mkdir(exist_ok=True)
    
    async def get_persistence(self):
        """
        Retorna instância de persistência configurada.
        
        Returns:
            Instância de persistência do python-telegram-bot
        """
        if self._persistence is None:
            if self.backend == "pickle":
                from telegram.ext import PicklePersistence
                self._persistence = PicklePersistence(
                    filepath="data/bot_data.pickle",
                    store_data=True,
                    update_interval=self.config.persistence_interval
                )
            elif self.backend == "sqlite":
                # Implementação customizada para SQLite
                self._persistence = await self._create_sqlite_persistence()
            elif self.backend == "json":
                # Implementação customizada para JSON
                self._persistence = await self._create_json_persistence()
        
        return self._persistence
    
    async def _create_sqlite_persistence(self):
        """Cria persistência SQLite customizada."""
        # Por ora, usar pickle como fallback
        # TODO: Implementar persistência SQLite completa
        from telegram.ext import PicklePersistence
        return PicklePersistence(
            filepath="data/bot_data.pickle",
            store_data=True,
            update_interval=self.config.persistence_interval
        )
    
    async def _create_json_persistence(self):
        """Cria persistência JSON customizada."""
        # Por ora, usar pickle como fallback
        # TODO: Implementar persistência JSON completa
        from telegram.ext import PicklePersistence
        return PicklePersistence(
            filepath="data/bot_data.pickle",
            store_data=True,
            update_interval=self.config.persistence_interval
        )
    
    async def save_user_data(self, user_id: int, data: Dict[str, Any]):
        """
        Salva dados de usuário.
        
        Args:
            user_id: ID do usuário
            data: Dados a serem salvos
        """
        file_path = Path(f"data/users/{user_id}.json")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        except Exception as e:
            self.log_error(f"Erro ao salvar dados do usuário {user_id}: {e}")
    
    async def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados do usuário ou None se não encontrado
        """
        file_path = Path(f"data/users/{user_id}.json")
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            self.log_error(f"Erro ao carregar dados do usuário {user_id}: {e}")
            return None
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os usuários salvos.
        
        Returns:
            Lista de usuários
        """
        users = []
        users_dir = Path("data/users")
        
        if not users_dir.exists():
            return users
        
        for user_file in users_dir.glob("*.json"):
            try:
                async with aiofiles.open(user_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    user_data = json.loads(content)
                    users.append(user_data)
            except Exception as e:
                self.log_warning(f"Erro ao carregar arquivo {user_file}: {e}")
        
        return users
    
    async def get_user_count(self) -> int:
        """
        Retorna número de usuários salvos.
        
        Returns:
            Contagem de usuários
        """
        users_dir = Path("data/users")
        
        if not users_dir.exists():
            return 0
        
        return len(list(users_dir.glob("*.json")))
    
    async def save_bot_data(self, data: Dict[str, Any]):
        """
        Salva dados gerais do bot.
        
        Args:
            data: Dados a serem salvos
        """
        file_path = Path("data/bot_data.json")
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        except Exception as e:
            self.log_error(f"Erro ao salvar dados do bot: {e}")
    
    async def get_bot_data(self) -> Dict[str, Any]:
        """
        Obtém dados gerais do bot.
        
        Returns:
            Dados do bot
        """
        file_path = Path("data/bot_data.json")
        
        if not file_path.exists():
            return {}
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            self.log_error(f"Erro ao carregar dados do bot: {e}")
            return {}
    
    async def save_plugin_data(self, plugin_name: str, data: Dict[str, Any]):
        """
        Salva dados específicos de plugin.
        
        Args:
            plugin_name: Nome do plugin
            data: Dados a serem salvos
        """
        file_path = Path(f"data/plugins/{plugin_name}.json")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        except Exception as e:
            self.log_error(f"Erro ao salvar dados do plugin {plugin_name}: {e}")
    
    async def get_plugin_data(self, plugin_name: str) -> Dict[str, Any]:
        """
        Obtém dados específicos de plugin.
        
        Args:
            plugin_name: Nome do plugin
            
        Returns:
            Dados do plugin
        """
        file_path = Path(f"data/plugins/{plugin_name}.json")
        
        if not file_path.exists():
            return {}
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            self.log_error(f"Erro ao carregar dados do plugin {plugin_name}: {e}")
            return {}
    
    async def backup_data(self, backup_name: Optional[str] = None):
        """
        Cria backup dos dados.
        
        Args:
            backup_name: Nome do backup (padrão: timestamp)
        """
        if backup_name is None:
            backup_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_dir = Path(f"backups/{backup_name}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup dos dados
        data_dir = Path("data")
        if data_dir.exists():
            import shutil
            shutil.copytree(data_dir, backup_dir / "data", dirs_exist_ok=True)
        
        # Backup da configuração
        env_file = Path(".env")
        if env_file.exists():
            shutil.copy2(env_file, backup_dir / ".env")
        
        self.log_info(f"Backup criado: {backup_dir}")
    
    async def restore_backup(self, backup_name: str):
        """
        Restaura backup dos dados.
        
        Args:
            backup_name: Nome do backup a restaurar
        """
        backup_dir = Path(f"backups/{backup_name}")
        
        if not backup_dir.exists():
            raise FileNotFoundError(f"Backup {backup_name} não encontrado")
        
        # Restaurar dados
        backup_data_dir = backup_dir / "data"
        if backup_data_dir.exists():
            import shutil
            data_dir = Path("data")
            if data_dir.exists():
                shutil.rmtree(data_dir)
            shutil.copytree(backup_data_dir, data_dir)
        
        # Restaurar configuração
        backup_env = backup_dir / ".env"
        if backup_env.exists():
            import shutil
            shutil.copy2(backup_env, ".env")
        
        self.log_info(f"Backup {backup_name} restaurado")
    
    async def list_backups(self) -> List[str]:
        """
        Lista backups disponíveis.
        
        Returns:
            Lista de nomes de backup
        """
        backups_dir = Path("backups")
        
        if not backups_dir.exists():
            return []
        
        return [backup.name for backup in backups_dir.iterdir() if backup.is_dir()]
    
    async def cleanup_old_backups(self, keep_count: int = 10):
        """
        Remove backups antigos, mantendo apenas os mais recentes.
        
        Args:
            keep_count: Número de backups a manter
        """
        backups = await self.list_backups()
        
        if len(backups) <= keep_count:
            return
        
        # Ordenar por data de modificação
        backups_dir = Path("backups")
        backup_paths = [(backup, backups_dir / backup) for backup in backups]
        backup_paths.sort(key=lambda x: x[1].stat().st_mtime, reverse=True)
        
        # Remover backups antigos
        for backup_name, backup_path in backup_paths[keep_count:]:
            import shutil
            shutil.rmtree(backup_path)
            self.log_info(f"Backup antigo removido: {backup_name}")
    
    async def flush(self):
        """Força salvamento de todos os dados pendentes."""
        if self._persistence and hasattr(self._persistence, 'flush'):
            await self._persistence.flush()
        
        self.log_debug("Dados de persistência sincronizados")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de persistência.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            "backend": self.backend,
            "users_count": await self.get_user_count(),
            "backups_count": len(await self.list_backups()),
            "data_size": 0,
        }
        
        # Calcular tamanho dos dados
        data_dir = Path("data")
        if data_dir.exists():
            stats["data_size"] = sum(
                f.stat().st_size for f in data_dir.rglob("*") if f.is_file()
            )
        
        return stats


class FilePersistenceManager:
    """File-based persistence manager."""
    
    def __init__(self, file_path: str):
        """
        Initialize file-based persistence.
        
        Args:
            file_path: Path to the storage file
        """
        self.file_path = file_path
        self.data = {}
        self._lock = asyncio.Lock()
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Load data or create new file
        self._load_data_sync()
        if not os.path.exists(file_path):
            self._save_data_sync()
    
    def _load_data_sync(self) -> None:
        """Load data from file synchronously (used during initialization)."""
        if not os.path.exists(self.file_path):
            self.data = {}
            return
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            # Handle corrupted files by starting with empty data
            self.data = {}
            # Don't raise during init, just log the error
            print(f"Error loading persistence file: {str(e)}")
    
    def _save_data_sync(self) -> None:
        """Save data to file synchronously."""
        try:
            # Save to a temporary file first to ensure atomicity
            temp_file = f"{self.file_path}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
                
            # Replace the actual file (atomic on most systems)
            if os.name == "posix":
                os.replace(temp_file, self.file_path)
            else:
                # Windows may need a different approach
                if os.path.exists(self.file_path):
                    os.unlink(self.file_path)
                os.rename(temp_file, self.file_path)
        except Exception as e:
            raise PersistenceError(f"Failed to save data to {self.file_path}: {str(e)}")
    
    async def _load_data(self) -> None:
        """Load data from file asynchronously."""
        if not os.path.exists(self.file_path):
            self.data = {}
            return
            
        try:
            async with aiofiles.open(self.file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                self.data = json.loads(content)
        except Exception as e:
            # Handle corrupted files by starting with empty data
            self.data = {}
            raise PersistenceError(f"Failed to load data from {self.file_path}: {str(e)}")
    
    async def _save_data(self) -> None:
        """Save data to file asynchronously."""
        try:
            # Create directory if needed
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
            # Save to a temporary file first to ensure atomicity
            temp_file = f"{self.file_path}.tmp"
            async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.data, indent=2, ensure_ascii=False))
                
            # Replace the actual file (atomic on most systems)
            if os.name == "posix":
                os.replace(temp_file, self.file_path)
            else:
                # Windows may need a different approach
                if os.path.exists(self.file_path):
                    os.unlink(self.file_path)
                os.rename(temp_file, self.file_path)
        except Exception as e:
            raise PersistenceError(f"Failed to save data to {self.file_path}: {str(e)}")
    
    async def set(self, key: str, value: Any) -> None:
        """
        Set a value in the persistence store.
        
        Args:
            key: The key to set
            value: The value to store
        """
        async with self._lock:
            self.data[key] = value
            await self._save_data()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the persistence store.
        
        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The value or default if key doesn't exist
        """
        return self.data.get(key, default)
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the persistence store.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return key in self.data
    
    async def delete(self, key: str) -> None:
        """
        Delete a key from the persistence store.
        
        Args:
            key: The key to delete
        """
        async with self._lock:
            if key in self.data:
                del self.data[key]
                await self._save_data()
    
    async def clear(self) -> None:
        """Clear all data from the persistence store."""
        async with self._lock:
            self.data.clear()
            await self._save_data()
    
    async def close(self) -> None:
        """Close the persistence store (ensure all data is saved)."""
        async with self._lock:
            await self._save_data()
    
    # Legacy methods for compatibility
    def get_data(self) -> Dict[str, Any]:
        """Get all stored data."""
        return self.data
    
    def update_data(self, new_data: Dict[str, Any]) -> None:
        """Update the stored data with new data."""
        self.data.update(new_data)
        self._save_data_sync()
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get data for a specific user."""
        return self.data.get('user_data', {}).get(str(user_id), {})
    
    async def update_user_data(self, user_id: int, data: Dict[str, Any]) -> None:
        """Atualiza dados de um usuário específico."""
        if 'user_data' not in self.data:
            self.data['user_data'] = {}
        
        if str(user_id) not in self.data['user_data']:
            self.data['user_data'][str(user_id)] = {}
            
        self.data['user_data'][str(user_id)].update(data)
        self._save_data()


class MemoryPersistenceManager:
    """In-memory persistence manager."""
    
    def __init__(self):
        """Initialize the in-memory persistence."""
        self.data = {}
    
    async def set(self, key: str, value: Any) -> None:
        """
        Set a value in the persistence store.
        
        Args:
            key: The key to set
            value: The value to store
        """
        self.data[key] = value
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the persistence store.
        
        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The value or default if key doesn't exist
        """
        return self.data.get(key, default)
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the persistence store.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return key in self.data
    
    async def delete(self, key: str) -> None:
        """
        Delete a key from the persistence store.
        
        Args:
            key: The key to delete
        """
        if key in self.data:
            del self.data[key]
    
    async def clear(self) -> None:
        """Clear all data from the persistence store."""
        self.data.clear()
    
    async def close(self) -> None:
        """Close the persistence store (no-op for memory store)."""
        pass
    
    # Legacy methods for compatibility
    def get_data(self) -> Dict[str, Any]:
        """Get all stored data."""
        return self.data
    
    def update_data(self, new_data: Dict[str, Any]) -> None:
        """Update the stored data with new data."""
        self.data.update(new_data)
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get data for a specific user."""
        return self.data.get('user_data', {}).get(str(user_id), {})
    
    async def update_user_data(self, user_id: int, data: Dict[str, Any]) -> None:
        """Atualiza dados de um usuário específico."""
        if 'user_data' not in self.data:
            self.data['user_data'] = {}
        
        if str(user_id) not in self.data['user_data']:
            self.data['user_data'][str(user_id)] = {}
            
        self.data['user_data'][str(user_id)].update(data)


class PersistenceError(Exception):
    """Base exception for persistence-related errors."""
    pass
