from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField('Tên sản phẩm', max_length=180)
    slug = models.SlugField('Đường dẫn', unique=True)
    description = models.TextField('Mô tả', blank=True)
    price = models.PositiveIntegerField('Giá (VNĐ)', help_text='Giá bán tính bằng VNĐ')
    image = models.ImageField(upload_to='products/', blank=True)
    stock = models.PositiveIntegerField('Tồn kho', default=0)
    is_active = models.BooleanField('Đang bán', default=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)

    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'category'], name='product_active_category_idx'),
        ]

    def __str__(self):
        return self.name
