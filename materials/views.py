from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from materials.models import Advertisement, Review
from materials.serializers import (
    AdvertisementSerializer, AdvertisementDetailSerializer,
    ReviewSerializer, ReviewDetailSerializer
)
from materials.paginators import AdvertisementPagination, ReviewPagination
from users.permissions import IsModerator, IsOwner


class AdvertisementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Advertisement model providing full CRUD operations
    Following SB1 Market API requirements for permissions
    """

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    pagination_class = AdvertisementPagination

    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        Moderators: can view/edit, but not create/delete
        Authors: can view/edit/delete their own advertisements
        """
        if self.action == 'create':
            # Only authenticated non-moderators can create
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['destroy']:
            # Only authors can delete (moderators cannot)
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            # Moderators OR authors can view/edit
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'list':
            # All authenticated users can list
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Automatically assign the current user as author when creating"""
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


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    """
    Generic view for listing and creating reviews
    Following SB1 Market API requirements for permissions
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = ReviewPagination
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