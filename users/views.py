from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer, UserRegistrationSerializer

User = get_user_model()




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
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get user profile"""
        user = self.get_object()
        serializer = UserSerializer(user)
        return Response(serializer.data)


