from django.core.management.base import BaseCommand
import requests
import os
import json

from main.export import group
class Command(BaseCommand):
    help = 'User: Load userlogs'

    def handle(self, *args, **options):
        group()
        # if options['request']:
        #     id = options['request'][0]
        #     if len(options['request']) == 2:
        #         BaseURL = options['request'][1]
        #     elif len(options['request']) == 1:
        #         BaseURL = 'localhost:8000'
        #     api = "main/user"
        #     params = {'id': id}
        #     r = requests.get(f"http://{BaseURL}/api/{api}", params=params)
        #     print(f"{r.text}\n")
        #     assert r.status_code == 200, r.text
        #
        #     if options['save']:
        #         if len(options['save']) == 2:
        #             filename = options['save'][0]
        #             dirname = options['save'][1]
        #         elif len(options['save']) == 1:
        #             base_dir = os.path.dirname(os.getcwd())
        #             dirname = os.path.join(base_dir, 'Research', 'LabelToolkit', 'usertest', 'result')
        #             filename = options['save'][0]
        #
        #         exportToExcel(dirname, filename, json.loads(r.text))

