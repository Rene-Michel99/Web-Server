import pickle
import datetime

class Router:
    def __init__(self):
        self.routes = {
            "/":"./pages/index.html",
            "/cadastrar":"./pages/cadastro.html",
            "/login":"./pages/home.html",
            "/login.html":"./pages/login.html",
            "/deposito":"./pages/home.html",
            "/sacar":"./pages/home.html",
            "/transferir":"./pages/home.html",
            "/extrato":"./pages/extrato.html",
            "/home":"./pages/home.html",
            "/logout":"./pages/index.html",
            "/login_error":"./pages/error.html"
        }
        self.session = {}
        print("-*- PAGES:",self.routes)

    def GET(self,params,to_page):
        modifications = None
        if to_page == "/extrato":
            modifications = self.extrato()
        elif to_page == "/logout":
            self.save()
        return to_page,modifications

    def POST(self,params,to_page):
        cadastro = params
        modifications = None
        if to_page == "/cadastrar":
            self.cad_session(params)
        elif to_page == "/login":
            logged = self.login(params)
            if not logged:
                to_page = "/login_error"
            else:
                modifications = logged
        elif to_page == "/deposito":
            self.deposito(params)
        elif to_page == "/sacar":
            self.sacar(params)
        elif to_page == "/transferir":
            self.transferir(params)

        return to_page,modifications

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
        html = ""
        for date,cash in self.session["transferencias"]:
            html += "<tr><td>"+date+"</td><td>"+cash+"</td></tr>"
        html += "<tr><td>Saldo:</td><td>"+str(self.session["cash"])+"</td></tr>"
        modifications = {"{data}":html}
        return modifications

    def login(self,params):
        cpf = params.split("&")[0].split("=")[1]
        senha = params.split("&")[1].split("=")[1]
        with open("accounts.data","rb") as f:
            accounts = pickle.load(f)
            for acc in accounts:
                if acc["cpf"] == cpf and acc["senha"] == senha:
                    self.session = acc
                    print("-*- logged:",self.session)
                    return {"{id}":acc["nome"]}
        return False

    def save(self):
        accs = []
        with open("accounts.data","rb") as f:
            accs = pickle.load(f)
        for acc in accs:
            if self.session["cpf"] == acc["cpf"] and self.session != acc:
                index = accs.index(acc)
                accs[index] = self.session
                with open("accounts.data","wb") as f:
                    pickle.dump(accs,f)
                break
        self.session.clear()
