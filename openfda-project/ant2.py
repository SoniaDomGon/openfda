import http.server
import http.client
import socketserver
import json

IP = "192.168.1.8"
PORT = 8000
socketserver.TCPServer.allow_reuse_address = True

R_SERVER = "api.fda.gov"
R_RESOURCE = "/drug/label.json"
headers = {'User-Agent': 'http-client'}

class TestHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def solicitud_openfda(self, limit, str_search=""):
        solicitud_str = "{}?limit={}".format(R_RESOURCE, limit)

        if str_search != "":
            solicitud_str += "&{}".format(str_search)

        conn = http.client.HTTPSConnection(R_SERVER)
        conn.request("GET", solicitud_str, None, headers)
        resp1 = conn.getresponse()
        print(resp1.status, resp1.reason)
        meds_json = resp1.read().decode("utf-8")
        conn.close()

        return json.loads(meds_json)

    def principal(self):
        pagina = """
        <!DOCTYPE html>
        <html>
        <body style='background-color: #cc99ff'>
        
        <form action = "/listDrugs" method="get">
            <input type="submit" value="Hacer lista farmacos">
            Limite: <input type="text" name="limit" value="">
        </form>
        <br>
        
        <form action = "/ListCompanies" method="get">
            <input type="submit" value="Hacer lista empresas">
        </form>
        <br>
        
        <form action = "/SearchDrug" method="get">
            <input type="submit" value="Buscar farmacos">
            Nombre: <input type="text" name="Principio activo" value="">
        </form>
        <br>
        
        <form action = "/SearchCompany" method="get">
            <input type="submit" value="Buscar empresas">
            Nombre: <input type="text" name="Nombre empresa" value="">
        </form>
        
        </body>
        </html>
        """

        return pagina


    def solicitud_listmeds(self, limit):

        meds = self.solicitud_openfda(limit)

        meta = meds['meta']
        total = meta['results']['total']
        limit = meta['results']['limit']
        print(limit, total)

        mensaje = """
        <!doctype html>
        <html>
        <body>
        <p>En el listado aparece el nombre, la marca, el fabricante, el ID y los propositos de cada medicamento.</p>
        <br>
        <ul style='list-style-type:square'>
        """

        for med in meds['results']:
            if med['openfda']:
                nombre = med['openfda']['substance_name'][0]
                marca = med['openfda']['brand_name'][0]
                fabricante = med['openfda']['manufacturer_name'][0]
            else:
                nombre = "Nombre desconocido"
                marca = "Marca desconocida"
                fabricante = "Fabricante desconocido"
            id = med['id']
            try:
                proposito = med['purpose']
            except KeyError:
                proposito = "Propositos desconocidos"

        mensaje += "<li>{}. {}. {}. {}. {}</li>\n".format(nombre, marca, fabricante, id, proposito)
        mensaje += """
        </ul>
        </body>
        </html>
        """

        return mensaje

    def solicitud_listcompanies(self, limit):
        meds = self.solicitud_openfda(limit)

        mensaje = """
        <!doctype html>
        <html>
        <body>
        <p>Los fabricantes son:</p>
        <br>
        <ul style='list-style.type: square'>
        """

        for med in meds['results']:
            if med['openfda']:
                fabricante = med['openfda']['manufacturer_name'][0]
            else:
                continue

        mensaje += "<li>{}</li>\n".format(fabricante)
        mensaje += """
        </ul>
        </body>
        </html>
        """

        return mensaje

    # GET. Este metodo se invoca automaticamente cada vez que hay una
    # peticion GET por HTTP. El recurso que nos solicitan se encuentra
    # en self.path
    def do_GET(self):

        print("Recurso pedido: {}".format(self.path))

        message = ""  # type: str

        # Dividir entre el endpoint y los parametros
        recurso_list = self.path.split("?")
        endpoint = recurso_list[0]
        if len(recurso_list) > 1:
            params = recurso_list[1]
        else:
            params = ""

        print("Endpoint: {}, params: {}".format(endpoint, params))

        # -- Valores por defecto de los parametros
        limit = 1

        # Obtener los parametros
        if params:
            print("Hay parametros")
            parse_limit = params.split("=")
            if parse_limit[0] == "limit":
                limit = int(parse_limit[1])
                print("Limit: {}".format(limit))
        else:
            print("SIN PARAMETROS")



        # -- Pagina INDICE
        if endpoint == "/":

            message = self.principal()

        # -- Listado de farmacos
        elif endpoint == "/listDrugs":

            print("Listado de farmacos solicitado: ListDrugs!")
            message = self.solicitud_listmeds(limit)

        elif endpoint == "/ListCompanies":

            print("Listado de empresas")
            message = self.solicitud_listcompanies(limit=10)

        # La primera linea del mensaje de respuesta es el
        # status. Indicamos que OK
        self.send_response(200)

        # En las siguientes lineas de la respuesta colocamos las
        # cabeceras necesarias para que el cliente entienda el
        # contenido que le enviamos (que sera HTML)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Enviar el mensaaje completo
        self.wfile.write(bytes(message, "utf8"))
        return




##Servidor!!!
Handler = TestHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("Serving at: port", PORT)

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Interrumpido por el usuario")

print("Servidor parado")