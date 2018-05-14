import socket
import http.client
import json
import socketserver


IP = "212.128.254.149"
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
        <h2>Elija una de las siguientes opciones:</h2>
        <form>
        <input type="radio" name="principal" value="ingrediente activo"> Consultar ingrediente activo<br>
        <input type="radio" name="principal" value="consultar empresas"> Consultar las empresas<br>
        <input type="radio" name="principal" value="lista de farmacos"> Hacer una lista de farmacos<br>
        <input type="radio" name="principal" value="lista de empresas"> Hacer una lista de empresas<br>
        <br>
        <input type="submit" value="enviar"
        </form>
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