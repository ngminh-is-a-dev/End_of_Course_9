from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from promotions.models import Voucher


@receiver(post_save, sender=get_user_model())
def create_welcome_voucher(sender, instance, created, **kwargs):
    if created:
        Voucher.objects.get_or_create(
            user=instance,
            code=f'FREESHIP-{instance.pk:05d}',
            defaults={'voucher_type': Voucher.FREE_SHIPPING},
        )
