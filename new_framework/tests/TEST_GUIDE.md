# Test Suite

This directory contains comprehensive tests for the Telegram Bot Framework.

## Test Structure

- `test_config.py` - Configuration management tests
- `test_crypto.py` - Cryptography utility tests  
- `test_framework.py` - Main framework tests
- `test_user_manager.py` - User management tests
- `test_persistence_manager.py` - Data persistence tests
- `test_plugin_manager.py` - Plugin system tests
- `test_payment_manager.py` - Payment processing tests
- `test_scheduler.py` - Job scheduling tests
- `test_decorators.py` - Decorator functionality tests
- `test_utils.py` - Utility module tests
- `test_plugins.py` - Built-in plugin tests

## Running Tests

### Prerequisites

Install test dependencies:

```bash
cd tests
pip install -r requirements.txt
```

### Running All Tests

```bash
# From the project root
pytest

# Or from tests directory
cd tests
pytest .
```

### Running Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only  
pytest -m integration

# Plugin tests only
pytest -m plugins

# Crypto tests only
pytest -m crypto

# Exclude slow tests
pytest -m "not slow"
```

### Running Specific Test Files

```bash
pytest tests/test_framework.py
pytest tests/test_plugins.py
pytest tests/test_crypto.py
```

### Running Tests with Coverage

```bash
# Generate coverage report
pytest --cov=tlgfwk --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
start htmlcov/index.html  # On Windows
```

### Running Tests in Parallel

```bash
# Use multiple processes to speed up tests
pytest -n auto
```

## Test Configuration

Test configuration is defined in `pyproject.toml`:

- **Coverage**: Minimum 80% coverage target
- **Markers**: Custom test markers for categorization
- **Async Support**: Full asyncio testing support
- **Parallel Execution**: Support for concurrent test execution

## Writing Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>`

### Example Test Structure

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestMyClass:
    @pytest.fixture
    def mock_dependency(self):
        return Mock()
    
    @pytest.mark.asyncio
    async def test_async_method(self, mock_dependency):
        # Test async functionality
        result = await my_async_method()
        assert result == expected_value
    
    def test_sync_method(self, mock_dependency):
        # Test sync functionality
        result = my_sync_method()
        assert result == expected_value
```

### Test Markers

Use appropriate markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration  
def test_integration_functionality():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.crypto
def test_encryption():
    pass
```

## Mocking Guidelines

- Mock external dependencies (Telegram API, databases, file system)
- Use `AsyncMock` for async methods
- Mock at the appropriate level (prefer mocking interfaces over implementations)
- Use fixtures for commonly mocked objects

## Test Data

- Keep test data minimal and focused
- Use factories or fixtures for complex test objects
- Avoid hardcoded values that might change
- Clean up test data in teardown methods

## Continuous Integration

Tests are designed to run in CI environments:

- No external dependencies required
- All network calls are mocked
- Temporary files are properly cleaned up
- Tests are deterministic and repeatable

## Performance Testing

For performance-critical components:

```python
@pytest.mark.slow
def test_performance():
    import time
    start = time.time()
    
    # Run operation
    result = expensive_operation()
    
    duration = time.time() - start
    assert duration < 1.0  # Should complete in under 1 second
```

## Debugging Tests

```bash
# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Run specific test with output
pytest -s tests/test_framework.py::TestTelegramBotFramework::test_start_command
```
