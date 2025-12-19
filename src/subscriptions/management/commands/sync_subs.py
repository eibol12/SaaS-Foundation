from typing import Any
from django.core.management.base import BaseCommand
from subscriptions.models import Subscription

class Command(BaseCommand):
    help = "Syncs subscriptions permissions to their assigned groups."


    def handle(self, *args, **options):
        # Your logic for syncing subscriptions should go here
        self.stdout.write("Starting subscription synchronization...")

        qs = Subscription.objects.filter(active=True)

        for obj in qs:
            sub_perms = obj.permissions.all()
            for group in obj.groups.all():
                group.permissions.set(sub_perms)

        self.stdout.write(self.style.SUCCESS("Subscription synchronization complete."))
