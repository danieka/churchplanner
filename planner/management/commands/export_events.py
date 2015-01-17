from django.core.management.base import BaseCommand, CommandError
from planner.export import export_events

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
    	export_events(args[0], args[1])