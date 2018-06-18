#Importamos los módulos necesarios para poder ejecutar el servidor
import http.server
import http.client
import json
import socketserver

#Indicamos el puerto
PORT=8000

#-----------------------------------------------------------------------------------------------------------------------

#Utilizamos la misma clase que en la práctica anterior, una clase derivada de BaseHTTPRequestHandler
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    #urls necsarias en posteriores procesos
    url_openfda = "api.fda.gov"
    client_openfda = "/drug/label.json"
    drug_openfda = '&search=active_ingredient:'
    company_openfda = '&search=openfda.manufacturer_name:'

    #Creamos una función en la que se controla el contenido en un documento html de la página de inicio, que es la página principal
    def start_page(self):
        main_page ="""<html>
                <head>
                    <title>Medicamentos OpenFda</title>
                </head>
                <body align=center style='background-color: lightblue'>
                    <h1>OpenFda</h1>
                    <br>
                    <p>1-.)Lista de medicamentos</p>
                    <form method="get" action="listDrugs"><input type = "submit" value="Drugs list"></input></form>
                    <br>
                    <br>
                    <p>2-.)Buscar medicamentos</p>
                    <form method="get" action="searchDrug"><input type = "submit" value="Search drug"><input type = "text" name="drug"></input></input></form>
                    <br>
                    <br>
                    <p>3-.)Lista de empresas</p>
                    <form method="get" action="listCompanies"><input type = "submit" value="Companies list"></input></form>
                    <br>
                    <br>
                    <p>4-.)Buscar empresas</p>
                    <form method="get" action="searchCompany"><input type = "submit" value="Search companies"><input type = "text" name="company"></input></input></form>
                    <br>
                    <br>
                    <p>5-.)Lista de advertencias</p>
                    <form method="get" action="listWarnings"><input type = "submit" value="Lista Advertencias"></input></form>
                    <br>
                    <br>
                    <img src="http://www.openbiomedical.org/wordpress/wp-content/uploads/2015/09/openfda_logo.jpg?x10565.png"width=30% height=20% clear=left>
                </body>
            </html>
                """
        return main_page

    #En esta función se regula lo relativo a la conexión , que utilizaremos para las que no son formularios
    def conexion (self, limit=10):
        conn = http.client.HTTPSConnection(self.url_openfda) #lo que nuestra página como cliente sugiere
        conn.request("GET", self.client_openfda + "?limit="+str(limit)) #la petición del cliente de nuestra página
        print (self.client_openfda + "?limit="+str(limit))
        r1 = conn.getresponse()
        data_raw = r1.read().decode("utf8")
        informacion = json.loads(data_raw)
        resultados = informacion['results']
        return resultados

    #En esta función se define el contenido que aparecerá en la página al rellenar el formulario
    def content (self, list):
        contenido = """ <html>
                        <head><title>Resultados de su búsqueda</title></head>
                                    <body>
                                        <ul>"""
        for a in list:
            contenido += "<li>" + a + "</li>"
        contenido += """
                                     </ul>
                                    </body>
                                </html>"""
        return contenido


    def do_GET(self):
        recurso_list = self.path.split("?")
        if len(recurso_list) > 1:
            parametros = recurso_list[1]
        else:
            parametros = ""
        limit = 10

        # Obtener los parametros
        if parametros:
            parse_limit = parametros.split("=")
            if parse_limit[0] == "limit":
                limit = int(parse_limit[1])
                print("Limit: {}".format(limit))
        else:
            print("SIN PARAMETROS")


