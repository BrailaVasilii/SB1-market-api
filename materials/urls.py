from django.urls import path, include
from rest_framework.routers import DefaultRouter
from materials.views import (
    AdvertisementViewSet,
    ReviewListCreateAPIView,
    ReviewRetrieveUpdateDestroyAPIView
)

app_name = 'materials'

# Router for ViewSet (Advertisement)
router = DefaultRouter()
router.register(r'advertisements', AdvertisementViewSet, basename='advertisement')

urlpatterns = [
    # ViewSet URLs (automatically generated)
    path('', include(router.urls)),
    
    # Generic class URLs for Reviews
    path('reviews/', ReviewListCreateAPIView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewRetrieveUpdateDestroyAPIView.as_view(), name='review-detail'),
]