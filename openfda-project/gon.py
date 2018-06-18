import http.client
import http.server
import socketserver
import json

PORT = 8000
COMPANY_SEARCH = '&search=openfda.manufacturer_name='
DRUG_SEARCH = '&search=active_ingredient='


class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    CLIENT = '/drug/label.json'
    URL = 'api.fda.gov'

    # <input type='text' name='limit'><br>

    def main_page(self):
        HTML = """
            <html>
                <head>
                    <title>OpenFDA</title>
                </head>
                <body align=center>
                    <h1>Bienvenido a OpenFDA </h1>
                    <h2><u>Buscar medicamento</u></h2>
                    <form method="get" action="searchDrug">
                        <br>Busqueda:
                        <input type = "text" name="drug"></input><br>
                        <br>Limit:
                        <input type='text' name='limit'>
                        <br><p><input type = "submit">
                        </input>
                    </form>
                    <h2><u>Buscar Fabricante</u></h2>
                    <form method="get" action="searchCompany">
                        <br>Busqueda
                        <input type = "text" name="company"></input><br>
                        <br>Limit:
                        <input type='text' name='limit'>
                        <br><p><input type = "submit" >
                        </input>
                    </form>
                    <h2><u>Listado de Medicamentos</u></h2>
                    <form method="get" action="listDrugs">
                        <br>Limit:
                        <input type='text' name='limit'>
                        <br><p><input type = "submit">
                        </input>
                    </form>

                    <h2><u>Listado de Fabricantes</u></h2>
                    <form method="get" action="listCompanies">
                        <br>Limit:
                        <input type='text' name='limit'>
                        <br><p><input type = "submit">
                        </input>
                    </form>
                    <h2><u>Listado de Advertencias</u></h2>
                    <form method="get" action="listWarnings">
                        <br>Limit:
                        <input type='text' name='limit'><br>
                        <br><p><input type = "submit">
                        </input>
                    </form>

                </body>
            </html>
                """

        return HTML

    def intro_content(self, LIST):
        content = ''
        for item in LIST:
            content += '<li>{}</li>'.format(item)
        HTML = '''<html><head><title></title></head>
        <body><ul>
        {}
        </ul></body>
        </html>'''.format(content)
        return HTML

    def openfda_conection(self, LIMIT=10):
        conn = http.client.HTTPSConnection(self.URL)
        conn.request('GET', self.CLIENT + '?limit={}'.format(LIMIT))
        r1 = conn.getresponse()
        response = r1.read().decode("utf-8")
        conn.close()
        json_info = json.loads(response)
        result = json_info['results']
        return result

    def send_headers(self):
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):

        path_list = self.path.split('?')
        if len(path_list) > 1:
            parametros = path_list[1]
            if len(parametros) == 0:
                LIMIT = 10
        else:
            parametros = ''
            LIMIT = 10

        if self.path == '/':
            self.send_response(200)
            self.send_headers()
            page = self.main_page()
            self.wfile.write(bytes(page, "utf8"))

        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_headers()

            parameters = self.path.split('?')[1]
            if parameters == 'limit=':
                LIMIT = 10
            else:
                LIMIT = parameters.split('=')[1]
                LIMIT = int(LIMIT)

            companies_list = []
            JSON = self.openfda_conection(LIMIT)
            for item in JSON:
                if 'manufacturer_name' in item['openfda']:
                    companies_list.append(item['openfda']['manufacturer_name'][0])
                else:
                    companies_list.append('Desconocido')

            page = self.intro_content(companies_list)
            self.wfile.write(bytes(page, "utf8"))

        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_headers()

            parameters = self.path.split('?')[1]
            if parameters == 'limit=':
                LIMIT = 10
            else:
                LIMIT = parameters.split('=')[1]
                LIMIT = int(LIMIT)

            drug_list = []
            JSON = self.openfda_conection(LIMIT)
            for item in JSON:
                if 'generic_name' in item['openfda']:
                    drug_list.append(item['openfda']['generic_name'][0])
                else:
                    drug_list.append('Desconocido')

            page = self.intro_content(drug_list)
            self.wfile.write(bytes(page, "utf8"))

        elif 'listWarnings' in self.path:
            self.send_response(200)
            self.send_headers()

            parameters = self.path.split('?')[1]
            if parameters == 'limit=':
                LIMIT = 10
            else:
                LIMIT = parameters.split('=')[1]
                LIMIT = int(LIMIT)

            warnings_list = []
            JSON = self.openfda_conection(LIMIT)
            print(JSON[0]['warnings'])
            for item in JSON:
                if 'warnings' in item:
                    warnings_list.append(item['warnings'][0])
                else:
                    warnings_list.append('Desconocido')
            page = self.intro_content(warnings_list)
            self.wfile.write(bytes(page, "utf8"))

        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_headers()

            parameters = self.path.split('&')
            limite = parameters[1]
            if limite == 'limit=':
                LIMIT = 10
            else:
                LIMIT = limite.split('=')[1]
                LIMIT = int(LIMIT)

            SEARCH = parameters[0].split('=')[1]
            drug_list = []
            conn = http.client.HTTPSConnection(self.URL)
            conn.request("GET", self.CLIENT + "?limit={}".format(LIMIT) + DRUG_SEARCH + SEARCH)
            r1 = conn.getresponse()
            response = r1.read()
            json_info = response.decode("utf8")
            results = json.loads(json_info)
            try:
                drugs = results['results']
                for item in drugs:
                    if 'generic_name' in item['openfda']:
                        drug_list.append(item['openfda']['generic_name'][0])
                    else:
                        drug_list.append('Desconocido')
            except KeyError:
                drug_list.append('No se encontraron resultados')

            page = self.intro_content(drug_list)
            self.wfile.write(bytes(page, "utf8"))

        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_headers()

            parameters = self.path.split('&')
            limite = parameters[1]
            if limite == 'limit=':
                LIMIT = 10
            else:
                LIMIT = limite.split('=')[1]
                LIMIT = int(LIMIT)

            SEARCH = parameters[0].split('=')[1]
            comp_list = []
            conn = http.client.HTTPSConnection(self.URL)
            conn.request('GET', self.CLIENT + '?limit={}'.format(LIMIT) + COMPANY_SEARCH + SEARCH)
            r1 = conn.getresponse()
            response = r1.read()
            data = response.decode('utf8')
            info = json.loads(data)
            try:
                json_info = info['results']
                for item in json_info:
                    if 'manufacturer_name' in item['openfda']:
                        comp_list.append(item['openfda']['manufacturer_name'][0])
                    else:
                        comp_list.append('Desconocido')
            except KeyError:
                comp_list.append('No se encontraro resultados')
            page = self.intro_content(comp_list)
            self.wfile.write(bytes(page, 'utf8'))

        elif 'secret' in self.path:
            self.send_response(401)

            self.send_header('WWW-Authenticate', 'Basic realm="Secure Area"')
            self.end_headers()

        elif 'redirect' in self.path:
            self.send_response(301)
            self.send_header('Location', 'http://127.0.0.1:8000')
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        else:
            self.send_error(404)

            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()

            self.wfile.write("Page not found ({})".format(self.path).encode('utf-8'))
        return


socketserver.TCPServer.allow_reuse_address = True

Handler = testHTTPRequestHandler
httpd = socketserver.TCPServer(('', PORT), Handler)
print('serving at port', PORT)
httpd.serve_forever()