import http.server
import http.client
import json
import socketserver

PORT = 8000


class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # La clase tiene 4 metodos
    # El metodo do_Get es el unico q se ejecuta automaticamente cuando alguien se conecte a mi practica y pida un get + recurso.
    # Los otros 3 metodos son auxiliares
    # GET
    URL = "api.fda.gov"
    LABEL = "/drug/label.json"
    DRUG = '&search=active_ingredient:'
    COMPANY = '&search=openfda.manufacturer_name:'

    def main_app(self):
        html = """
            <html>
                <head>
                    <title>OpenFDA App</title>
                </head>
                <body align=center style='background-color: yellow'>
                    <h1>Bienvenido a la pagina principal de la App </h1>
                    <br>
                    <form method="get" action="listDrugs">
                        <input type = "submit" value="Lista Medicamentos">
                        </input>
                    </form>
                    <br>
                    <br>
                    <form method="get" action="searchDrug">
                        <input type = "submit" value="Buscar Medicamentos">
                        <input type = "text" name="drug"></input>
                        </input>
                    </form>
                    <br>
                    <br>
                    <form method="get" action="listCompanies">
                        <input type = "submit" value="Lista Empresas">
                        </input>
                    </form>
                    <br>
                    <br>
                    <form method="get" action="searchCompany">
                        <input type = "submit" value="Buscador Empresas">
                        <input type = "text" name="company"></input>
                        </input>
                    </form>
                    <br>
                    <br>
                    <form method="get" action="listWarnings">
                        <input type = "submit" value="Lista Advertencias">
                        </input>
                    </form>
                    <br>
                    <br>
                    <p> Practica hecha por Javier Alvarez Benito </p>
                    <p> Ingenieria Biomedica - URJC </p>
                </body>
            </html>
                """
        return html

    def web(self, lista):
        lista_html = """
                                        <html>
                                            <head>
                                                <title>OpenFDA App</title>
                                            </head>
                                            <body style='background-color: yellow'>
                                                <h1> La informacion buscada es: </h1>
                                                <br>
                                                <ul>
                                    """
        for item in lista:
            lista_html += "<li>" + item + "</li>"

        lista_html += """
                                                </ul>
                                            </body>
                                        </html>
                                    """
        return lista_html

    def dame_resultados(self, limit=10):
        conexion = http.client.HTTPSConnection(self.URL)
        conexion.request("GET", self.LABEL + "?limit=" + str(limit))
        print (self.LABEL + "?limit=" + str(limit))
        r1 = conexion.getresponse()
        label = r1.read().decode("utf8")
        info = json.loads(label)
        resultados = info['results']
        return resultados

    def do_GET(self):
        # Dividir entre el endpoint y los parametros
        lista_recurso = self.path.split("?")
        if len(lista_recurso) > 1:  # Significa que despues de la ? te han pasado algun parametro de un recurso
            parametros = lista_recurso[1]
        else:
            parametros = ""

        limit = 1  # Limite por defecto

        # Obtener los parametros
        if parametros:
            print("HAY PARAMETROS")
            limite_parametro = parametros.split("=")
            if limite_parametro[0] == "limit":  # Te detecta el parametro limit
                limit = int(limite_parametro[1])
                print("Limit: {}".format(limit))
        else:
            print("SIN PARAMETROS")

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.main_app()
            self.wfile.write(bytes(html, "utf8"))

        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_medicamentos = []
            resultados = self.dame_resultados(limit)
            for resultado in resultados:
                if ('generic_name' in resultado['openfda']):
                    lista_medicamentos.append(resultado['openfda']['generic_name'][0])
                else:
                    lista_medicamentos.append('Se desconoce el nombre del medicamento')
            resultado_html = self.web(lista_medicamentos)
            self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_empresas = []
            resultados = self.dame_resultados(limit)
            for resultado in resultados:
                if ('manufacturer_name' in resultado['openfda']):
                    lista_empresas.append(resultado['openfda']['manufacturer_name'][0])
                else:
                    lista_empresas.append('Se desconoce el nombre de la empresa')
            resultado_html = self.web(lista_empresas)
            self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'listWarnings' in self.path:
            # listWarnings te devuelve toodo los warnings dee los medicamentos.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_advertencias = []
            resultados = self.dame_resultados(limit)
            for resultado in resultados:
                if ('warnings' in resultado):
                    lista_advertencias.append(resultado['warnings'][0])
                else:
                    lista_advertencias.append('Se desconoce las advertencias')
            resultado_html = self.web(lista_advertencias)
            self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Por defecto 10 en este caso, no 1
            limit = 10
            medicamento = self.path.split('=')[1]

            lista_medicamento = []
            conexion = http.client.HTTPSConnection(self.URL)
            conexion.request("GET",self.LABEL + "?limit=" + str(limit) + self.DRUG + medicamento)
            r1 = conexion.getresponse()
            label1 = r1.read().decode("utf8")
            info1 = json.loads(label1)
            buscador_medicamento = info1['results']
            for resultado in buscador_medicamento:
                if ('generic_name' in resultado['openfda']):
                    lista_medicamento.append(resultado['openfda']['generic_name'][0])
                else:
                    lista_medicamento.append('Se desconoce el nombre del medicamento')
            resultado_html = self.web(lista_medicamento)
            self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Por defecto 10 en este caso, no 1
            limit = 10
            empresa = self.path.split('=')[1]
            lista_empresa = []
            conexion = http.client.HTTPSConnection(self.URL)
            conexion.request("GET", self.LABEL + "?limit=" + str(limit) + self.COMPANY + empresa)
            r1 = conexion.getresponse()
            label2 = r1.read().decode("utf8")
            info2 = json.loads(label2)
            buscador_empresa = info2['results']
            for event in buscador_empresa:
                lista_empresa.append(event['openfda']['manufacturer_name'][0])
            resultado_html = self.web(lista_empresa)
            self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'redirect' in self.path:  # Te dirige hacia la pagina principal
            self.send_response(301)
            self.send_header('Location', 'http://localhost:' + str(PORT))
            self.end_headers()
        elif 'secret' in self.path: #Te pide datos para acceder a sitios privados
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')  # Le envias esa cabecera.
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("No encuentro ese recurso '{}'.".format(self.path).encode())
        return


socketserver.TCPServer.allow_reuse_address = True
# Handler = http.server.SimpleHTTPRequestHandler
Handler = testHTTPRequestHandler
# es una instancia de una clase q se encarga de responde a las peticciones http que puede venir de dos sitios, un ordenador o el test de la practica

httpd = socketserver.TCPServer(("192.168.1.8", PORT), Handler)
print("Sirviendo en el puerto:", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("El usuario ha interrumpido el servidor en el puerto:", PORT)
    print("Reanudelo de nuevo")

print("Servidor parado")