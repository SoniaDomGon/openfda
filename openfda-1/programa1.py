import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/label.json?&limit=1", None, headers)
inf = conn.getresponse()
print(inf.status, inf.reason)
prods_raw = inf.read().decode("utf-8")
conn.close()

prods = json.loads(prods_raw)

prod = prods['results'][0]

print("id: ", prod['id'])
print("Próposito del producto:", prod['purpose'])
print("Fabricante del producto", prod['openfda']['manufacturer_name'])
