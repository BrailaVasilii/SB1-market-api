from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users import views
from users.views import (
    StripeCreateCoursePaymentView,
    StripeCreateLessonPaymentView, 
    StripePaymentStatusView
)

app_name = 'users'

router = DefaultRouter()
router.register('users', views.UserViewSet)

urlpatterns = [
    # JWT Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    
    # Subscriptions
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscription-list'),
    path('subscriptions/toggle/', views.SubscriptionToggleView.as_view(), name='subscription-toggle'),
    
    # Stripe Payments
    path('stripe/create-course-payment/', StripeCreateCoursePaymentView.as_view(), name='create-course-payment'),
    path('stripe/create-lesson-payment/', StripeCreateLessonPaymentView.as_view(), name='create-lesson-payment'),
    path('stripe/payment-status/<int:payment_id>/', StripePaymentStatusView.as_view(), name='payment-status'),
    
    # Users CRUD via ViewSet
    path('', include(router.urls)),
]