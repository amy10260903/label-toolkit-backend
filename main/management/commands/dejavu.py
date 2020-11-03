from django.core.management.base import BaseCommand, CommandError
import os, sys

from main.dejavu import fingerprint_directory

class Command(BaseCommand):
    help = 'Dejavu: Audio Fingerprinting library'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--config', nargs='?',
                            help='Path to configuration file\n'
                                 'Usages: \n'
                                 '--config /path/to/config-file\n')
        parser.add_argument('-f', '--fingerprint', nargs='*',
                            help='Fingerprint files in a directory\n'
                                 'Usages: \n'
                                 '--fingerprint /path/to/directory extension\n'
                                 '--fingerprint /path/to/directory')
        parser.add_argument('-r', '--recognize', nargs=2,
                            help='Recognize what is '
                                 'playing through the microphone or in a file.\n'
                                 'Usage: \n'
                                 '--recognize mic number_of_seconds \n'
                                 '--recognize file path/to/file \n')

    def handle(self, *args, **options):
        fingerprint = options['fingerprint']
        if fingerprint:
            if len(fingerprint) == 2:
                directory = fingerprint[0]
                extension = fingerprint[1]
                self.stdout.write(f"Fingerprinting all .{extension} files in the {directory} directory")
                fingerprint_directory(directory, ["." + extension], 4)

            elif len(fingerprint) == 1:
                filepath = fingerprint[0]
                if os.path.isdir(filepath):
                    self.stdout.write("Please specify an extension if you'd like to fingerprint a directory!")
                    sys.exit(1)
                # djv.fingerprint_file(filepath)