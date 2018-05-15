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

    def solicitud_openfda(self, limit=1, str_search=""):

        solicitud_str = "{}?limit={}".format(R_RESOURCE, limit)

        if str_search != "":
            solicitud_str += "&{}".format(str_search)

        print("Recurso solicitado: {}".format(solicitud_str))

        conn = http.client.HTTPSConnection(R_SERVER)

        conn.request("GET", solicitud_str, None, headers)

        resp = conn.getresponse()

        print(resp.status, resp.reason)

        meds_json = resp.read().decode("utf-8")
        conn.close()

        return json.loads(meds_json)

    def primera_pagina(self):
        pagina = """
        <!DOCTYPE html>
        <html>
        <body style='background-color: #cc99ff'>
        
        <form action = "/SearchDrug" method="get">
            <input type="submit" value="Buscar farmacos">
            Nombre: <input type="text" name="ingrediente" value="">
        </form>
        <br>
        
        <form action = "/ListDrugs" method="get">
            <input type="submit" value="Hacer lista de farmacos">
            Limite: <input type="text" name="limit" value="1">
        </form>
        <br>
        
        <form action = "/SearchCompany" method="get">
            <input type="submit" value="Buscar empresas">
            Nombre: <input type="text" name="empresa" value="">
        </form>
        <br>
        
        <form action = "/ListCompanies" method="get">
            <input type="submit" value="Hacer lista de empresas">
            Limite: <input type="text" name="limit" value="1">
        </form>
        <br>

        </body>
        </html>
        """

        return pagina

    def solicitud_listmeds(self, limit):

        meds = self.solicitud_openfda(limit)

        meta = meds['meta']
        total = meta['results']['total']
        limit = meta['results']['limit']
        print("Medicamentos recibidos: {} / {}".format(limit, total))

        mensaje = """
        <!DOCTYPE html>
        <html>
        <body style='background-color: #ccfff5'>
        <p>Lista con nombre, marca, fabricante, ID y propositos de cada medicamento:</p>
        <ul style='list-style-type:square'>
        """

        for med in meds['results']:
            if med['openfda']:
                nombre = med['openfda']['substance_name'][0]
                marca = med['openfda']['brand_name'][0]
                fabricante = med['openfda']['manufacturer_name'][0]
            else:
                nombre = "Nombre desconocido"
                marca = "Marca desconocido"
                fabricante = "Fabricante desconocido"

            id = med['id']

            try:
                proposito = med['purpose'][0]
            except KeyError:
                proposito = "Proposito desconocido"

            mensaje += "<li>{}. {}. {}. {}. {}</li>\n".format(nombre, marca, fabricante, id, proposito)

        mensaje += """
        </ul>
        </body>
        </html>
        """

        return mensaje

    def solicitud_listempresas(self, limit):

        meds = self.solicitud_openfda(limit)

        meta = meds['meta']
        total = meta['results']['total']
        limit = meta['results']['limit']
        print("Empresas recibidas: {} / {}".format(limit, total))

        mensaje = """
        <!DOCTYPE html>
        <html>
        <body style='background-color: #ffb3d1'>
        <p>Los fabricantes de los medicamentos son:</p>
        <ul style='list-style-type:square'>
        """

        for med in meds['results']:
            if med['openfda']:
                fabricante = med['openfda']['manufacturer_name'][0]
            else:
                continue
            mensaje += "<li>{}</li>".format(fabricante)
        mensaje += """
        </ul>
        </body>
        </html>
        """

        return mensaje

    def buscar_medicamento(self):

        ingrediente = self.path.split("=")[1]

        solicitud = "{}?search=active_ingredient:{}".format(R_RESOURCE, ingrediente)

        conn = http.client.HTTPSConnection(R_SERVER)
        conn.request("GET", solicitud, None, headers)
        resp = conn.getresponse()
        print(resp.status, resp.reason)
        meds_raw = resp.read().decode("utf-8")
        conn.close()
        meds = json.loads(meds_raw)

        mensaje = """
        <!DOCTYPE html>
        <html>
        <body style='background-color: #b3ffb3'>
        <p>Los medicamentos con el nombre buscado son:</p>
        <ul style='list-style-type:square'>
        """

        for med in meds['results']:
            if med['openfda']:
                nombre = med['openfda']['substance_name'][0]
            else:
                nombre = "Nombre desconocido"
            mensaje += "<li>{}</li>".format(nombre)
        mensaje += """
        </ul>
        </body>
        </html>
        """

        return mensaje

    def buscar_empresa(self):

        empresa = self.path.split("=")[1]

        solicitud = "{}?search=openfda.manufacturer_name:{}".format(R_RESOURCE, empresa)

        conn = http.client.HTTPSConnection(R_SERVER)
        conn.request("GET", solicitud, None, headers)
        resp = conn.getresponse()
        print(resp.status, resp.reason)
        meds_raw = resp.read().decode("utf-8")
        conn.close()
        meds = json.loads(meds_raw)

        mensaje = """
        <!DOCTYPE html>
        <html>
        <body style='background-color: #ffeb99'>
        <p>Las empresas con el nombre buscado son:</p>
        <ul style='list-style-type:square'>
        """

        for med in meds['results']:
            if med['openfda']:
                empresa = med['openfda']['manufacturer_name'][0]
            else:
                empresa = "Empresa desconocida"
            mensaje += "<li>{}</li>".format(empresa)
        mensaje += """
        </ul>
        </body>
        </html>
        """
        return mensaje

    def do_GET(self):

        print("Recurso: {}".format(self.path))

        mensaje = ""
        recurso = self.path.split("?")
        fin = recurso[0]
        if len(recurso) > 1:
            parametro = recurso[1]
        else:
            parametro = ""

        print("Endpoint: {}, params: {}".format(fin, parametro))

        limit = 1

        if parametro:
            print("Hay parametros")
            parse_limit = parametro.split("=")
            if parse_limit[0] == "limit":
                limit = int(parse_limit[1])
                print("Limit: {}".format(limit))
        else:
            print("SIN PARAMETROS")

        if fin == "/":
            mensaje = self.primera_pagina()

        elif fin == "/ListDrugs":
            mensaje = self.solicitud_listmeds(limit)

        elif fin == "/ListCompanies":
            mensaje = self.solicitud_listempresas(limit)

        elif fin == "/SearchDrug":
            mensaje = self.buscar_medicamento()

        elif fin == "/SearchCompany":
            mensaje = self.buscar_empresa()

        self.send_response(200)

        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes(mensaje, "utf8"))
        return

Handler = TestHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("Serving at: port", PORT)

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Interrumpido por el usuario")

print("Servidor parado")