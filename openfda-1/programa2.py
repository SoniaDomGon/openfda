import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/label.json?&limit=10", None, headers)
inf = conn.getresponse()
print(inf.status, inf.reason)
prods_raw = inf.read().decode("utf-8")
conn.close()

prods = json.loads(prods_raw)

obj = 0
while obj < 10:
    prod = prods['results'][obj]
    print("id: ", prod['id'])
    obj +=1