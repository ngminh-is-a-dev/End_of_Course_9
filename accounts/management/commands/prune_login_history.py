import calendar

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import LoginHistory


def retention_cutoff(now=None):
    now = now or timezone.now()
    previous_year = now.year - 1
    last_day = calendar.monthrange(previous_year, now.month)[1]
    return now.replace(year=previous_year, day=min(now.day, last_day))


class Command(BaseCommand):
    help = 'Delete login history records older than 12 months.'

    def handle(self, *args, **options):
        cutoff = retention_cutoff()
        deleted_count, _ = LoginHistory.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(f'Deleted {deleted_count} login history record(s).')
