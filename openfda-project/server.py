import http.server
import http.client
import socketserver
import json

PORT = 8000

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    URL = "api.fda.gov"
    CLIENTE  = "/drug/label.json"

    def sol_openfda(self,limit=10):
        conn = http.client.HTTPSConnection(self.URL)
        conn.request("GET", self.CLIENTE + "?limit={}".format(limit))
        resp = conn.getresponse()
        info_raw = resp.read().decode("utf-8")
        info = json.loads(info_raw)
        results = info['results']
        return results

    def cabeceras(self):
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def primera_pagina(self):
        pagina = """
        <html>
            <body style="background-color:#cc99ff">
                <h1>Drug product labelling</h1>
                <br>
                <h2>Buscar medicamentos:</h2>
                <p>
                    <form method="get" action="searchDrug">
                        Nombre:<input type="text" name="drug"></input>
                        <br>
                        Limite:<input type="text" name="limit"></input>
                        <br>
                        <input type="submit" value="Buscar medicamentos"></input>
                    </form>
                    <br>
                </p>
                <h2>Buscar empresas:</h2>
                <p>
                    <form method="get" action="searchCompany">
                        Nombre:<input type="text" name="company"></input>
                        <br>
                        Limite:<input type="text" name="limit"></input>
                        <br>
                        <input type="submit" value="Buscar empresas"></input>
                    </form>
                    <br>
                </p>
                <h2>Lista de medicamentos:</h2>
                <p>
                    <form method="get" action="listDrugs">
                        Limite:<input type="text" name="limit"></input>
                        <br>
                        <input type="submit" value="Lista medicamentos"></input>
                    </form>
                    <br>
                </p>
                <h2>Lista de empresas:</h2>
                <p>
                    <form method="get" action="listCompanies">
                        Limite:<input type="text" name="limit"></input>
                        <br>
                        <input type="submit" value="Lista empresas"></input>
                    </form>
                    <br>
                </p>
                <h2>Lista de advertencias:</h2>
                <p>
                    <form method="get" action="listWarnings">
                        Limite:<input type="text" name="limit"></input>
                        <br>
                        <input type="submit" value="Lista advertencias"></input>
                    </form>
                </p>
            </body>
        </html>
        """
        return pagina

    def contenido_inicial(self, lista):
        contenido = ""
        for i in lista:
            contenido += "<li>{}</li>".format(i)
        inicio = """
        <html>
            <body style="background-color:#99ffd6">
                <ul style="list-style-type:square">{}</ul>
            </body>
        </html>
        """.format(contenido)
        return inicio

    def do_GET(self):
        lista_path = self.path.split("?")
        if len(lista_path)>1:
            params = lista_path[1]
        else:
            params = ""

        if self.path == "/":
            self.send_response(200)
            self.cabeceras()
            todo = self.primera_pagina()
            self.wfile.write(bytes(todo,"utf-8"))

        elif "searchDrug" in self.path:
            self.send_response(200)
            self.cabeceras()
            params = self.path.split("&")
            url_limit = params[1]
            if url_limit == "limit=":
                limit = 10
            else:
                limit = int(url_limit.split("=")[1])

            ingrediente = params[0].split("=")[1]
            lista_drugs = []
            conn = http.client.HTTPSConnection(self.URL)
            conn.request("GET", self.CLIENTE + "?limit={}".format(limit) + "&search=active_ingredient=" + ingrediente)
            resp = conn.getresponse()
            info_raw = resp.read().decode("utf-8")
            info = json.loads(info_raw)
            try:
                results = info['results']
                for i in results:
                    if 'generic_name' in i['openfda']:
                        lista_drugs.append(i['openfda']['generic_name'][0])
                    else:
                        lista_drugs.append("Medicamento desconocido")
            except KeyError:
                lista_drugs.append("Sin resultados")

            todo = self.contenido_inicial(lista_drugs)
            self.wfile.write(bytes(todo, "utf-8"))

        elif "searchCompany" in self.path:
            self.send_response(200)
            self.cabeceras()
            params = self.path.split("&")
            url_limit = params[1]
            if url_limit == "limit=":
                limit = 10
            else:
                limit = int(url_limit.split("=")[1])

            comp = params[0].split("=")[1]
            lista_comps = []
            conn = http.client.HTTPSConnection(self.URL)
            conn.request("GET", self.CLIENTE + "?limit={}".format(limit) + "&search=openfda.manufacturer_name=" + comp)
            resp = conn.getresponse()
            info_raw = resp.read().decode("utf-8")
            info = json.loads(info_raw)
            try:
                results = info['results']
                for i in results:
                    if 'manufacturer_name' in i['openfda']:
                        lista_comps.append(i['openfda']['manufacturer_name'][0])
                    else:
                        lista_comps.append("Empresa desconocida")
            except KeyError:
                lista_comps.append("Sin resultados")

            todo = self.contenido_inicial(lista_comps)
            self.wfile.write(bytes(todo, "utf-8"))

        elif "listDrugs" in self.path:
            self.send_response(200)
            self.cabeceras()
            params = self.path.split("?")
            url_limit = params[1]
            if url_limit == "limit=":
                limit = 10
            else:
                limit = int(url_limit.split("=")[1])

            lista_drugs = []
            given = self.sol_openfda(limit)
            for i in given:
                if 'generic_name' in i['openfda']:
                    lista_drugs.append(i['openfda']['generic_name'][0])
                else:
                    lista_drugs.append("Medicamento desconocido")

            todo = self.contenido_inicial(lista_drugs)
            self.wfile.write(bytes(todo, "utf-8"))

        elif "listCompanies" in self.path:
            self.send_response(200)
            self.cabeceras()
            params = self.path.split("?")
            url_limit = params[1]
            if url_limit == "limit=":
                limit = 10
            else:
                limit = int(url_limit.split("=")[1])

            lista_companies = []
            given = self.sol_openfda(limit)
            for i in given:
                if 'manufacturer_name' in i['openfda']:
                    lista_companies.append(i['openfda']['manufacturer_name'][0])
                else:
                    lista_companies.append("Empresa desconocida")

            todo = self.contenido_inicial(lista_companies)
            self.wfile.write(bytes(todo, "utf-8"))

        elif "listWarnings" in self.path:
            self.send_response(200)
            self.cabeceras()
            params = self.path.split("?")
            url_limit = params[1]
            if url_limit == "limit=":
                limit = 10
            else:
                limit = int(url_limit.split("=")[1])

            lista_warnings = []
            given = self.sol_openfda(limit)
            for i in given:
                if 'warnings' in i:
                    lista_warnings.append(i['warnings'])
                else:
                    lista_warnings.append("Adevertencias desconocidas")

            todo = self.contenido_inicial(lista_warnings)
            self.wfile.write(bytes(todo, "utf-8"))

        else:
            self.send_error(404)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("No encontrado ({})".format(self.path).encode("utf-8"))

        return

socketserver.TCPServer.allow_reuse_address = True
Handler = testHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print("Sirviendo en el puerto", PORT)
httpd.serve_forever()