from django.core.management.base import BaseCommand, CommandError
from planner.tasks import send_updated_participations

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        send_updated_participations()