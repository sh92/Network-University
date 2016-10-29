import socket
import threading

class ThreadedServer(object):
    def __init__(self, host, port):
        self.connections = set()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def serverMessage(self, client, address):
        while True:
            message = input('[Server]')
            self.broadcast(message,client,address)
            if message[8:12].lower() == 'quit':
                break

    def listen(self):
        self.sock.listen(10)
        while True:
            client, address = self.sock.accept()
            client.settimeout(600)
            self.connections.add((client,address))
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def broadcast(self,data,client,address):
        print("boradCast")
        for conn,addr in self.connections:
            if conn== client and addr == address:
                continue
            print(addr)
            conn.send((data).encode())

    def listenToClient(self, client, address):
        size = 4096
        threading.Thread(target = self.serverMessage,args = (client,address)).start()
        while True:
            try:
                data = client.recv(size)
                if data:
                    response = data.decode('utf-8')
                    print(response)
                    self.broadcast(response,client,address)
                else:
                    self.connections.remove((client,address)) 
                    raise error('Client disconnected')
            except:
                client.close()
                return False

if __name__ == "__main__":
    port_num = input("Port? ")
    ThreadedServer('',int(port_num)).listen()
