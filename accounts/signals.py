from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from promotions.models import Voucher
from .models import LoginHistory, UserProfile


@receiver(post_save, sender=get_user_model())
def create_welcome_voucher(sender, instance, created, **kwargs):
    if created:
        Voucher.objects.get_or_create(
            user=instance,
            code=f'FREESHIP-{instance.pk:05d}',
            defaults={'voucher_type': Voucher.FREE_SHIPPING},
        )


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(user_logged_in)
def record_successful_login(sender, request, user, **kwargs):
    remote_addr = request.META.get('REMOTE_ADDR') if request else None
    LoginHistory.objects.create(user=user, ip_address=remote_addr or None)
