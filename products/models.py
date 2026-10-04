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

# Create your models here.
