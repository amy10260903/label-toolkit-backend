import requests
import json

# BaseURL = "https://filmmusic.avmapping.co/"
BaseURL = "http://127.0.0.1:8000/"

print("=== API Testing ===")

# api = "main/fingerprint"
# with open(r"test/mrt-music-cut.m4a", 'rb') as f:
# 	files = {
# 		'file': f
# 	}
#
# 	data = {
# 		'category': 'origin'
# 	}
#
# 	print(api)
# 	r = requests.post(f"{BaseURL}api/{api}/", data=data, files=files)
#
# 	with open(r"log.txt", 'w') as flog:
# 		flog.write(r.text)
#
# 	print(f"{r.text}\n")
# 	assert r.status_code == 200 , r.text

api = "main/option"
print(api)
r = requests.get(f"{BaseURL}api/{api}/")
print(f"{r.text}\n")
assert r.status_code == 200 , r.text