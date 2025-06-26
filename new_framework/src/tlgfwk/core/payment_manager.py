"""
Payment Management System

This module provides payment integration functionality for the Telegram Bot Framework.
Supports multiple payment providers including Stripe, PayPal, and PIX (Brazil).
"""

import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
import logging
from decimal import Decimal
import hashlib
import hmac

from ..utils.logger import get_logger


class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    SUCCESS = "success"  # Alias for COMPLETED
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class PaymentProvider(Enum):
    """Payment provider enumeration."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    PIX = "pix"
    TELEGRAM = "telegram"
    CUSTOM = "custom"


@dataclass
class PaymentItem:
    """Individual payment item."""
    name: str
    description: str
    price: Decimal
    quantity: int = 1
    currency: str = "USD"
    
    @property
    def total(self) -> Decimal:
        """Calculate total price for this item."""
        return self.price * self.quantity


@dataclass
class PaymentRequest:
    """Payment request data."""
    id: str
    user_id: int
    provider: PaymentProvider
    items: List[PaymentItem]
    currency: str
    total_amount: Decimal
    description: str
    status: PaymentStatus
    created_at: datetime
    expires_at: Optional[datetime] = None
    payment_url: Optional[str] = None
    provider_payment_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PaymentResult:
    """Payment processing result."""
    status: PaymentStatus
    transaction_id: Optional[str]
    amount: Decimal
    currency: str
    message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    
    @property
    def success(self) -> bool:
        """Determine if payment was successful."""
        return self.status in (PaymentStatus.SUCCESS, PaymentStatus.COMPLETED)


class PaymentProvider_Base:
    """Base class for payment providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize payment provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """
        Create a payment with the provider.
        
        Args:
            request: Payment request data
            
        Returns:
            PaymentResult with success status and details
        """
        raise NotImplementedError("Subclasses must implement create_payment")
    
    def verify_payment(self, payment_id: str, provider_data: Dict[str, Any]) -> PaymentResult:
        """
        Verify a payment with the provider.
        
        Args:
            payment_id: Internal payment ID
            provider_data: Provider-specific verification data
            
        Returns:
            PaymentResult with verification status
        """
        raise NotImplementedError("Subclasses must implement verify_payment")
    
    def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> PaymentResult:
        """
        Refund a payment.
        
        Args:
            payment_id: Internal payment ID
            amount: Amount to refund (None for full refund)
            
        Returns:
            PaymentResult with refund status
        """
        raise NotImplementedError("Subclasses must implement refund_payment")


