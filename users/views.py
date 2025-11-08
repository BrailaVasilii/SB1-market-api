from decimal import Decimal
from rest_framework import generics, filters, viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, DateFilter
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from users.models import Payment, Subscription
from users.serializers import PaymentSerializer, UserSerializer, UserProfileSerializer, UserRegistrationSerializer, SubscriptionSerializer
from users.services import StripeService
from materials.models import Course, Lesson

User = get_user_model()


class PaymentFilter(FilterSet):
    """Filter for Payment model"""
    
    payment_method = CharFilter(field_name='payment_method', lookup_expr='exact')
    paid_course = CharFilter(field_name='paid_course__id', lookup_expr='exact')
    paid_lesson = CharFilter(field_name='paid_lesson__id', lookup_expr='exact')
    
    class Meta:
        model = Payment
        fields = ['payment_method', 'paid_course', 'paid_lesson']


class PaymentListView(generics.ListCreateAPIView):
    """List and create payments with filtering and sorting"""
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete payment"""
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """CRUD operations for users"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'], serializer_class=UserProfileSerializer)
    def profile(self, request, pk=None):
        """Get user profile with payment history"""
        user = self.get_object()
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class SubscriptionToggleView(APIView):
    """Toggle subscription for a course"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Toggle subscription to a course.
        If subscription exists - delete it.
        If subscription doesn't exist - create it.
        """
        user = request.user
        course_id = request.data.get('course_id')
        
        if not course_id:
            return Response(
                {"error": "course_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course_item = get_object_or_404(Course, id=course_id)
        
        # Check if subscription exists
        subs_item = Subscription.objects.filter(user=user, course=course_item)
        
        if subs_item.exists():
            # If subscription exists - delete it
            subs_item.delete()
            message = 'подписка удалена'
        else:
            # If subscription doesn't exist - create it
            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'
        
        return Response({"message": message})


class SubscriptionListView(generics.ListAPIView):
    """List user subscriptions"""
    
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user, is_active=True)


# Stripe Payment Views

class StripeCreateCoursePaymentView(APIView):
    """Create Stripe payment for a course"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs) -> Response:
        """
        Create a Stripe payment for a course.
        
        Expected data:
        {
            "course_id": 1,
            "amount": "29.99"
        }
        """
        user = request.user
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')
        
        if not course_id or not amount:
            return Response(
                {"error": "course_id and amount are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = get_object_or_404(Course, id=course_id)
            stripe_service = StripeService()
            
            # Create Stripe product
            product_id = stripe_service.create_product(
                name=course.title,
                description=course.description
            )
            
            # Create Stripe price
            price_id = stripe_service.create_price(
                product_id=product_id,
                amount=Decimal(amount)
            )
            
            # Create checkout session
            session_data = stripe_service.create_checkout_session(price_id)
            
            # Create payment record in database
            payment = Payment.objects.create(
                user=user,
                paid_course=course,
                payment_amount=Decimal(amount),
                payment_method='stripe',
                payment_status='pending',
                stripe_product_id=product_id,
                stripe_price_id=price_id,
                stripe_session_id=session_data['session_id'],
                stripe_checkout_url=session_data['checkout_url']
            )
            
            return Response({
                'payment_id': payment.id,
                'checkout_url': session_data['checkout_url'],
                'session_id': session_data['session_id']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class StripeCreateLessonPaymentView(APIView):
    """Create Stripe payment for a lesson"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs) -> Response:
        """
        Create a Stripe payment for a lesson.
        
        Expected data:
        {
            "lesson_id": 1,
            "amount": "9.99"
        }
        """
        user = request.user
        lesson_id = request.data.get('lesson_id')
        amount = request.data.get('amount')
        
        if not lesson_id or not amount:
            return Response(
                {"error": "lesson_id and amount are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            stripe_service = StripeService()
            
            # Create Stripe product
            product_id = stripe_service.create_product(
                name=lesson.title,
                description=lesson.description
            )
            
            # Create Stripe price
            price_id = stripe_service.create_price(
                product_id=product_id,
                amount=Decimal(amount)
            )
            
            # Create checkout session
            session_data = stripe_service.create_checkout_session(price_id)
            
            # Create payment record in database
            payment = Payment.objects.create(
                user=user,
                paid_lesson=lesson,
                payment_amount=Decimal(amount),
                payment_method='stripe',
                payment_status='pending',
                stripe_product_id=product_id,
                stripe_price_id=price_id,
                stripe_session_id=session_data['session_id'],
                stripe_checkout_url=session_data['checkout_url']
            )
            
            return Response({
                'payment_id': payment.id,
                'checkout_url': session_data['checkout_url'],
                'session_id': session_data['session_id']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class StripePaymentStatusView(APIView):
    """Check Stripe payment status"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, payment_id: int, *args, **kwargs) -> Response:
        """
        Check payment status via Stripe API and update local record.
        """
        try:
            payment = get_object_or_404(
                Payment, 
                id=payment_id, 
                user=request.user,
                payment_method='stripe'
            )
            
            if not payment.stripe_session_id:
                return Response(
                    {"error": "No Stripe session found for this payment"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stripe_service = StripeService()
            session_status = stripe_service.get_session_status(payment.stripe_session_id)
            
            # Map Stripe status to our status
            status_mapping = {
                'paid': 'paid',
                'unpaid': 'pending',
                'no_payment_required': 'paid'
            }
            
            new_status = status_mapping.get(session_status['payment_status'], 'pending')
            
            # Update payment status
            payment.payment_status = new_status
            payment.save()
            
            return Response({
                'payment_id': payment.id,
                'payment_status': payment.payment_status,
                'stripe_status': session_status['payment_status'],
                'session_status': session_status['status']
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
