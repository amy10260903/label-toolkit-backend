import requests
from main.export.config import BaseURL
import json

class Userlog():
    url = "main/user"

    def get(self, req_id):
        params = {'id': req_id}
        r = requests.get(f"{BaseURL}api/{self.url}/", params=params)
        assert r.status_code == 200, r.text
        return json.loads(r.text)