from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from typing import Optional


class UserManager(BaseUserManager):
    """Manager for custom User model"""
    
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields) -> 'User':
        """Create and save a regular User with given email and password"""
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email: str, password: str) -> 'User':
        """Create and save a SuperUser with given email and password"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with email as username field"""
    
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True) 
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self) -> str:
        return self.email


class Payment(models.Model):
    """Payment model for course and lesson purchases"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
        ('stripe', 'Stripe'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')
    paid_course = models.ForeignKey(
        'materials.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Оплаченный курс'
    )
    paid_lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Оплаченный урок'
    )
    payment_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Способ оплаты'
    )
    
    # Stripe integration fields
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Stripe Product ID'
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Stripe Price ID'
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Stripe Session ID'
    )
    stripe_checkout_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Stripe Checkout URL'
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='Payment Status'
    )
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']
        
    def __str__(self) -> str:
        paid_item = self.paid_course.title if self.paid_course else self.paid_lesson.title
        return f"{self.user.email} - {paid_item} - {self.payment_amount}"
        
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError('Должен быть указан либо курс, либо урок для оплаты')
        if self.paid_course and self.paid_lesson:
            raise ValidationError('Нельзя указать одновременно курс и урок')


class Subscription(models.Model):
    """Subscription model for course updates"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        'materials.Course',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Курс'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']  # Prevent duplicate subscriptions
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        return f"{self.user.email} - {self.course.title}"
