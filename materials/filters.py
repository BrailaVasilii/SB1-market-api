from django_filters import rest_framework as filters
from .models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """
    Фильтр для объявлений
    SB1 Requirement: поиск по title
    """

    title = filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Поиск по названию'
    )

    class Meta:
        model = Advertisement
        fields = ['title']