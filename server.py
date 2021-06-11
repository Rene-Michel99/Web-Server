import os
import re
import pickle
import socket
import datetime
import threading
from HTTP import HTTPpackage
from HandlerThreads import HandlerThreads

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.running = True
        self.paths = {}
        self.source = []
        self.session = {}
        self.http = HTTPpackage()

        self.define_pages()
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

    def define_pages(self):
        pages = os.listdir('./pages')

        self.paths["/"] = "./pages/index.html"
        self.paths["/cadastrar"] = "./pages/home.html"
        self.paths["/cadastro.html"] = "./pages/cadastro.html"
        self.paths["/login.html"] = "./pages/login.html"
        self.paths["/login"] = "./pages/home.html"
        self.paths["/deposito"] = "./pages/home.html"
        self.paths["/logout"] = "./pages/index.html"
        self.paths["/sacar"] = "./pages/home.html"
        self.paths["/home"] = "./pages/home.html"
        self.paths["/transferir"] = "./pages/home.html"
        self.paths["/login_error"] = "./pages/error.html"

        print("-*- PAGES:",self.paths)

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
            return self.paths["/"]

        for key in self.paths.keys():
            if self.paths[key] == search != -1 or search == key:
                return self.paths[key]

        for file in self.source:
            if file == search:
                return "."+file
        return None

    def get_content(self,path):
        data = None
        if path.find('/img/') == -1:
            arq = open(path,'r',encoding='utf-8')
            data = arq.read()
            if data.find("{id}") != -1:
                data = data.replace("{id}",self.session["nome"])
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

    def get_page(self,to_page):
        path = self.existDirectory(to_page)
        print("-*- page:",to_page,"=>",path)
        if path:
            print("-*- localhost: OK STATUS")
            template = self.http.get_template(path)
            data = self.get_content(path)
            pack = self.pack(template,data)
            return pack
        else:
            print("-*- localhost: 404 NOT FOUND")
            return self.http.get_error_template().encode()

    def GET(self,params,to_page):
        if to_page == "/extrato":
            return self.extrato()
        elif to_page == "/logout":
            self.save()

        data = self.get_page(to_page)

        return data

    def cad_session(self,data):
        data = data.split("&")
        for dt in data:
            self.session[dt.split("=")[0]] = dt.split("=")[1]
        self.session["cash"] = 0
        self.session["transferencias"] = []
        print("-*- session:",self.session)

    def deposito(self,params):
        date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        cash = params.split("=")[1]
        self.session["cash"] += int(cash)
        self.session["transferencias"].append([date,"Depositado: +"+cash])

    def sacar(self,params):
        date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        cash = params.split("=")[1]
        self.session["cash"] -= int(cash)
        self.session["transferencias"].append([date,"Sacado: -"+cash])

    def transferir(self,params):
        date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        cpf = params.split("&")[0].split("=")[1]
        cash = params.split("&")[1].split("=")[1]
        self.session["cash"] -= int(cash)
        self.session["transferencias"].append([date,"Transferido: "+cash+" -> "+cpf])

    def extrato(self):
        with open("./pages/extrato.html","r",encoding='utf-8') as f:
            html = f.read()
            html = html.split("\n")
            init = html.index("          {data}")
            for date,cash in self.session["transferencias"]:
                html = html[:init]+["<tr><td>"+date+"</td><td>"+cash+"</td></tr>"]+html[init:]
                init += 1
            html = "".join(html)
            html = html.replace("{data}","")
            html = html.replace("{end}","<tr><td>"+"Saldo Atual:"+"</td><td>"+str(self.session["cash"])+"</td></tr>")
            pack = self.pack(self.http.get_ok_template(),html)
            return pack

    def login(self,params):
        cpf = params.split("&")[0].split("=")[1]
        senha = params.split("&")[1].split("=")[1]
        with open("accounts.data","rb") as f:
            accounts = pickle.load(f)
            for acc in accounts:
                if acc["cpf"] == cpf and acc["senha"] == senha:
                    self.session = acc
                    return True
        return False

    def save(self):
        accs = []
        with open("accounts.data","rb") as f:
            accs = pickle.load(f)
        print(accs)
        for acc in accs:
            if self.session["cpf"] == acc["cpf"] and self.session != acc:
                index = accs.index(acc)
                accs[index] = self.session
                with open("accounts.data","wb") as f:
                    pickle.dump(accs,f)
                break
        self.session.clear()

    def POST(self,params,to_page):
        cadastro = params
        if to_page == "/cadastrar":
            self.cad_session(params)
        elif to_page == "/login":
            if not self.login(params):
                to_page = "/login_error"
        elif to_page == "/deposito":
            self.deposito(params)
        elif to_page == "/sacar":
            self.sacar(params)
        elif to_page == "/transferir":
            self.transferir(params)

        print("-*-",self.session)

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
