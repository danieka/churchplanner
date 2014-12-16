from django.core.management.base import BaseCommand, CommandError
from planner.tasks import *

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
    	send_email_participation()