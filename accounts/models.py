from django.conf import settings
from django.db import models


class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Số điện thoại', max_length=20, blank=True)
    address = models.TextField('Địa chỉ', blank=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Cập nhật lần cuối', auto_now=True)

    class Meta:
        verbose_name = 'Hồ sơ'
        verbose_name_plural = 'Hồ sơ'

    def __str__(self):
        return f'Hồ sơ của {self.user.username}'
