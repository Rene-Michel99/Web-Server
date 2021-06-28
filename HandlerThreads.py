import threading
import socket
import time

class HandlerThreads:
    def __init__(self):
        self.threads = []
        self.conns = []
        self.running = True

    def add_client(self,client):
        self.conns.append(client)

    def close_all_conns(self):
        print("-*- Closing",len(self.conns),"connections...")
        time.sleep(5)
        for client in self.conns:
            client.close()

    def blockAll(self):
        for conn in self.conns:
            conn.settimeout(1)

    def newThread(self,client,fn):
        th = threading.Thread(target=fn,args=(client,))
        th.daemon = True
        th.start()

        self.threads.append(th)
        print("-*- Thread ",th," iniciada")

    def getAliveThreads(self):
        print("\n-*- Threads em execução")
        for thread in self.threads:
            if thread.isAlive():
                print(thread)

    def check(self):
        while self.running:
            for thread in self.threads:
                if not thread.isAlive():
                    self.threads.remove(thread)
                    print("-*-",thread," encerrada.")
                    print("-------------------------------------------------------\n")
                    break
        if not self.running:
            if self.threads!=[]:
                print("-*-",len(self.threads)," threads recentes fechadas.")
                self.threads.clear()
