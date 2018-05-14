import socket
import http.client
import json
import flask

IP = "212.128.255.129"
PORT = 8000

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")

conn.request("GET", "/drug/label.json?search=active_ingredient:", name, None, headers)

inf = conn.getresponse()

print(inf.status, inf.reason)
prods_raw = inf.read().decode("utf-8")
conn.close()




def process_client(client_socket):

    mens_solic = client_socket.recv(1024)

    cont = """
      <!doctype html>
      <html>
      <body style='background-color: lightgreen'>
        <h1>Medicamentos:</h1>
      </body>
      </html>
    """
    for prod in prods['results']:
        if prod['openfda']:
            print("El medicamento es:", prod['openfda']['generic_name'][0])
            cont += (prod['openfda']['generic_name'][0])
            cont +="</br></body></html>"
        else:
            continue

    l_inic = "HTTP/1.1 200 OK\n"
    cab = "Content-Type: text/html\n"
    cab += "Content-Length: {}\n".format(len(str.encode(cont)))


    mens_resp = str.encode(l_inic + cab + "\n" + cont)
    client_socket.send(mens_resp)
    client_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:

    server_socket.bind((IP, PORT))

    server_socket.listen(MAX_OPEN_REQUESTS)

    while True:
        print("Esperando clientes en IP: {}, Puerto: {}".format(IP, PORT))
        (client_socket, address) = server_socket.accept()


        print("  Peticion de cliente recibida. IP: {}".format(address))
        process_client(client_socket)

except socket.error:
    print("Problemas usando el puerto {}".format(PORT))
    print("Lanzalo en otro puerto (y verifica la IP)")