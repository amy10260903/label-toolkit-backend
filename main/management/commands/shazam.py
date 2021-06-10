from django.core.management.base import BaseCommand
from main.method import fingerprint_directory, recognize
from main.method.encoder import MyEncoder
import json
import os

class Command(BaseCommand):
    help = 'Shazam: Audio Fingerprinting Library'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--fingerprint', nargs=2,
                            help='Fingerprint files in a directory\n'
                                 'Usages: \n'
                                 '--fingerprint /path/to/directory extension\n')
        parser.add_argument('-c', '--category', nargs=1,
                            help='Category for files\n'
                                 'Usages: \n'
                                 '--category name\n')
        parser.add_argument('-r', '--recognize', nargs=2,
                            help='Recognize what is '
                                 'playing through the microphone or in a file.\n'
                                 'Usage: \n'
                                 '--recognize file path/to/file \n')

    def handle(self, *args, **options):
        if options['fingerprint']:
            dir_name = options['fingerprint'][0]
            ext = options['fingerprint'][1]
            self.stdout.write(f"Retreive all .{ext} files in the {dir_name} directory\n"
                              "=== Start fingerprinting ===")
            cat = options['category'][0] if options['category'] else 'default'
            fingerprint_directory(dir_name, ext, cat, 4)

        elif options['recognize']:
            # Recognize audio source
            songs = None
            source = options['recognize'][0]
            opt_arg = options['recognize'][1]
            cat = options['category'][0] if options['category'] else 'default'
            # params = {'thsld': 18, 'fan': 40}
            params = {'thsld': 24, 'fan': 10}

            if source == 'file':
                is_stream = False
                recordings = recognize(opt_arg, cat, params, is_stream)
                recordings = recordings._replace(
                                matched_result=[obj._asdict() for obj in recordings.matched_result],
                                event_name=os.path.basename(recordings.event_name).split('.')[0])
                with open(os.path.join('result', f'{recordings.event_name}.json'), 'w', encoding='utf-8') as outfile:
                    json.dump(recordings._asdict(), outfile,
                               cls=MyEncoder, indent=4)