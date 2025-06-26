"""
Tests for the PaymentManager class.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal

from tlgfwk.core.payment_manager import PaymentManager, PaymentProvider, PaymentResult, PaymentStatus


class MockPaymentProvider(PaymentProvider):
    """Mock payment provider for testing."""
    
    def __init__(self, should_succeed=True):
        self.should_succeed = should_succeed
        self.processed_payments = []
    
    async def process_payment(self, amount: Decimal, currency: str, user_id: int, description: str = "") -> PaymentResult:
        """Mock payment processing."""
        payment_data = {
            'amount': amount,
            'currency': currency,
            'user_id': user_id,
            'description': description
        }
        self.processed_payments.append(payment_data)
        
        if self.should_succeed:
            return PaymentResult(
                status=PaymentStatus.SUCCESS,
                transaction_id=f"mock_tx_{len(self.processed_payments)}",
                amount=amount,
                currency=currency,
                message="Payment processed successfully"
            )
        else:
            return PaymentResult(
                status=PaymentStatus.FAILED,
                transaction_id=None,
                amount=amount,
                currency=currency,
                message="Payment failed"
            )
    
    async def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Mock payment verification."""
        if transaction_id.startswith("mock_tx_") and self.should_succeed:
            return PaymentResult(
                status=PaymentStatus.SUCCESS,
                transaction_id=transaction_id,
                amount=Decimal("10.00"),
                currency="USD",
                message="Payment verified"
            )
        else:
            return PaymentResult(
                status=PaymentStatus.FAILED,
                transaction_id=transaction_id,
                amount=Decimal("0.00"),
                currency="USD",
                message="Payment verification failed"
            )
    
    async def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """Mock payment refund."""
        if self.should_succeed:
            return PaymentResult(
                status=PaymentStatus.SUCCESS,
                transaction_id=f"refund_{transaction_id}",
                amount=amount or Decimal("10.00"),
                currency="USD",
                message="Refund processed"
            )
        else:
            return PaymentResult(
                status=PaymentStatus.FAILED,
                transaction_id=transaction_id,
                amount=Decimal("0.00"),
                currency="USD",
                message="Refund failed"
            )


class TestPaymentResult:
    """Test cases for PaymentResult."""
    
    def test_payment_result_creation(self):
        """Test creating a PaymentResult."""
        result = PaymentResult(
            status=PaymentStatus.SUCCESS,
            transaction_id="test_tx",
            amount=Decimal("25.50"),
            currency="USD",
            message="Success"
        )
        
        assert result.status == PaymentStatus.SUCCESS
        assert result.transaction_id == "test_tx"
        assert result.amount == Decimal("25.50")
        assert result.currency == "USD"
        assert result.message == "Success"
    
    def test_payment_result_success_property(self):
        """Test the success property."""
        success_result = PaymentResult(
            status=PaymentStatus.SUCCESS,
            transaction_id="test_tx",
            amount=Decimal("10.00"),
            currency="USD"
        )
        
        failed_result = PaymentResult(
            status=PaymentStatus.FAILED,
            transaction_id=None,
            amount=Decimal("10.00"),
            currency="USD"
        )
        
        assert success_result.success is True
        assert failed_result.success is False


