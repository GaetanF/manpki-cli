import http.client
import urllib.parse
from jose import jws
import json
import sys

conn = http.client.HTTPConnection("127.0.0.1:8888")
if sys.argv[1] == "POST" or sys.argv[1] == "PUT":
   headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
   conn.request(sys.argv[1], sys.argv[2], sys.argv[3], headers)
else:
   conn.request(sys.argv[1], sys.argv[2])
r1 = conn.getresponse()
print("Status : ", r1.status, r1.reason)
if r1.status == 200:
   data = json.loads(r1.read().decode("utf8"))
   signed = jws.verify(data, 'secret', algorithms=['HS256'])
   print(json.dumps(json.loads(signed.decode("utf8")), sort_keys=True, indent=4, separators=(',', ': ')))
conn.close()
