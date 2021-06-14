from openpyxl import Workbook
import requests
import os
import time

from main.export.config import grouplist, mappinglist
from main.export.api import Userlog

headers = ['Filename', 'Labeling Time (mm:ss)']
base_dir = os.path.dirname(os.getcwd())
result_dir = os.path.join(base_dir, 'Research', 'LabelToolkit', 'usertest', 'result')

def group():
    api = Userlog()
    for group, users in grouplist.items():
        for username, request in users.items():
            dirname = os.path.join(result_dir, group, username, mappinglist[group])
            # print(dirname)
            if username == 'Jim':
                data = []
                for rid in request:
                    response = api.get(rid-4)
                    data.extend(response)
                print(data)
                exportToExcel(dirname, 'record', data)

def exportToExcel(dirname, filename, data):
    wb = Workbook()
    page = wb.active
    page.append(headers)
    for row in data:
        labeled_time = time.strftime('%M:%S', time.gmtime(row['labeled_time']))
        page.append([row['filename'], labeled_time])

    wb.save(os.path.join(dirname, f"{filename}.xlsx"))