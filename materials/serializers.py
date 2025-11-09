from rest_framework import serializers
from materials.models import Advertisement, Review


class ReviewForAdvertisementSerializer(serializers.ModelSerializer):
    """Simplified serializer for reviews when displayed within advertisement"""
    
    author_email = serializers.CharField(source='author.email', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'text', 'author_email', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Full serializer for Review model"""
    
    author_email = serializers.CharField(source='author.email', read_only=True)
    ad_title = serializers.CharField(source='ad.title', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'text', 'author', 'author_email', 
            'ad', 'ad_title', 'created_at'
        ]
        read_only_fields = ['id', 'author', 'created_at']


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer for Advertisement model with nested reviews"""
    
    reviews = ReviewForAdvertisementSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField()
    author_email = serializers.CharField(source='author.email', read_only=True)
    
    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'price', 'description', 'author', 'author_email',
            'image', 'reviews_count', 'reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
        
    def get_reviews_count(self, obj: Advertisement) -> int:
        """Get count of reviews for the advertisement"""
        return obj.reviews.count()


class AdvertisementDetailSerializer(AdvertisementSerializer):
    """Detailed serializer for Advertisement with full review info"""
    
    class Meta(AdvertisementSerializer.Meta):
        pass


class ReviewDetailSerializer(ReviewSerializer):
    """Detailed serializer for Review with advertisement info"""
    
    class Meta(ReviewSerializer.Meta):
        fields = ReviewSerializer.Meta.fields