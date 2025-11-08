from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import re
from urllib.parse import urlparse


def validate_youtube_url(value):
    """
    Validator function to check if URL is from YouTube domain only.
    Allows only youtube.com and youtu.be domains.
    """
    if not value:
        return
    
    # First validate that it's a proper URL
    url_validator = URLValidator()
    try:
        url_validator(value)
    except ValidationError:
        raise ValidationError('Введите корректный URL.')
    
    # Parse the URL to get the domain
    parsed_url = urlparse(value)
    domain = parsed_url.netloc.lower()
    
    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # List of allowed domains
    allowed_domains = ['youtube.com', 'youtu.be']
    
    if domain not in allowed_domains:
        raise ValidationError(
            'Разрешены только ссылки на YouTube (youtube.com или youtu.be). '
            'Ссылки на сторонние ресурсы запрещены.'
        )


class YouTubeURLValidator:
    """
    Class-based validator for YouTube URLs.
    Can be used in serializer Meta validators.
    """
    
    def __init__(self, field='video_url'):
        self.field = field
    
    def __call__(self, attrs):
        """
        Validate that video_url field contains only YouTube URLs.
        """
        video_url = attrs.get(self.field)
        if video_url:
            validate_youtube_url(video_url)
        return attrs