class TestPaymentManager:
    """Test cases for PaymentManager."""
    
    @pytest.fixture
    def mock_persistence(self):
        """Create a mock persistence manager."""
        persistence = Mock()
        persistence.get = AsyncMock()
        persistence.set = AsyncMock()
        persistence.exists = AsyncMock()
        return persistence
    
    @pytest.fixture
    def payment_manager(self, mock_persistence):
        """Create a PaymentManager instance."""
        config = {
            'payments.default_currency': 'USD',
            'payments.enable_logging': True
        }
        return PaymentManager(config, mock_persistence)
    
    def test_initialization(self, payment_manager):
        """Test PaymentManager initialization."""
        assert payment_manager.providers == {}
        assert payment_manager.default_currency == "USD"
        assert payment_manager.enable_logging is True
    
    def test_register_provider(self, payment_manager):
        """Test registering a payment provider."""
        provider = MockPaymentProvider()
        
        payment_manager.register_provider("mock", provider)
        
        assert "mock" in payment_manager.providers
        assert payment_manager.providers["mock"] == provider
    
    def test_register_provider_duplicate(self, payment_manager):
        """Test registering duplicate provider name."""
        provider1 = MockPaymentProvider()
        provider2 = MockPaymentProvider()
        
        payment_manager.register_provider("mock", provider1)
        
        with pytest.raises(ValueError, match="Provider 'mock' already registered"):
            payment_manager.register_provider("mock", provider2)
    
    def test_unregister_provider(self, payment_manager):
        """Test unregistering a payment provider."""
        provider = MockPaymentProvider()
        payment_manager.register_provider("mock", provider)
        
        result = payment_manager.unregister_provider("mock")
        
        assert result is True
        assert "mock" not in payment_manager.providers
    
    def test_unregister_provider_not_found(self, payment_manager):
        """Test unregistering non-existent provider."""
        result = payment_manager.unregister_provider("nonexistent")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_process_payment_success(self, payment_manager, mock_persistence):
        """Test successful payment processing."""
        provider = MockPaymentProvider(should_succeed=True)
        payment_manager.register_provider("mock", provider)
        
        result = await payment_manager.process_payment(
            provider_name="mock",
            amount=Decimal("25.50"),
            currency="USD",
            user_id=123456,
            description="Test payment"
        )
        
        assert result.success is True
        assert result.amount == Decimal("25.50")
        assert result.currency == "USD"
        assert result.transaction_id.startswith("mock_tx_")
        
        # Should log the payment
        mock_persistence.set.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_payment_failure(self, payment_manager, mock_persistence):
        """Test failed payment processing."""
        provider = MockPaymentProvider(should_succeed=False)
        payment_manager.register_provider("mock", provider)
        
        result = await payment_manager.process_payment(
            provider_name="mock",
            amount=Decimal("25.50"),
            currency="USD",
            user_id=123456,
            description="Test payment"
        )
        
        assert result.success is False
        assert result.transaction_id is None
    
    @pytest.mark.asyncio
    async def test_process_payment_provider_not_found(self, payment_manager):
        """Test payment processing with non-existent provider."""
        with pytest.raises(ValueError, match="Provider 'nonexistent' not found"):
            await payment_manager.process_payment(
                provider_name="nonexistent",
                amount=Decimal("10.00"),
                currency="USD",
                user_id=123456
            )
    
    @pytest.mark.asyncio
    async def test_process_payment_default_currency(self, payment_manager):
        """Test payment processing with default currency."""
        provider = MockPaymentProvider(should_succeed=True)
        payment_manager.register_provider("mock", provider)
        
        result = await payment_manager.process_payment(
            provider_name="mock",
            amount=Decimal("10.00"),
            user_id=123456
        )
        
        assert result.currency == "USD"  # Default currency
    
    @pytest.mark.asyncio
    async def test_verify_payment_success(self, payment_manager):
        """Test successful payment verification."""
        provider = MockPaymentProvider(should_succeed=True)
        payment_manager.register_provider("mock", provider)
        
        result = await payment_manager.verify_payment("mock", "mock_tx_1")
        
        assert result.success is True
        assert result.transaction_id == "mock_tx_1"
    
    @pytest.mark.asyncio
    async def test_verify_payment_failure(self, payment_manager):
        """Test failed payment verification."""
        provider = MockPaymentProvider(should_succeed=False)
        payment_manager.register_provider("mock", provider)
        
        result = await payment_manager.verify_payment("mock", "invalid_tx")
        
        assert result.success is False
    
    @pytest.mark.asyncio
    async def test_refund_payment_success(self, payment_manager):
        """Test successful payment refund."""
        provider = MockPaymentProvider(should_succeed=True)
        payment_manager.register_provider("mock", provider)
        
        result = await payment_manager.refund_payment("mock", "mock_tx_1")
        
        assert result.success is True
        assert result.transaction_id.startswith("refund_")
    
    @pytest.mark.asyncio
    async def test_refund_payment_partial(self, payment_manager):
        """Test partial payment refund."""
        provider = MockPaymentProvider(should_succeed=True)
        payment_manager.register_provider("mock", provider)
        
        result = await payment_manager.refund_payment(
            "mock", "mock_tx_1", Decimal("5.00")
        )
        
        assert result.success is True
        assert result.amount == Decimal("5.00")
    
    @pytest.mark.asyncio
    async def test_get_payment_history(self, payment_manager, mock_persistence):
        """Test getting payment history."""
        mock_persistence.get.return_value = [
            {
                'transaction_id': 'tx_1',
                'amount': '10.00',
                'currency': 'USD',
                'status': 'SUCCESS'
            }
        ]
        
        history = await payment_manager.get_payment_history(123456)
        
        assert len(history) == 1
        assert history[0]['transaction_id'] == 'tx_1'
        mock_persistence.get.assert_called_with("payments:user:123456", [])
    
    @pytest.mark.asyncio
    async def test_get_payment_history_empty(self, payment_manager, mock_persistence):
        """Test getting empty payment history."""
        mock_persistence.get.return_value = []
        
        history = await payment_manager.get_payment_history(999999)
        
        assert history == []
    
    def test_get_supported_currencies(self, payment_manager):
        """Test getting supported currencies."""
        provider1 = Mock()
        provider1.get_supported_currencies = Mock(return_value=['USD', 'EUR'])
        provider2 = Mock()
        provider2.get_supported_currencies = Mock(return_value=['USD', 'GBP', 'CAD'])
        
        payment_manager.register_provider("provider1", provider1)
        payment_manager.register_provider("provider2", provider2)
        
        currencies = payment_manager.get_supported_currencies()
        
        # Should return union of all supported currencies
        assert 'USD' in currencies
        assert 'EUR' in currencies
        assert 'GBP' in currencies
        assert 'CAD' in currencies
    
    def test_get_provider_info(self, payment_manager):
        """Test getting provider information."""
        provider = Mock()
        provider.name = "Mock Provider"
        provider.get_info = Mock(return_value={
            'name': 'Mock Provider',
            'version': '1.0.0',
            'supported_currencies': ['USD', 'EUR']
        })
        
        payment_manager.register_provider("mock", provider)
        
        info = payment_manager.get_provider_info("mock")
        
        assert info['name'] == 'Mock Provider'
        assert 'USD' in info['supported_currencies']
    
    def test_get_provider_info_not_found(self, payment_manager):
        """Test getting info for non-existent provider."""
        info = payment_manager.get_provider_info("nonexistent")
        
        assert info is None
    
    @pytest.mark.asyncio
    async def test_payment_logging_disabled(self, mock_persistence):
        """Test payment manager with logging disabled."""
        config = {
            'payments.default_currency': 'USD',
            'payments.enable_logging': False
        }
        payment_manager = PaymentManager(config, mock_persistence)
        
        provider = MockPaymentProvider(should_succeed=True)
        payment_manager.register_provider("mock", provider)
        
        result = await payment_manager.process_payment(
            provider_name="mock",
            amount=Decimal("10.00"),
            currency="USD",
            user_id=123456
        )
        
        assert result.success is True
        # Should not log when logging is disabled
        mock_persistence.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_concurrent_payments(self, payment_manager):
        """Test concurrent payment processing."""
        provider = MockPaymentProvider(should_succeed=True)
        payment_manager.register_provider("mock", provider)
        
        # Process multiple payments concurrently
        import asyncio
        tasks = []
        for i in range(5):
            task = payment_manager.process_payment(
                provider_name="mock",
                amount=Decimal("10.00"),
                currency="USD",
                user_id=123456 + i,
                description=f"Payment {i}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All payments should succeed
        assert all(result.success for result in results)
        
        # All should have unique transaction IDs
        tx_ids = [result.transaction_id for result in results]
        assert len(set(tx_ids)) == len(tx_ids)
    
    @pytest.mark.asyncio
    async def test_payment_validation(self, payment_manager):
        """Test payment parameter validation."""
        provider = MockPaymentProvider(should_succeed=True)
        payment_manager.register_provider("mock", provider)
        
        # Test negative amount
        with pytest.raises(ValueError, match="Amount must be positive"):
            await payment_manager.process_payment(
                provider_name="mock",
                amount=Decimal("-10.00"),
                currency="USD",
                user_id=123456
            )
        
        # Test zero amount
        with pytest.raises(ValueError, match="Amount must be positive"):
            await payment_manager.process_payment(
                provider_name="mock",
                amount=Decimal("0.00"),
                currency="USD",
                user_id=123456
            )
        
        # Test invalid user ID
        with pytest.raises(ValueError, match="User ID must be positive"):
            await payment_manager.process_payment(
                provider_name="mock",
                amount=Decimal("10.00"),
                currency="USD",
                user_id=-1
            )
