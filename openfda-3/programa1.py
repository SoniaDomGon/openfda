import socket
import http.client
import json

# Configuracion del servidor:
IP = "212.128.254.131"
PORT = 2222
MAX_OPEN_REQUESTS = 3

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/label.json?&limit=10", None, headers)
inf = conn.getresponse()
print(inf.status, inf.reason)
prods_raw = inf.read().decode("utf-8")
conn.close()

prods = json.loads(prods_raw)
def process_client(clientsocket):
    """Funcion para atender al cliente. Lee la peticion (pero la ignora)
       y le envia un mensaje de respuesta, con contenido HTML que se muestra en el navegador"""

    # Leemos el mensaje de solicitud
    # Pero no hacemos nada con el. Lo descartamos: con independencia de
    # lo que nos pida, siempre le devolvemos lo mismo
    mens_solic = client_socket.recv(1024)

    # Empezamos definiendo el contenido, porque necesitamos saber cuanto
    # ocupa para indicarlo en la cabecera
    # En este contenido pondremos el texto en HTML que queremos que se
    # visualice en el navegador cliente
    cont = """
      <!doctype html>
      <html>
      <body style='background-color: light-green'>
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

    # Creamos mensaje de respuesta. Tiene que ser en HTTP, porque el navegador no lo entiende
    # El mensaje HTTP debe contener:
    # Linea inicial
    # cabecera
    # Linea en blanco
    # Cuerpo

    # Indicamos primero que esta OK. Cualquier peticion es correcta para nosotros
    l_inic = "HTTP/1.1 200 OK\n"
    cab = "Content-Type: text/html\n"
    cab += "Content-Length: {}\n".format(len(str.encode(cont)))

    # Creamos el mensaje uniendo todas sus partes
    mens_resp = str.encode(l_inic + cab + "\n" + cont)
    client_socket.send(mens_resp)
    client_socket.close()

#Comienza a ejecutarse el servidor aqui

# Crear un socket para el servidor. Por el llegan las peticiones de los clientes.
# Sentido: Cliente --> Servidor

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Asociacion del socket a direccion IP y puertos del servidor
    server_socket.bind((IP, PORT))

    # Se trata de un socket de servidor, sobre el que escucharemos
    # Se permiten MAX_OPEN_REQUESTS solicitudes que se encolan antes, el resto se rechazan
    server_socket.listen(MAX_OPEN_REQUESTS)

    # Bucle principal del servidor. El servidor se queda escuchando
    # al "socket" hasta que llegue una conexion de un cliente
    # La atiende, para lo que recibe otro socket que le permite comunicarse con el
    while True:
        print("Esperando clientes en IP: {}, Puerto: {}".format(IP, PORT))
        (client_socket, address) = server_socket.accept()

        # Procesamos la peticion del cliente, pasandole el socket como argumento
        print("  Peticion de cliente recibida. IP: {}".format(address))
        process_client(client_socket)

except socket.error:
    print("Problemas usando el puerto {}".format(PORT))
    print("Lanzalo en otro puerto (y verifica la IP)")