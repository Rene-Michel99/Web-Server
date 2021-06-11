import os
import socket
import threading
import re
import datetime

def VerificaDiretorio():
    # Getting the current work directory (cwd)
    thisdir = os.getcwd()   #thisdir recebe o caminho da pasta atual

    # r=root, d=directories, f = files
    caminhos = []

    #percorre pastas em busca de arquivos
    for r, d, f in os.walk(thisdir): #os.walk "caminha entre os diretorios para encontrar o arquivo especificado"
        for file in f:
            if "" in file:
                caminho_completo = (os.path.join(r, file))
                caminho_a_partir_do_host = caminho_completo.find("Trabalho_16_09")
                caminhos.append(caminho_completo[caminho_a_partir_do_host + 15:])

    #percorre pastas em busca de pastas
    for r, d, f in os.walk(thisdir): #os.walk "caminha entre os diretorios para encontrar o arquivo especificado"
        for file in d:
            if "" in file:
                caminho_completo = (os.path.join(r, file))
                caminho_a_partir_do_host = caminho_completo.find("Trabalho_16_09")
                caminhos.append(caminho_completo[caminho_a_partir_do_host + 15:])

    contador = 0
    for item in caminhos:
        caminhos[contador] = item.replace("\\", '/')
        contador += 1

    caminhos_organizados = []
    for item in caminhos:
        if '.' not in item:
            caminhos_organizados.append(item)

    for item in caminhos:
        if item not in caminhos_organizados:
            caminhos_organizados.append(item)

    #print (caminhos_organizados)

    return caminhos_organizados

class HandleThreads:
    def __init__(self):
        self.threads = []
        self.running = True

    def newThread(self,client,fn):
        th = threading.Thread(target=fn,args=(client,))
        th.daemon = True
        th.start()

        self.threads.append(th)
        print("\nThread ",th," iniciada")

    def getAliveThreads(self):
        print("\nThreads em execução")
        for thread in self.threads:
            if thread.isAlive():
                print(thread)


    def check(self):
        while self.running:
            for thread in self.threads:
                if not thread.isAlive():
                    self.threads.remove(thread)
                    print("\nThread ",thread," encerrada. Desalocando...")
                    print("-------------------------------------------------------\n")
                    break
        if not self.running:
            if self.threads!=[]:
                print(len(self.threads)," threads recentes fechadas.")
                self.threads.clear()


class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.running = True
        self.conns = []
        self.paths = {}

        self.define_pages()

        self.multiThread = HandleThreads()

        tm = threading.Thread(target=self.multiThread.check)
        tm.daemon = True
        tm.start()

        th = threading.Thread(target=self.handleInput)
        th.daemon = True
        th.start()

        self.start()

    def define_pages(self):
        pages = os.listdir('./pages')

        self.paths["/"] = "./pages/index.html"

        for item in pages:
            if item == "main.html":
                self.paths["/cadastrar"] = "./pages/"+item
            else:
                self.paths["/"+item] = "./pages/"+item
        print("PAGES:",self.paths)

    def blockAll(self):
        for conn in self.conns:
            conn.settimeout(1)

    def close_all_conns(self):
        print("-*- Closing",len(self.conns),"connections...")
        for client in self.conns:
            client.close()

    def handleInput(self):
        while self.running:
            cmd = input("")
            if cmd == "quit":
                self.running = False
                self.server.setblocking(True)
                print("Desligando...")
                self.multiThread.running = False
                self.blockAll()
            elif cmd == "getalivethreads":
                self.multiThread.getAliveThreads()

    def existDirectory(self,search):
        if search == "":
            return self.paths["/"]

        for key in self.paths.keys():
            if self.paths[key].find(search) != -1 or search == key:
                return self.paths[key]
        return None

    def get_ok_template(self):
        data = "\r\nHTTP/1.1 200 OK\r\n"
        data += "Data: "+datetime.datetime.now().strftime('%d/%m/%Y %H:%M')+"\r\n"
        data += "Server: ServidorWeb\r\n"
        data += "Content-Type: text/html\r\n"
        data += "\r\n"

        return data

    def get_error_template(self):
        data = "HTTP/1.1 404 NOT FOUND\r\n"
        data += "Data: "+datetime.datetime.now().strftime('%d/%m/%Y %H:%M')+"\r\n"
        data += "Server: ServidorWeb\r\n"
        data += "Content-Type: text/html\r\n"
        data += "\r\n"
        data += "<html><body><h1>ERROR 404 NOT FOUND</h1></body></html>\r\n\r\n"

        return data

    def get_content(self,path):
        arq = open(path,'r',encoding='utf-8')
        data = arq.read()
        arq.close()

        return data+"\r\n\r\n"

    def get_page(self,to_page):
        path = self.existDirectory(to_page)
        print("--->",path)
        if path:
            print("OK STATUS")
            page = self.get_ok_template()
            page += self.get_content(path)
            return page
        else:
            print("404 NOT FOUND")
            return self.get_error_template()

    def GET(self,params,to_page):
        data = self.get_page(to_page)

        return data

    def POST(self,params,to_page):
        cadastro = params
        print("data:",cadastro)

        data = self.get_page(to_page)
        return data

    def treat_method(self,method,params,to_page):
        if method == "GET":
            return self.GET(params,to_page)
        elif method == "POST":
            return self.POST(params,to_page)

    def handleNewConnection(self,client):
        request = client.recv(5000).decode()
        request = request.split("\n")
        data = ""

        if(request[0]):
            method = request[0].split()[0]
            to_page = request[0].split()[1]

            print("METHOD [",method,"]")

            params = request[len(request)-1]
            data = self.treat_method(method,params,to_page)

            client.sendall(data.encode())
            client.shutdown(1)

    def start(self):
        self.server.bind(("localhost",8080))
        self.server.settimeout(10)
        self.server.listen(5)
        print("Server iniciado (localhost:8080)\nDigite 'quit' para encerrar o sevidor")

        while self.running:
            try:
                client,address = self.server.accept()
                self.conns.append(client)
                print("---------------------------------------------------------")
                print("Cliente: ",address,end="")

                self.multiThread.newThread(client,self.handleNewConnection)
            except:
                pass
        self.close_all_conns()
        self.server.close()

server = Server()
