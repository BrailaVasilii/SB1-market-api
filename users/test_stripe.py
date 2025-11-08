"""
Tests for Stripe integration following TDD principles.
"""

from decimal import Decimal
from unittest.mock import Mock, patch
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from materials.models import Course, Lesson
from users.models import Payment
from users.services import StripeService

User = get_user_model()


class StripeServiceTests(TestCase):
    """Test suite for Stripe service functions."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            course=self.course,
            owner=self.user
        )
        
    @patch('stripe.Product.create')
    def test_create_stripe_product_success(self, mock_create: Mock) -> None:
        """Test successful Stripe product creation."""
        # Arrange (Red phase)
        mock_create.return_value = Mock(id='prod_test123')
        service = StripeService()
        
        # Act
        product_id = service.create_product('Test Course', 'Course description')
        
        # Assert
        self.assertEqual(product_id, 'prod_test123')
        mock_create.assert_called_once_with(
            name='Test Course',
            description='Course description'
        )
        
    @patch('stripe.Price.create')
    def test_create_stripe_price_success(self, mock_create: Mock) -> None:
        """Test successful Stripe price creation."""
        # Arrange (Red phase)
        mock_create.return_value = Mock(id='price_test123')
        service = StripeService()
        
        # Act
        price_id = service.create_price('prod_test123', Decimal('29.99'))
        
        # Assert
        self.assertEqual(price_id, 'price_test123')
        mock_create.assert_called_once_with(
            product='prod_test123',
            unit_amount=2999,  # Amount in cents
            currency='usd'
        )
        
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_success(self, mock_create: Mock) -> None:
        """Test successful Stripe checkout session creation."""
        # Arrange (Red phase)
        mock_create.return_value = Mock(
            id='cs_test123',
            url='https://checkout.stripe.com/c/pay/test123'
        )
        service = StripeService()
        
        # Act
        session_data = service.create_checkout_session('price_test123')
        
        # Assert
        self.assertEqual(session_data['session_id'], 'cs_test123')
        self.assertEqual(session_data['checkout_url'], 'https://checkout.stripe.com/c/pay/test123')
        mock_create.assert_called_once()
        
    @patch('stripe.checkout.Session.retrieve')
    def test_retrieve_session_status_success(self, mock_retrieve: Mock) -> None:
        """Test successful session status retrieval."""
        # Arrange (Red phase)
        mock_retrieve.return_value = Mock(
            payment_status='paid',
            status='complete'
        )
        service = StripeService()
        
        # Act
        status = service.get_session_status('cs_test123')
        
        # Assert
        self.assertEqual(status['payment_status'], 'paid')
        self.assertEqual(status['status'], 'complete')
        mock_retrieve.assert_called_once_with('cs_test123')
        
    @patch('stripe.Product.create')
    def test_create_product_handles_stripe_error(self, mock_create: Mock) -> None:
        """Test proper handling of Stripe API errors."""
        # Arrange (Red phase)
        from stripe import StripeError
        mock_create.side_effect = StripeError("API Error")
        service = StripeService()
        
        # Act & Assert
        with self.assertRaises(StripeError):
            service.create_product('Test', 'Description')


class StripePaymentViewTests(APITestCase):
    """Test suite for Stripe payment views."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.client = APIClient()
        
    def test_create_course_payment_endpoint_exists(self) -> None:
        """Test that course payment endpoint will exist."""
        # This test will fail initially (Red phase)
        from django.urls import reverse
        url = reverse('users:create-course-payment')
        self.assertTrue(url)
        
    @patch('users.services.StripeService.create_product')
    @patch('users.services.StripeService.create_price')  
    @patch('users.services.StripeService.create_checkout_session')
    def test_create_course_payment_success(self, mock_session, mock_price, mock_product) -> None:
        """Test successful course payment creation."""
        # Arrange (Red phase)
        mock_product.return_value = 'prod_test123'
        mock_price.return_value = 'price_test123'
        mock_session.return_value = {
            'session_id': 'cs_test123',
            'checkout_url': 'https://checkout.stripe.com/test'
        }
        
        self.client.force_authenticate(user=self.user)
        url = reverse('users:create-course-payment')
        data = {
            'course_id': self.course.id,
            'amount': '29.99'
        }
        
        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertIn('checkout_url', response.data)
        self.assertIn('payment_id', response.data)


class PaymentModelStripeTests(TestCase):
    """Test suite for Payment model Stripe integration."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        
    def test_payment_model_has_stripe_fields(self) -> None:
        """Test that Payment model has required Stripe fields."""
        # This will fail initially (Red phase)
        payment = Payment(
            user=self.user,
            paid_course=self.course,
            payment_amount=Decimal('29.99'),
            payment_method='stripe'
        )
        
        # These fields should exist
        self.assertTrue(hasattr(payment, 'stripe_product_id'))
        self.assertTrue(hasattr(payment, 'stripe_price_id'))
        self.assertTrue(hasattr(payment, 'stripe_session_id'))
        self.assertTrue(hasattr(payment, 'stripe_checkout_url'))
        self.assertTrue(hasattr(payment, 'payment_status'))
        
    def test_payment_status_choices_include_stripe_statuses(self) -> None:
        """Test that payment status choices include Stripe statuses."""
        # This will fail initially (Red phase)
        from users.models import Payment
        
        status_choices = dict(Payment.PAYMENT_STATUS_CHOICES)
        self.assertIn('pending', status_choices)
        self.assertIn('paid', status_choices)
        self.assertIn('failed', status_choices)
        self.assertIn('canceled', status_choices)