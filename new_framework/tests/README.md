# Testing Guide

This directory contains the test suite for the Telegram Bot Framework.

## Running Tests

### Install Test Dependencies

```bash
pip install -r tests/requirements.txt
```

Or install the development dependencies:

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
# From the project root
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=src/tlgfwk --cov-report=html
```

### Run Specific Tests

```bash
# Run specific test file
python -m pytest tests/test_config.py

# Run specific test class
python -m pytest tests/test_config.py::TestConfig

# Run specific test method
python -m pytest tests/test_config.py::TestConfig::test_config_creation_with_required_params
```

### Test Options

```bash
# Verbose output
python -m pytest tests/ -v

# Stop on first failure
python -m pytest tests/ -x

# Run tests in parallel
python -m pytest tests/ -n auto
```

## Test Structure

```
tests/
├── README.md              # This file
├── requirements.txt       # Test dependencies
├── conftest.py            # Test configuration (to be created)
├── test_config.py         # Configuration tests
├── test_crypto.py         # Cryptography tests
├── test_framework.py      # Framework tests (to be created)
├── test_user_manager.py   # User management tests (to be created)
├── test_persistence.py    # Persistence tests (to be created)
├── test_plugins.py        # Plugin system tests (to be created)
└── fixtures/              # Test fixtures and data
```

## Test Categories

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Fast execution

### Integration Tests
- Test component interactions
- Use real dependencies when possible
- Slower execution

### End-to-End Tests
- Test complete user workflows
- Use real Telegram Bot API (with test bot)
- Slowest execution

## Mocking

The tests use various mocking strategies:

- **Environment Variables**: `patch.dict(os.environ, ...)`
- **File Operations**: `mock_open()` for file content
- **External APIs**: Mock HTTP requests and responses
- **Telegram API**: Mock bot interactions

## Test Data

Test fixtures and sample data are stored in the `fixtures/` directory:

- Configuration files
- Sample .env files
- Mock API responses
- Test databases

## Continuous Integration

The test suite is designed to run in CI environments:

- No external dependencies required
- All necessary services are mocked
- Environment variables can be injected
- Multiple Python versions supported

## Coverage Goals

- **Overall Coverage**: > 90%
- **Core Modules**: > 95%
- **Plugin System**: > 85%
- **Utilities**: > 90%

## Writing Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>_<condition>`

### Example Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock

class TestMyClass:
    """Test cases for MyClass."""
    
    def test_method_success_case(self):
        """Test method with successful execution."""
        # Arrange
        instance = MyClass()
        
        # Act
        result = instance.method()
        
        # Assert
        assert result is not None
    
    def test_method_error_case(self):
        """Test method with error condition."""
        instance = MyClass()
        
        with pytest.raises(ValueError):
            instance.method(invalid_param=True)
    
    @patch('module.external_dependency')
    def test_method_with_mock(self, mock_dependency):
        """Test method with mocked dependency."""
        mock_dependency.return_value = "mocked_result"
        
        instance = MyClass()
        result = instance.method()
        
        assert result == "mocked_result"
        mock_dependency.assert_called_once()
```

### Async Tests

```python
import pytest

class TestAsyncMethods:
    """Test cases for async methods."""
    
    @pytest.mark.asyncio
    async def test_async_method(self):
        """Test async method execution."""
        instance = MyClass()
        result = await instance.async_method()
        assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input_value,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_method_with_parameters(input_value, expected):
    """Test method with various parameters."""
    instance = MyClass()
    result = instance.method(input_value)
    assert result == expected
```

## Test Environment

### Environment Variables

Tests should not depend on external environment variables. Use `patch.dict()` to set up test environments:

```python
@patch.dict(os.environ, {
    'BOT_TOKEN': 'test_token',
    'OWNER_USER_ID': '123456789'
})
def test_with_env_vars(self):
    # Test implementation
    pass
```

### Temporary Files

Use `tempfile` for creating test files:

```python
import tempfile
import os

def test_file_operations(self):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
        
    try:
        # Use temp_path for testing
        pass
    finally:
        os.unlink(temp_path)
```

### Database Testing

For database tests, use in-memory databases:

```python
def test_database_operations(self):
    config = {
        'database_url': 'sqlite:///:memory:'
    }
    # Test with in-memory database
```

## Performance Testing

Basic performance tests are included for critical paths:

```python
import time

def test_method_performance(self):
    """Test that method executes within time limit."""
    instance = MyClass()
    
    start_time = time.time()
    result = instance.expensive_method()
    end_time = time.time()
    
    assert result is not None
    assert (end_time - start_time) < 1.0  # Should complete in < 1 second
```

## Security Testing

Security-related tests focus on:

- Input validation
- Authorization checks
- Encryption/decryption
- Token generation
- Password handling

```python
def test_security_feature(self):
    """Test security-critical functionality."""
    # Test with malicious input
    malicious_input = "<script>alert('xss')</script>"
    
    with pytest.raises(SecurityError):
        instance.process_input(malicious_input)
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe the scenario
3. **Minimal Setup**: Use fixtures for common setup
4. **Fast Execution**: Mock external dependencies
5. **Comprehensive**: Cover edge cases and error conditions
6. **Maintainable**: Keep tests simple and focused

## Debugging Tests

### Running with Debugger

```bash
# Run with pdb
python -m pytest tests/ --pdb

# Run with pdb on failure
python -m pytest tests/ --pdb-on-failure
```

### Verbose Output

```bash
# Show all output
python -m pytest tests/ -s

# Show detailed assertion information
python -m pytest tests/ -vv
```

### Specific Test Debugging

```python
def test_debug_example(self):
    """Example test with debugging."""
    import pdb; pdb.set_trace()  # Breakpoint
    
    # Test code here
    pass
```

This test suite ensures the reliability and correctness of the Telegram Bot Framework components.
