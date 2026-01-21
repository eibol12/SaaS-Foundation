from typing import Any
from django.core.management.base import BaseCommand
from subscriptions import utils as subs_utils


class Command(BaseCommand):
    help = "Syncs subscriptions permissions to their assigned groups."


    def handle(self, *args, **options):
        # Your logic for syncing subscriptions should go here
        subs_utils.sync_subs_group_permissions()


