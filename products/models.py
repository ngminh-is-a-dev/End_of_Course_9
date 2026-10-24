from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    ROAST_CHOICES = [('light', 'Rang nhạt'), ('medium', 'Rang vừa'), ('dark', 'Rang đậm')]
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.PositiveIntegerField(help_text='Giá VND')
    image = models.ImageField(upload_to='products/', blank=True)
    roast_level = models.CharField(max_length=10, choices=ROAST_CHOICES, default='medium')
    origin = models.CharField(max_length=120, blank=True)
    stock = models.PositiveIntegerField(default=20)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'category'], name='product_active_category_idx'),
            models.Index(fields=['is_active', 'roast_level'], name='product_active_roast_idx'),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug])


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField(blank=True, max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['product', 'user'], name='one_review_per_user_product'),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name='product_review_rating_1_5',
            ),
        ]
        indexes = [models.Index(fields=['product', '-created_at'], name='prod_review_product_date_idx')]

    def __str__(self):
        return f'{self.product.name}: {self.rating}/5 by {self.user.get_username()}'

# Create your models here.
