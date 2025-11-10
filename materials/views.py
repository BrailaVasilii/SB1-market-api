from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsOwnerOrAdmin
from .paginators import AdvertisementPagination
from .filters import AdvertisementFilter
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action
from materials.models import Advertisement, Review
from materials.serializers import (
    AdvertisementSerializer, AdvertisementDetailSerializer,
    ReviewSerializer, ReviewDetailSerializer
)
from users.permissions import IsModerator, IsOwner


class AdvertisementViewSet(viewsets.ModelViewSet):
    """ViewSet для управления объявлениями"""

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    pagination_class = AdvertisementPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter

    def perform_create(self, serializer):
        """Автоматически устанавливать автора при создании"""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'retrieve':
            return AdvertisementDetailSerializer
        return AdvertisementSerializer

    def get_queryset(self):
        """Get queryset with prefetched reviews for performance"""
        return Advertisement.objects.prefetch_related('reviews')

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a specific advertisement"""
        ad = self.get_object()
        reviews = ad.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для управления отзывами"""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        """Автоматически устанавливать автора при создании"""
        serializer.save(author=self.request.user)


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    """
    Generic view for listing and creating reviews
    Following SB1 Market API requirements for permissions
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = AdvertisementPagination
    permission_classes = [IsAuthenticated, ~IsModerator]  # Non-moderators can create

    def perform_create(self, serializer):
        """Automatically assign the current user as author when creating"""
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """Get queryset with selected related advertisement for performance"""
        return Review.objects.select_related('ad')


class ReviewRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic view for retrieving, updating, and deleting reviews
    Following SB1 Market API requirements for permissions
    """

    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

    def get_queryset(self):
        """Get queryset with selected related advertisement for performance"""
        return Review.objects.select_related('ad')