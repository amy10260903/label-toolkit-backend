from openpyxl import Workbook
import os
import time

from main.export.api import Userlog
from main.export.config import \
    exportlist, grouplist, mappinglist

headers = ['Filename', 'Labeling Time (mm:ss)']
base_dir = os.path.dirname(os.getcwd())
result_dir = os.path.join(base_dir, 'Research', 'LabelToolkit', 'usertest', 'result', 'user')

def exportUserRecord():
    api = Userlog()
    for group, users in grouplist.items():
        for username, request in users.items():
            if username not in exportlist:
                dirname = os.path.join(result_dir, group, username, mappinglist[group])

                data = []
                for rid in request:
                    response = api.get(rid)
                    data.extend(response)

                exportToExcel(dirname, 'record', data)
                print(f"export to {username} / {os.path.basename(dirname)}")
                exportlist.append(username)
    print(f"Exported: {exportlist}")

def exportToExcel(dirname, filename, data):
    wb = Workbook()
    page = wb.active
    page.append(headers)
    for row in data:
        if row['id'] == 5:
            row['labeled_time'] = row['labeled_time'] - 800
        if row['id'] in [51, 88, 99, 143, 193, 206, 207, 211, 214, 215, 216, 217, 218, 219, 220, 242]:
            continue
        if row['id'] in [11, 87, 117, 150, 186, 205, 239]:
            row['filename'] = 'audio_08'
            # continue
        labeled_time = time.strftime('%M:%S', time.gmtime(row['labeled_time']))
        page.append([row['filename'], labeled_time])

    wb.save(os.path.join(dirname, f"{filename}.xlsx"))