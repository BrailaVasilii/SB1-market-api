from django.contrib import admin

from .models import Advertisement, Review


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "price", "author", "created_at"]
    list_filter = ["created_at", "author"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "text", "author", "ad", "created_at"]
    list_filter = ["created_at", "author"]
    search_fields = ["text"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
