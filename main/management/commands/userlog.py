from django.core.management.base import BaseCommand
from main.export import exportUserRecord

class Command(BaseCommand):
    help = 'User: Load userlogs'

    def handle(self, *args, **options):
        print('=== User Record ===')
        exportUserRecord()
        print('=== Done ===')

