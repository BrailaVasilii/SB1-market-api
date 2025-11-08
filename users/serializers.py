from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from users.models import Payment, Subscription
from materials.serializers import CourseSerializer, LessonSerializer

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    
    paid_course_title = serializers.CharField(source='paid_course.title', read_only=True)
    paid_lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date', 
            'paid_course', 'paid_course_title',
            'paid_lesson', 'paid_lesson_title',
            'payment_amount', 'payment_method'
        ]
        read_only_fields = ['id', 'payment_date']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'phone', 'city', 'avatar']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
        
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_email', 'course', 'course_title', 
            'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']


class UserProfileSerializer(UserSerializer):
    """Extended User serializer with payment history"""
    
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['payments']