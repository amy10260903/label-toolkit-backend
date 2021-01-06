from django.core.management.base import BaseCommand
from main.shazam import get_files_from_directory

class Command(BaseCommand):
    help = 'Shazam: Audio Fingerprinting Library'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--fingerprint', nargs=2,
                            help='Fingerprint files in a directory\n'
                                 'Usages: \n'
                                 '--fingerprint /path/to/directory extension\n')

    def handle(self, *args, **options):
        if options['fingerprint']:
            dir_name = options['fingerprint'][0]
            ext = options['fingerprint'][1]
            self.stdout.write(f"Retreive all .{ext} files in the {dir_name} directory\n"
                              "=== Start fingerprinting ===")
            # get_files_from_directory(dir_name, ext, 4)

