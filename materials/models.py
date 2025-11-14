from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Advertisement(models.Model):
    """Advertisement model for marketplace platform"""

    title = models.CharField(max_length=200, verbose_name="Название")
    price = models.IntegerField(verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="advertisements",
        verbose_name="Автор объявления",
    )
    image = models.ImageField(
        upload_to="advertisements/images/",
        blank=True,
        null=True,
        verbose_name="Изображение",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} - {self.price} руб."


class Review(models.Model):
    """Review/Comment model for advertisements"""

    text = models.TextField(verbose_name="Текст отзыва")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор отзыва",
    )
    ad = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Объявление",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Отзыв от {self.author.email} на {self.ad.title}"