# Ahora comienzan las condiciones según el contenido que pone el cliente en la url, en utf8

        #Condición en la que se evalúa lo que debe devolver el servidor si se añade -> /
        if self.path=='/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html') #cabeceras necesarias para que el cliente entienda el contenido que le enviamos
            self.end_headers()
            html=self.start_page()  #Llamamos a la función en la que tenemos el contenido de la página principal y la almacenamos en una variable
            self.wfile.write(bytes(html, "utf8"))  #"Escribimos" el contenido que corresponde a la página principal

        #Condición en la que se devuelve una lista de medicamentos de la openfda al añadir en la url-> listDrugs
        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html') #cabeceras necesarias para que el cliente entienda el contenido que le enviamos
            self.end_headers()
            medicamentos = [] #lista vacía en la que se iran añadiendo los medicamentos
            resultados = self.conexion(limit) #llamamos a la función que nos devuelve los resultados de la búsqueda en openfda para poder añadir a la lista lo que buscamos
            for resultado in resultados:
                if ('generic_name' in resultado['openfda']):
                    medicamentos.append (resultado['openfda']['generic_name'][0]) #buscamos dentro de los resultados con las propiedades de los diccionarios
                else:
                    medicamentos.append('Medicamento no encontrado') #Se valora el caso en el que no aparece un medicamento
            resultado_html = self.content (medicamentos) #llamamos a la función en la que se encuentra el contenido e introducimos como argumento los medicamentos para que se añadan al contenido
            self.wfile.write(bytes(resultado_html, "utf8")) #escribimos el contenido en la página

        #Condición en la que se devuelve una lista de empresas de la openfda al añadir a la url-> listCompanies
        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')  #cabeceras necesarias para que el cliente entienda el contenido que le enviamos
            self.end_headers()
            companies = [] #creamos una lista vacía en la que se añaden las empresas
            resultados = self.conexion (limit) #llamamos a la funcion que nos devuelve los resultados de la búsqueda
            for resultado in resultados:
                if ('manufacturer_name' in resultado['openfda']):
                    companies.append (resultado['openfda']['manufacturer_name'][0]) #buscamos dentro de los resultados con las propiedades
                else:
                    companies.append('Empresa no encontrada') #se valora el caso en el que la empresa no se ha podido encontrar
            resultado_html = self.content(companies) #llamamos a la función en la que se encuentra el contenido al rellenar un formularion y ponemos de argumento la lista de empresas para que se añada
            self.wfile.write(bytes(resultado_html, "utf8")) #escribimos el contenido en la página

        #Condición en la que se devuelven una serie de riesgos de los medicamentos al añadir a la url-> listWarnings
        elif 'listWarnings' in self.path:
            # Send response status code
            self.send_response(200)
            self.send_header('Content-type', 'text/html')  #cabeceras necesarias para que el cliente entienda el contenido que le enviamos
            self.end_headers()
            warnings = [] #lista en la que se añadirán las advertencias o riesgos
            resultados = self.conexion (limit)
            for resultado in resultados:
                if ('warnings' in resultado):
                    warnings.append (resultado['warnings'][0]) #buscamos mediante las propiedades de los diccionarios el apartado de warnings
                else:
                    warnings.append('No encontrado') #caso en el que no se encuentran los riesgos o avisos
            resultado_html = self.content(warnings) #llamamos a la función que tiene el contenido de la página tras rellenar el formulario y ponemos como argumento la lista creada anteriormente para que se añada como contenido en la misma
            self.wfile.write(bytes(resultado_html, "utf8")) #escribimos el contenido en la página

        #Condición que nos devuelve lo pedido en el formulario sobre medicamentos
        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')  #cabeceras necesarias para que el cliente entienda el contenido que le enviamos
            self.end_headers()
            limit = 10 #cambiamos limit
            drug=self.path.split('=')[1] #ponemos aquí el igual ya que posteriormente como lo hacemos llamando a una variable
            drugs = []
            conn = http.client.HTTPSConnection(self.url_openfda) #nuestra página es cliente de openfda
            conn.request("GET", self.client_openfda + "?limit="+str(limit) + self.drug_openfda + drug) #creamos la url de petición de nuestra página a openfda
            r1 = conn.getresponse()
            data1 = r1.read()
            data = data1.decode("utf8")
            biblioteca = json.loads(data)
            resultados_drug = biblioteca['results'] #tenemos en una variable los resultados de la búsqueda
            for r in resultados_drug:
                if ('generic_name' in r['openfda']):
                    drugs.append(r['openfda']['generic_name'][0])
                else:
                    drugs.append('Medicamento no encontrado')

            resultado_html = self.content(drugs)
            self.wfile.write(bytes(resultado_html, "utf8"))

        #Condición que nos devuelve lo pedido en el formulario sobre empresas
        elif 'searchCompany' in self.path:
            # Send response status code
            self.send_response(200)
            self.send_header('Content-type', 'text/html')  #cabeceras necesarias para que el cliente entienda el contenido que le enviamos
            self.end_headers()
            limit = 10 #cambiamos limit
            company=self.path.split('=')[1]
            companies = [] #creamos una lista vacía en la que se añaden las empresas
            conn = http.client.HTTPSConnection(self.url_openfda)  #nuestra página es cliente de openfda
            conn.request("GET", self.client_openfda + "?limit=" + str(limit) + self.company_openfda + company) #creamos la url de petición de nuestra página a openfda
            r1 = conn.getresponse()
            data1 = r1.read()
            data = data1.decode("utf8")
            biblioteca = json.loads(data)
            resultados_company = biblioteca['results'] #tenemos en una variable los resultados de la búsqueda

            for u in resultados_company:
                if ('manufacturer_name' in u['openfda']):
                    companies.append(u['openfda']['manufacturer_name'][0])
                else:
                    companies.append('Empresa no encontrada')
            resultado_html = self.content(companies)
            self.wfile.write(bytes(resultado_html, "utf8"))


        #Algunas de las extensiones aunque más arriba podemos encontrar mas

        # Condición en la que al añadir a la url-> secret nos devuelve un error
        elif 'secret' in self.path:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Secure Area"')
            self.end_headers()

        # Condición en la que al añadir a la url-> redirect nos devuelve un error
        elif 'redirect' in self.path:
            self.send_response(302)
            self.send_header('Location', 'http://192.168.1.159:8000')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        # Condición en la que se valora cuando lo que se introduce en la url no está especificado en ninguna de las condiciones anteriores y nos salta un error
        else:
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("I don't know '{}'.".format(self.path).encode())
        return


#Aquí se ejecuta el manejador
socketserver.TCPServer.allow_reuse_address= True
Handler = testHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print("200 OK")
print("serving at port", PORT)
httpd.serve_forever()