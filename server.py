import os
import re
import pickle
import socket
import datetime
import threading
from routes import Router
from HTTP import HTTPpackage
from HandlerThreads import HandlerThreads

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.running = True
        self.source = []
        self.router = Router()
        self.http = HTTPpackage()

        self.define_source()

        self.multiThread = HandlerThreads()

        tm = threading.Thread(target=self.multiThread.check)
        tm.daemon = True
        tm.start()

        th = threading.Thread(target=self.handleInput)
        th.daemon = True
        th.start()

        self.start()

    def define_source(self):
        for file in os.listdir('./src'):
            if os.path.isdir("./src/"+file):
                for item in os.listdir("./src/"+file):
                    self.source.append("/src/"+file+"/"+item)
            else:
                self.source.append("/src/"+file)
        print("-*- source:",self.source)

    def handleInput(self):
        while self.running:
            cmd = input("")
            if cmd == "quit":
                self.running = False
                self.server.setblocking(True)
                print("-*- Desligando...")
                self.multiThread.running = False
                self.multiThread.blockAll()
            elif cmd == "getalivethreads":
                self.multiThread.getAliveThreads()

    def existDirectory(self,search):
        if search == "":
            return self.router.routes["/"]

        for key in self.router.routes.keys():
            if self.router.routes[key] == search != -1 or search == key:
                return self.router.routes[key]

        for file in self.source:
            if file == search:
                return "."+file
        return None

    def get_content(self,path,mod):
        data = None
        if path.find('/img/') == -1:
            arq = open(path,'r',encoding='utf-8')
            data = arq.read()
            if mod:
                for key in mod.keys():
                    data = data.replace(key,mod[key])
            arq.close()
        else:
            arq = open(path,'rb')
            data = arq.read()
            arq.close()
        return data

    def pack(self,page,data):
        if type(data) == bytes:
            pack = page.encode()+ data + "\r\n\r\n".encode()
            return pack
        else:
            pack = page+data+"\r\n\r\n"
            return pack.encode()

    def get_page(self,to_page,mod=None):
        path = self.existDirectory(to_page)
        print("-*- page:",to_page,"=>",path)
        if path:
            print("-*- localhost: OK STATUS")
            template = self.http.get_template(path)
            data = self.get_content(path,mod)
            pack = self.pack(template,data)
            return pack
        else:
            print("-*- localhost: 404 NOT FOUND")
            return self.http.get_error_template().encode()

    def treat_method(self,method,params,to_page):
        if method == "GET":
            to_page,modifications = self.router.GET(params,to_page)
            return self.get_page(to_page,modifications)
        elif method == "POST":
            to_page,modifications = self.router.POST(params,to_page)
            return self.get_page(to_page,modifications)

    def handleNewConnection(self,client):
        request = client.recv(5000).decode()
        request = request.split("\n")
        data = ""

        if(request[0]):
            method = request[0].split()[0]
            to_page = request[0].split()[1]

            print("-*- cliente: METHOD [",method,"]")

            params = request[len(request)-1]
            data = self.treat_method(method,params,to_page)

            client.sendall(data)
            try:
                client.shutdown(1)
            except:
                pass

    def start(self):
        self.server.bind(("localhost",8080))
        self.server.settimeout(10)
        self.server.listen(5)
        print("-*- Server iniciado (localhost:8080)\n-*- Digite 'quit' para encerrar o sevidor\n")

        while self.running:
            try:
                client,address = self.server.accept()
                self.multiThread.add_client(client)
                print("---------------------------------------------------------")
                print("-*- cliente: ",address,end="")

                self.multiThread.newThread(client,self.handleNewConnection)
            except:
                pass
        self.multiThread.close_all_conns()
        self.server.close()

server = Server()
