"""
Tests for the PersistenceManager class.
"""

import pytest
import tempfile
import os
import json
import asyncio
from unittest.mock import Mock, AsyncMock, patch, mock_open

from tlgfwk.core.persistence_manager import PersistenceManager, FilePersistenceManager, MemoryPersistenceManager


class TestPersistenceManager:
    """Test cases for base PersistenceManager."""
    
    def test_abstract_methods(self):
        """Test that PersistenceManager is abstract."""
        with pytest.raises(TypeError):
            PersistenceManager()


class TestMemoryPersistenceManager:
    """Test cases for MemoryPersistenceManager."""
    
    @pytest.fixture
    def memory_persistence(self):
        """Create a MemoryPersistenceManager instance."""
        return MemoryPersistenceManager()
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, memory_persistence):
        """Test setting and getting data."""
        key = "test_key"
        value = {"name": "test", "value": 42}
        
        await memory_persistence.set(key, value)
        result = await memory_persistence.get(key)
        
        assert result == value
    
    @pytest.mark.asyncio
    async def test_get_nonexistent(self, memory_persistence):
        """Test getting non-existent key."""
        result = await memory_persistence.get("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_with_default(self, memory_persistence):
        """Test getting with default value."""
        default_value = "default"
        result = await memory_persistence.get("nonexistent", default_value)
        assert result == default_value
    
    @pytest.mark.asyncio
    async def test_exists_true(self, memory_persistence):
        """Test exists for existing key."""
        key = "test_key"
        await memory_persistence.set(key, "value")
        
        result = await memory_persistence.exists(key)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_exists_false(self, memory_persistence):
        """Test exists for non-existent key."""
        result = await memory_persistence.exists("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_existing(self, memory_persistence):
        """Test deleting existing key."""
        key = "test_key"
        await memory_persistence.set(key, "value")
        
        await memory_persistence.delete(key)
        
        result = await memory_persistence.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, memory_persistence):
        """Test deleting non-existent key (should not raise error)."""
        await memory_persistence.delete("nonexistent")
        # Should complete without error
    
    @pytest.mark.asyncio
    async def test_clear(self, memory_persistence):
        """Test clearing all data."""
        await memory_persistence.set("key1", "value1")
        await memory_persistence.set("key2", "value2")
        
        await memory_persistence.clear()
        
        assert await memory_persistence.get("key1") is None
        assert await memory_persistence.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_close(self, memory_persistence):
        """Test close method (should be safe to call)."""
        await memory_persistence.close()
        # Should complete without error


class TestFilePersistenceManager:
    """Test cases for FilePersistenceManager."""
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def file_persistence(self, temp_file):
        """Create a FilePersistenceManager instance."""
        return FilePersistenceManager(temp_file)
    
    @pytest.mark.asyncio
    async def test_initialization_new_file(self, temp_file):
        """Test initialization with new file."""
        os.unlink(temp_file)  # Remove the temp file
        
        persistence = FilePersistenceManager(temp_file)
        
        # File should be created
        assert os.path.exists(temp_file)
        
        # Should contain empty dict
        with open(temp_file, 'r') as f:
            data = json.load(f)
        assert data == {}
    
    @pytest.mark.asyncio
    async def test_initialization_existing_file(self, temp_file):
        """Test initialization with existing file."""
        # Populate the file with some data
        test_data = {"existing": "data"}
        with open(temp_file, 'w') as f:
            json.dump(test_data, f)
        
        persistence = FilePersistenceManager(temp_file)
        
        # Should load existing data
        result = await persistence.get("existing")
        assert result == "data"
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, file_persistence):
        """Test setting and getting data."""
        key = "test_key"
        value = {"name": "test", "value": 42}
        
        await file_persistence.set(key, value)
        result = await file_persistence.get(key)
        
        assert result == value
    
    @pytest.mark.asyncio
    async def test_persistence_across_instances(self, temp_file):
        """Test that data persists across instances."""
        # First instance
        persistence1 = FilePersistenceManager(temp_file)
        await persistence1.set("persistent_key", "persistent_value")
        await persistence1.close()
        
        # Second instance
        persistence2 = FilePersistenceManager(temp_file)
        result = await persistence2.get("persistent_key")
        
        assert result == "persistent_value"
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self, file_persistence):
        """Test concurrent access to the same file."""
        # Simulate concurrent writes
        tasks = []
        for i in range(10):
            task = file_persistence.set(f"key_{i}", f"value_{i}")
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Verify all data was written
        for i in range(10):
            result = await file_persistence.get(f"key_{i}")
            assert result == f"value_{i}"
    
    @pytest.mark.asyncio
    async def test_file_corruption_handling(self, temp_file):
        """Test handling of corrupted JSON file."""
        # Write invalid JSON
        with open(temp_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle gracefully and start with empty data
        persistence = FilePersistenceManager(temp_file)
        
        result = await persistence.get("any_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_directory_creation(self):
        """Test that directories are created if they don't exist."""
        temp_dir = tempfile.mkdtemp()
        nested_path = os.path.join(temp_dir, "nested", "deep", "file.json")
        
        try:
            persistence = FilePersistenceManager(nested_path)
            await persistence.set("test", "value")
            
            assert os.path.exists(nested_path)
            
            result = await persistence.get("test")
            assert result == "value"
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_large_data_handling(self, file_persistence):
        """Test handling of large data sets."""
        # Create a large data structure
        large_data = {f"key_{i}": f"value_{i}" * 100 for i in range(1000)}
        
        await file_persistence.set("large_data", large_data)
        result = await file_persistence.get("large_data")
        
        assert result == large_data
    
    @pytest.mark.asyncio
    async def test_special_characters_in_data(self, file_persistence):
        """Test handling of special characters in data."""
        special_data = {
            "unicode": "Hello 世界 🌍",
            "json_chars": '{"nested": "value"}',
            "newlines": "line1\nline2\r\nline3",
            "quotes": 'He said "Hello" and she said \'Hi\''
        }
        
        await file_persistence.set("special", special_data)
        result = await file_persistence.get("special")
        
        assert result == special_data
    
    @pytest.mark.asyncio
    async def test_atomic_writes(self, file_persistence):
        """Test that writes are atomic (no partial writes)."""
        # This is a bit tricky to test directly, but we can verify
        # that the file is always in a valid state
        
        large_data = {"data": "x" * 10000}
        
        # Start multiple concurrent writes
        tasks = []
        for i in range(5):
            task = file_persistence.set(f"atomic_test_{i}", large_data)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Verify file is still valid JSON
        with open(file_persistence.file_path, 'r') as f:
            data = json.load(f)
        
        # Should have all the data
        for i in range(5):
            assert f"atomic_test_{i}" in data
    
    @pytest.mark.asyncio
    async def test_backup_and_restore(self, file_persistence, temp_file):
        """Test backup functionality if implemented."""
        # Set some data
        test_data = {"important": "data", "count": 42}
        await file_persistence.set("backup_test", test_data)
        
        # Create backup manually (simulating backup feature)
        backup_path = temp_file + ".backup"
        with open(file_persistence.file_path, 'r') as src:
            with open(backup_path, 'w') as dst:
                dst.write(src.read())
        
        try:
            # Corrupt original file
            with open(file_persistence.file_path, 'w') as f:
                f.write("corrupted")
            
            # Create new instance (should handle corruption)
            new_persistence = FilePersistenceManager(file_persistence.file_path)
            
            # Manually restore from backup
            with open(backup_path, 'r') as src:
                with open(file_persistence.file_path, 'w') as dst:
                    dst.write(src.read())
            
            restored_persistence = FilePersistenceManager(file_persistence.file_path)
            result = await restored_persistence.get("backup_test")
            
            assert result == test_data
        finally:
            if os.path.exists(backup_path):
                os.unlink(backup_path)
