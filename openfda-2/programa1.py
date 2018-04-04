import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")

conn.request("GET", "/drug/label.json?search=active_ingredient:%22acetylsalicylic+acid%22&limit=100&skip", None, headers)

inf = conn.getresponse()

print(inf.status, inf.reason)
prods_raw = inf.read().decode("utf-8")
conn.close()

prods = json.loads(prods_raw)

for prod in prods['results']:
    print ("id: ", prod['id'])
    if prod['openfda']:
        print("Fabricante: ",prod['openfda']['manufacturer_name'])
    else:
        print("Fabricante desconocido.")
