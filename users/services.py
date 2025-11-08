"""
Stripe integration services for payment processing.

This module provides service functions for interacting with Stripe API
following the requirements from instruction.txt.
"""

from decimal import Decimal
from typing import Dict, Any
import stripe
from django.conf import settings


class StripeService:
    """Service class for Stripe API interactions."""
    
    def __init__(self) -> None:
        """Initialize Stripe service with API key."""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
    def create_product(self, name: str, description: str) -> str:
        """
        Create a product in Stripe.
        
        Args:
            name: Product name
            description: Product description
            
        Returns:
            str: Stripe product ID
            
        Raises:
            stripe.error.StripeError: If API call fails
        """
        try:
            product = stripe.Product.create(
                name=name,
                description=description
            )
            return product.id
        except stripe.StripeError as e:
            raise e
            
    def create_price(self, product_id: str, amount: Decimal) -> str:
        """
        Create a price for a product in Stripe.
        
        Args:
            product_id: Stripe product ID
            amount: Price amount in dollars
            
        Returns:
            str: Stripe price ID
            
        Raises:
            stripe.error.StripeError: If API call fails
        """
        try:
            # Convert amount to cents (Stripe requirement)
            amount_cents = int(amount * 100)
            
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_cents,
                currency='ron'
            )
            return price.id
        except stripe.StripeError as e:
            raise e
            
    def create_payment_intent(self, amount: Decimal, currency: str = 'ron') -> Dict[str, str]:
        """
        Create a payment intent for direct payment processing.
        
        Args:
            amount: Payment amount in dollars
            currency: Currency code (default: usd)
            
        Returns:
            Dict containing payment_intent_id and client_secret
            
        Raises:
            stripe.error.StripeError: If API call fails
        """
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                payment_method_types=['card'],
            )
            
            return {
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': amount_cents,
                'currency': currency
            }
        except stripe.StripeError as e:
            raise e

    def create_checkout_session(self, price_id: str) -> Dict[str, str]:
        """
        Create a checkout session for payment.
        
        Args:
            price_id: Stripe price ID
            
        Returns:
            Dict containing session_id and checkout_url
            
        Raises:
            stripe.error.StripeError: If API call fails
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://example.com/cancel',
                allow_promotion_codes=True,
                billing_address_collection='auto',
            )
            
            return {
                'session_id': session.id,
                'checkout_url': session.url
            }
        except stripe.StripeError as e:
            raise e
            
    def get_session_status(self, session_id: str) -> Dict[str, str]:
        """
        Retrieve session status from Stripe.
        
        Args:
            session_id: Stripe session ID
            
        Returns:
            Dict containing payment_status and status
            
        Raises:
            stripe.error.StripeError: If API call fails
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            return {
                'payment_status': session.payment_status,
                'status': session.status
            }
        except stripe.StripeError as e:
            raise e