import socket
import http.client
import json
import socketserver

IP = "192.168.1.8"
##IP = "212.128.254.149"
PORT = 8000
MAX_OPEN_REQUESTS = 5

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")

conn.request("GET", "/drug/label.json", None, headers)

inf = conn.getresponse()

print(inf.status, inf.reason)
prods_raw = inf.read().decode("utf-8")
conn.close()




def process_client(clientsocket):

    mens_solic = clientsocket.recv(1024)

    cont = """
      <!doctype html>
      <html>
      <body style='background-color: lightgreen'>
        <h1>WELCOME!</h1>
        <h2>Estas son las opciones que puede realizar:</h2>
        <p>
        Consultar ingrediente activo <input type="text" name="ingrediente"><br>
        <br>    
        Consultar las empresas <input type="text" name="empresas"><br>
        <br>
        Hacer una lista de farmacos <input type="text" name="listf"><br>
        <br>
        Hacer una lista de empresas <input type="text" name="liste"><br>
        <br>
        <input type="submit" value="Enviar">
      </body>
      </html>
    """


    l_inic = "HTTP/1.1 200 OK\n"
    cab = "Content-Type: text/html\n"
    cab += "Content-Length: {}\n".format(len(str.encode(cont)))


    mens_resp = str.encode(l_inic + cab + "\n" + cont)
    clientsocket.send(mens_resp)
    clientsocket.close()


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socketserver.TCPServer.allow_reuse_address = True

try:

    serversocket.bind((IP, PORT))

    serversocket.listen(MAX_OPEN_REQUESTS)

    while True:
        print("Esperando clientes en IP: {}, Puerto: {}".format(IP, PORT))
        (clientsocket, address) = serversocket.accept()


        print("  Peticion de cliente recibida. IP: {}".format(address))
        process_client(clientsocket)

except socket.error:
    print("Problemas usando el puerto {}".format(PORT))
    print("Lanzalo en otro puerto (y verifica la IP)")
