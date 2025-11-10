from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()




class UserSerializer(serializers.ModelSerializer):
    """Serializer для User model"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'role']
        read_only_fields = ['id', 'role']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer для регистрации пользователя"""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'city']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