class StripeProvider(PaymentProvider_Base):
    """Stripe payment provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Initialize Stripe (would require stripe library)
        self.api_key = config.get('api_key')
        self.webhook_secret = config.get('webhook_secret')
        
        if not self.api_key:
            raise ValueError("Stripe API key is required")
    
    def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a Stripe payment session."""
        try:
            # This is a mock implementation
            # In real implementation, you would use the Stripe SDK
            
            # Create payment session
            session_data = {
                'payment_method_types': ['card'],
                'line_items': [
                    {
                        'price_data': {
                            'currency': item.currency.lower(),
                            'product_data': {
                                'name': item.name,
                                'description': item.description,
                            },
                            'unit_amount': int(item.price * 100),  # Stripe uses cents
                        },
                        'quantity': item.quantity,
                    }
                    for item in request.items
                ],
                'mode': 'payment',
                'success_url': f'https://your-domain.com/success?session_id={{CHECKOUT_SESSION_ID}}',
                'cancel_url': f'https://your-domain.com/cancel',
                'metadata': {
                    'payment_id': request.id,
                    'user_id': str(request.user_id),
                    **request.metadata
                }
            }
            
            # Mock response
            session_id = f"cs_test_{uuid.uuid4().hex[:24]}"
            payment_url = f"https://checkout.stripe.com/pay/{session_id}"
            
            request.payment_url = payment_url
            request.provider_payment_id = session_id
            request.status = PaymentStatus.PENDING
            
            self.logger.info(f"Created Stripe payment session: {session_id}")
            
            return PaymentResult(
                success=True,
                payment_request=request,
                provider_response={'session_id': session_id, 'url': payment_url}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create Stripe payment: {e}")
            return PaymentResult(
                success=False,
                payment_request=request,
                error_message=str(e)
            )
    
    def verify_payment(self, payment_id: str, provider_data: Dict[str, Any]) -> PaymentResult:
        """Verify Stripe payment via webhook."""
        try:
            # Verify webhook signature
            signature = provider_data.get('stripe_signature')
            payload = provider_data.get('payload', '')
            
            if self.webhook_secret and signature:
                if not self._verify_webhook_signature(payload, signature):
                    raise ValueError("Invalid webhook signature")
            
            # Parse webhook data
            event_data = json.loads(payload) if isinstance(payload, str) else payload
            
            if event_data.get('type') == 'checkout.session.completed':
                session = event_data['data']['object']
                payment_status = PaymentStatus.COMPLETED
            elif event_data.get('type') == 'payment_intent.payment_failed':
                payment_status = PaymentStatus.FAILED
            else:
                payment_status = PaymentStatus.PENDING
            
            # Create mock payment request for verification
            request = PaymentRequest(
                id=payment_id,
                user_id=0,  # Would be populated from stored data
                provider=PaymentProvider.STRIPE,
                items=[],
                currency="USD",
                total_amount=Decimal("0"),
                description="",
                status=payment_status,
                created_at=datetime.now()
            )
            
            return PaymentResult(
                success=True,
                payment_request=request,
                provider_response=event_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to verify Stripe payment: {e}")
            return PaymentResult(
                success=False,
                payment_request=None,
                error_message=str(e)
            )
    
    def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> PaymentResult:
        """Refund Stripe payment."""
        try:
            # Mock refund implementation
            self.logger.info(f"Processing Stripe refund for payment: {payment_id}")
            
            # Create mock request
            request = PaymentRequest(
                id=payment_id,
                user_id=0,
                provider=PaymentProvider.STRIPE,
                items=[],
                currency="USD",
                total_amount=amount or Decimal("0"),
                description="Refund",
                status=PaymentStatus.REFUNDED,
                created_at=datetime.now()
            )
            
            return PaymentResult(success=True, payment_request=request)
            
        except Exception as e:
            self.logger.error(f"Failed to refund Stripe payment: {e}")
            return PaymentResult(
                success=False,
                payment_request=None,
                error_message=str(e)
            )
    
    def _verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Stripe webhook signature."""
        try:
            elements = signature.split(',')
            timestamp = None
            signatures = []
            
            for element in elements:
                key, value = element.split('=', 1)
                if key == 't':
                    timestamp = value
                elif key == 'v1':
                    signatures.append(value)
            
            if not timestamp or not signatures:
                return False
            
            # Compute expected signature
            signed_payload = f"{timestamp}.{payload}"
            expected_sig = hmac.new(
                self.webhook_secret.encode(),
                signed_payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return expected_sig in signatures
            
        except Exception as e:
            self.logger.error(f"Error verifying webhook signature: {e}")
            return False


class PIXProvider(PaymentProvider_Base):
    """PIX payment provider implementation (Brazil)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.bank_code = config.get('bank_code')
        self.account_key = config.get('account_key')  # PIX key
        self.merchant_name = config.get('merchant_name', 'Merchant')
        self.merchant_city = config.get('merchant_city', 'City')
        
        if not self.account_key:
            raise ValueError("PIX account key is required")
    
    def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a PIX payment (QR code generation)."""
        try:
            # Generate PIX QR code data
            qr_data = self._generate_pix_qr_code(request)
            
            request.payment_url = f"pix://qr?data={qr_data}"
            request.provider_payment_id = f"pix_{uuid.uuid4().hex[:16]}"
            request.status = PaymentStatus.PENDING
            request.expires_at = datetime.now() + timedelta(minutes=30)  # PIX payments expire
            
            self.logger.info(f"Created PIX payment: {request.provider_payment_id}")
            
            return PaymentResult(
                success=True,
                payment_request=request,
                provider_response={'qr_code': qr_data, 'expires_in': 1800}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create PIX payment: {e}")
            return PaymentResult(
                success=False,
                payment_request=request,
                error_message=str(e)
            )
    
    def verify_payment(self, payment_id: str, provider_data: Dict[str, Any]) -> PaymentResult:
        """Verify PIX payment (would integrate with bank API)."""
        try:
            # Mock verification - in reality, you'd check with bank API
            transaction_id = provider_data.get('transaction_id')
            
            if transaction_id:
                status = PaymentStatus.COMPLETED
            else:
                status = PaymentStatus.PENDING
            
            request = PaymentRequest(
                id=payment_id,
                user_id=0,
                provider=PaymentProvider.PIX,
                items=[],
                currency="BRL",
                total_amount=Decimal("0"),
                description="",
                status=status,
                created_at=datetime.now()
            )
            
            return PaymentResult(
                success=True,
                payment_request=request,
                provider_response=provider_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to verify PIX payment: {e}")
            return PaymentResult(
                success=False,
                payment_request=None,
                error_message=str(e)
            )
    
    def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> PaymentResult:
        """PIX refunds are typically manual processes."""
        self.logger.info(f"PIX refund requested for payment: {payment_id}")
        
        # PIX refunds usually require manual intervention
        return PaymentResult(
            success=False,
            payment_request=None,
            error_message="PIX refunds require manual processing"
        )
    
    def _generate_pix_qr_code(self, request: PaymentRequest) -> str:
        """Generate PIX QR code data (simplified)."""
        # This is a simplified implementation
        # Real PIX QR codes follow the EMV QR Code specification
        
        amount_str = f"{float(request.total_amount):.2f}"
        description = request.description[:50]  # Limit description length
        
        # Mock QR data
        qr_data = (
            f"00020126360014br.gov.bcb.pix0114{self.account_key}"
            f"52040000530398654{len(amount_str):02d}{amount_str}"
            f"5802BR59{len(self.merchant_name):02d}{self.merchant_name}"
            f"60{len(self.merchant_city):02d}{self.merchant_city}"
            f"62{len(description)+4:02d}05{len(description):02d}{description}6304"
        )
        
        # Add CRC16 checksum (simplified)
        checksum = self._calculate_crc16(qr_data)
        qr_data += f"{checksum:04X}"
        
        return qr_data
    
    def _calculate_crc16(self, data: str) -> int:
        """Calculate CRC16 checksum for PIX QR code."""
        # Simplified CRC16 calculation
        # Real implementation should use proper CRC16-CCITT
        return abs(hash(data)) % 65536


class PaymentManager:
    """
    Payment Manager for the Telegram Bot Framework.
    
    Handles payment processing across multiple providers.
    """
    
    def __init__(self, config: Dict[str, Any], persistence_manager=None):
        """
        Initialize the payment manager.
        
        Args:
            config: Payment configuration dictionary
            persistence_manager: Optional persistence manager for storing payment data
        """
        self.config = config
        self.persistence = persistence_manager
        self.logger = get_logger(__name__)
        
        # Payment storage
        self.payments: Dict[str, PaymentRequest] = {}
        
        # Payment providers
        self.providers = {}
        
        # Set default currency
        self.default_currency = config.get('payments.default_currency', 'USD')
        
        # Check if payment logging is enabled
        self.enable_logging = config.get('payments.enable_logging', True)
        
        # Set default currency
        self.default_currency = config.get('payments.default_currency', 'USD')
        
        # Check if payment logging is enabled
        self.enable_logging = config.get('payments.enable_logging', True)
        
        # Event callbacks
        self.payment_callbacks: Dict[str, List[Callable]] = {
            'payment_created': [],
            'payment_completed': [],
            'payment_failed': [],
            'payment_cancelled': [],
            'payment_refunded': []
        }
        
        # Initialize providers
        self._initialize_providers()
        
        self.logger.info("Payment manager initialized")
    
    def _initialize_providers(self):
        """Initialize payment providers based on configuration."""
        # Get provider configs safely
        if isinstance(self.config, dict):
            provider_configs = self.config.get('providers', {})
        else:
            provider_configs = {}
        
        # Initialize Stripe
        if isinstance(provider_configs, dict) and 'stripe' in provider_configs:
            try:
                self.providers[PaymentProvider.STRIPE] = StripeProvider(
                    provider_configs['stripe']
                )
                self.logger.info("Stripe provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Stripe provider: {e}")
        
        # Initialize PIX
        if 'pix' in provider_configs:
            try:
                self.providers[PaymentProvider.PIX] = PIXProvider(
                    provider_configs['pix']
                )
                self.logger.info("PIX provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize PIX provider: {e}")
        
        # Initialize other providers as needed
    
    def create_payment(
        self,
        user_id: int,
        items: List[PaymentItem],
        provider: PaymentProvider,
        description: str = "",
        currency: str = "USD",
        expires_in_minutes: int = 60,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Create a new payment request.
        
        Args:
            user_id: Telegram user ID
            items: List of payment items
            provider: Payment provider to use
            description: Payment description
            currency: Payment currency
            expires_in_minutes: Payment expiration time
            metadata: Additional metadata
            
        Returns:
            PaymentResult with creation status
        """
        try:
            # Validate provider
            if provider not in self.providers:
                raise ValueError(f"Provider {provider.value} is not configured")
            
            # Calculate total amount
            total_amount = sum(item.total for item in items)
            
            # Generate payment ID
            payment_id = f"pay_{uuid.uuid4().hex[:16]}"
            
            # Create payment request
            request = PaymentRequest(
                id=payment_id,
                user_id=user_id,
                provider=provider,
                items=items,
                currency=currency,
                total_amount=total_amount,
                description=description,
                status=PaymentStatus.PENDING,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=expires_in_minutes),
                metadata=metadata or {}
            )
            
            # Create payment with provider
            provider_instance = self.providers[provider]
            result = provider_instance.create_payment(request)
            
            if result.success:
                # Store payment
                self.payments[payment_id] = result.payment_request
                
                # Store in persistent storage
                if hasattr(self.bot, 'persistence'):
                    self.bot.persistence.save_payment_data(payment_id, asdict(result.payment_request))
                
                # Trigger callbacks
                self._trigger_callbacks('payment_created', result.payment_request)
                
                self.logger.info(f"Payment created successfully: {payment_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create payment: {e}")
            return PaymentResult(
                success=False,
                payment_request=None,
                error_message=str(e)
            )
    
    def verify_payment(
        self,
        payment_id: str,
        provider_data: Dict[str, Any]
    ) -> PaymentResult:
        """
        Verify a payment with the provider.
        
        Args:
            payment_id: Payment ID to verify
            provider_data: Provider-specific verification data
            
        Returns:
            PaymentResult with verification status
        """
        try:
            # Get stored payment
            if payment_id not in self.payments:
                # Try to load from persistent storage
                if hasattr(self.bot, 'persistence'):
                    payment_data = self.bot.persistence.load_payment_data(payment_id)
                    if payment_data:
                        self.payments[payment_id] = PaymentRequest(**payment_data)
                
                if payment_id not in self.payments:
                    raise ValueError(f"Payment {payment_id} not found")
            
            payment = self.payments[payment_id]
            provider_instance = self.providers[payment.provider]
            
            # Verify with provider
            result = provider_instance.verify_payment(payment_id, provider_data)
            
            if result.success and result.payment_request:
                # Update payment status
                old_status = payment.status
                payment.status = result.payment_request.status
                
                # Update persistent storage
                if hasattr(self.bot, 'persistence'):
                    self.bot.persistence.save_payment_data(payment_id, asdict(payment))
                
                # Trigger status change callbacks
                if old_status != payment.status:
                    event_name = f"payment_{payment.status.value}"
                    if event_name in self.payment_callbacks:
                        self._trigger_callbacks(event_name, payment)
                
                self.logger.info(f"Payment verified: {payment_id} -> {payment.status.value}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to verify payment {payment_id}: {e}")
            return PaymentResult(
                success=False,
                payment_request=None,
                error_message=str(e)
            )
    
    def get_payment(self, payment_id: str) -> Optional[PaymentRequest]:
        """
        Get a payment by ID.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            PaymentRequest or None if not found
        """
        if payment_id in self.payments:
            return self.payments[payment_id]
        
        # Try to load from persistent storage
        if hasattr(self.bot, 'persistence'):
            payment_data = self.bot.persistence.load_payment_data(payment_id)
            if payment_data:
                payment = PaymentRequest(**payment_data)
                self.payments[payment_id] = payment
                return payment
        
        return None
    
    def list_user_payments(
        self,
        user_id: int,
        status_filter: Optional[PaymentStatus] = None
    ) -> List[PaymentRequest]:
        """
        List payments for a specific user.
        
        Args:
            user_id: User ID
            status_filter: Optional status filter
            
        Returns:
            List of PaymentRequest objects
        """
        user_payments = [
            payment for payment in self.payments.values()
            if payment.user_id == user_id
        ]
        
        if status_filter:
            user_payments = [
                payment for payment in user_payments
                if payment.status == status_filter
            ]
        
        return user_payments
    
    def cancel_payment(self, payment_id: str) -> bool:
        """
        Cancel a pending payment.
        
        Args:
            payment_id: Payment ID to cancel
            
        Returns:
            True if successful
        """
        try:
            payment = self.get_payment(payment_id)
            if not payment:
                return False
            
            if payment.status != PaymentStatus.PENDING:
                self.logger.warning(f"Cannot cancel payment {payment_id} with status {payment.status}")
                return False
            
            # Update status
            payment.status = PaymentStatus.CANCELLED
            
            # Update persistent storage
            if hasattr(self.bot, 'persistence'):
                self.bot.persistence.save_payment_data(payment_id, asdict(payment))
            
            # Trigger callbacks
            self._trigger_callbacks('payment_cancelled', payment)
            
            self.logger.info(f"Payment cancelled: {payment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel payment {payment_id}: {e}")
            return False
    
    def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> PaymentResult:
        """
        Refund a completed payment.
        
        Args:
            payment_id: Payment ID to refund
            amount: Amount to refund (None for full refund)
            
        Returns:
            PaymentResult with refund status
        """
        try:
            payment = self.get_payment(payment_id)
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")
            
            if payment.status != PaymentStatus.COMPLETED:
                raise ValueError(f"Cannot refund payment with status {payment.status}")
            
            provider_instance = self.providers[payment.provider]
            result = provider_instance.refund_payment(payment_id, amount)
            
            if result.success:
                # Update payment status
                payment.status = PaymentStatus.REFUNDED
                
                # Update persistent storage
                if hasattr(self.bot, 'persistence'):
                    self.bot.persistence.save_payment_data(payment_id, asdict(payment))
                
                # Trigger callbacks
                self._trigger_callbacks('payment_refunded', payment)
                
                self.logger.info(f"Payment refunded: {payment_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to refund payment {payment_id}: {e}")
            return PaymentResult(
                success=False,
                payment_request=None,
                error_message=str(e)
            )
    
    def add_payment_callback(self, event: str, callback: Callable):
        """
        Add a payment event callback.
        
        Args:
            event: Event name (payment_created, payment_completed, etc.)
            callback: Callback function
        """
        if event in self.payment_callbacks:
            self.payment_callbacks[event].append(callback)
        else:
            self.logger.warning(f"Unknown payment event: {event}")
    
    def _trigger_callbacks(self, event: str, payment: PaymentRequest):
        """Trigger callbacks for a payment event."""
        for callback in self.payment_callbacks.get(event, []):
            try:
                callback(payment)
            except Exception as e:
                self.logger.error(f"Error in payment callback for {event}: {e}")
    
    def cleanup_expired_payments(self):
        """Clean up expired payments."""
        now = datetime.now()
        expired_payments = []
        
        for payment_id, payment in self.payments.items():
            if (payment.expires_at and 
                payment.expires_at < now and 
                payment.status == PaymentStatus.PENDING):
                expired_payments.append(payment_id)
        
        for payment_id in expired_payments:
            payment = self.payments[payment_id]
            payment.status = PaymentStatus.EXPIRED
            
            # Update persistent storage
            if hasattr(self.bot, 'persistence'):
                self.bot.persistence.save_payment_data(payment_id, asdict(payment))
            
            self.logger.info(f"Payment expired: {payment_id}")
        
        return len(expired_payments)
    
    def register_provider(self, name: str, provider):
        """
        Register a payment provider.
        
        Args:
            name: Provider name
            provider: Payment provider instance
            
        Raises:
            ValueError: If provider with the same name is already registered
        """
        if name in self.providers:
            raise ValueError(f"Provider '{name}' already registered")
        
        self.providers[name] = provider
        self.logger.info(f"Payment provider '{name}' registered")
        return True
    
    def unregister_provider(self, name: str) -> bool:
        """
        Unregister a payment provider.
        
        Args:
            name: Provider name
            
        Returns:
            True if provider was unregistered, False if not found
        """
        if name in self.providers:
            del self.providers[name]
            self.logger.info(f"Payment provider '{name}' unregistered")
            return True
        else:
            self.logger.warning(f"Attempted to unregister non-existent provider '{name}'")
            return False
    
    def get_provider_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered payment provider.
        
        Args:
            name: Provider name
            
        Returns:
            Provider information dict or None if not found
        """
        if name not in self.providers:
            return None
            
        provider = self.providers[name]
        if hasattr(provider, 'get_info') and callable(provider.get_info):
            return provider.get_info()
        
        # Default basic info
        info = {
            'name': getattr(provider, 'name', name),
            'supported_currencies': self.get_provider_supported_currencies(name)
        }
        
        return info
    
    def get_provider_supported_currencies(self, name: str) -> List[str]:
        """
        Get currencies supported by a specific provider.
        
        Args:
            name: Provider name
            
        Returns:
            List of currency codes
        """
        if name not in self.providers:
            return []
            
        provider = self.providers[name]
        if hasattr(provider, 'get_supported_currencies') and callable(provider.get_supported_currencies):
            return provider.get_supported_currencies()
        
        # Default to USD if no method is available
        return ['USD']
    
    def get_supported_currencies(self) -> List[str]:
        """
        Get all currencies supported by any payment provider.
        
        Returns:
            List of unique currency codes supported across all providers
        """
        all_currencies = set()
        
        for name, provider in self.providers.items():
            currencies = self.get_provider_supported_currencies(name)
            all_currencies.update(currencies)
        
        return list(all_currencies)
    
    async def process_payment(
        self, 
        provider_name: str, 
        amount: Decimal, 
        user_id: int, 
        currency: str = None,
        description: str = ""
    ) -> PaymentResult:
        """
        Process a payment using the specified provider.
        
        Args:
            provider_name: Name of the registered payment provider to use
            amount: Payment amount
            user_id: Telegram user ID
            currency: Payment currency (uses default if not specified)
            description: Payment description
            
        Returns:
            PaymentResult with processing status
            
        Raises:
            ValueError: If provider not found or invalid parameters
        """
        # Validate parameters
        if amount <= Decimal('0'):
            raise ValueError("Amount must be positive")
        
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        
        # Use default currency if not specified
        if currency is None:
            currency = self.default_currency
        
        # Check if provider exists
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        provider = self.providers[provider_name]
        
        # Process payment
        try:
            result = await provider.process_payment(
                amount=amount,
                currency=currency,
                user_id=user_id,
                description=description
            )
            
            # Log successful payments if enabled
            if self.enable_logging and result.success and self.persistence:
                payment_data = {
                    'user_id': user_id,
                    'provider': provider_name,
                    'amount': str(amount),
                    'currency': currency,
                    'transaction_id': result.transaction_id,
                    'description': description,
                    'status': result.status.value,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store in user payment history
                try:
                    history_key = f"payments:user:{user_id}"
                    history = await self.persistence.get(history_key, [])
                    history.append(payment_data)
                    await self.persistence.set(history_key, history)
                except Exception as e:
                    self.logger.error(f"Failed to log payment: {e}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Payment processing error: {e}")
            return PaymentResult(
                status=PaymentStatus.FAILED,
                transaction_id=None,
                amount=amount,
                currency=currency,
                message=f"Payment processing error: {str(e)}"
            )
    
    async def verify_payment(self, provider_name: str, transaction_id: str) -> PaymentResult:
        """
        Verify a payment with a provider.
        
        Args:
            provider_name: Name of the registered payment provider
            transaction_id: Transaction ID to verify
            
        Returns:
            PaymentResult with verification status
        """
        if provider_name not in self.providers:
            return PaymentResult(
                status=PaymentStatus.FAILED,
                transaction_id=transaction_id,
                amount=Decimal("0.00"),
                currency="",
                message=f"Provider '{provider_name}' not found"
            )
            
        try:
            provider = self.providers[provider_name]
            return await provider.verify_payment(transaction_id)
        except Exception as e:
            self.logger.error(f"Payment verification error: {e}")
            return PaymentResult(
                status=PaymentStatus.FAILED,
                transaction_id=transaction_id,
                amount=Decimal("0.00"),
                currency="",
                message=f"Payment verification error: {str(e)}"
            )
    
    async def refund_payment(
        self, 
        provider_name: str, 
        transaction_id: str, 
        amount: Decimal = None
    ) -> PaymentResult:
        """
        Refund a payment.
        
        Args:
            provider_name: Name of the registered payment provider
            transaction_id: Transaction ID to refund
            amount: Refund amount (None for full refund)
            
        Returns:
            PaymentResult with refund status
        """
        if provider_name not in self.providers:
            return PaymentResult(
                status=PaymentStatus.FAILED,
                transaction_id=transaction_id,
                amount=amount or Decimal("0.00"),
                currency="",
                message=f"Provider '{provider_name}' not found"
            )
            
        try:
            provider = self.providers[provider_name]
            return await provider.refund_payment(transaction_id, amount)
        except Exception as e:
            self.logger.error(f"Payment refund error: {e}")
            return PaymentResult(
                status=PaymentStatus.FAILED,
                transaction_id=transaction_id,
                amount=amount or Decimal("0.00"),
                currency="",
                message=f"Payment refund error: {str(e)}"
            )
    
    async def get_payment_history(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get payment history for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of payment records
        """
        if not self.persistence:
            return []
            
        try:
            history_key = f"payments:user:{user_id}"
            history = await self.persistence.get(history_key, [])
            return history
        except Exception as e:
            self.logger.error(f"Failed to get payment history: {e}")
            return []
