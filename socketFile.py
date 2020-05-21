import socket
import ModelRunner as mr
import threading
import os
from time import sleep
model_delaytime: str = "5s\n"
buffer_size: int = 1024
time_size: int = 110250
# 24648


class Connection:
    socket: socket.socket

    def __init__(self, connection, info, count):
        super().__init__()
        print("connected with", info)
        self.socket = connection
        self.info = info
        self.count = count
        self.fileName = str(self.count)+"temp.wav"

    def recieveFile(self) -> bool:
        try:
            received = self.socket.recv(2048)
            dataSize: int = int(received[2:])
            print("dataSize", dataSize)
            print("fileName : ", self.fileName)
            file = open(self.fileName, "wb")
            size = 0
            received = self.socket.recv(dataSize)
            while True:
                size += len(received)
                file.write(received)
                if not size < dataSize:
                    break
                received = self.socket.recv(dataSize)
            file.close()
            print("recieved")
            return True
        except Exception as e:
            print(e)
            print("Excepted !!")
            return False

    def controll(self):
        self.socket.sendall(model_delaytime.encode('utf-8'))
        while True:
            if not self.recieveFile():
                return
            result, label = mr.classifyFromFile(self.fileName)
            sendString = label + ' '+' '.join(result)+" endData\n"
            print(sendString)
            self.socket.sendall(sendString.encode('utf-8'))
            print("data sended")
            sleep(0.5)
            os.remove(self.fileName)


class Runner:
    socCount: int = 0
    host: str
    port: int
    fileName: str
    socket: socket.socket

    def __init__(self, host: str = '192.9.45.72', port: int = 3389):
        self.host = host
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.host, self.port))
        super().__init__()

    def startServer(self):
        print('start NC Server')
        self.serverSocket.listen()
        while True:
            clientSocket, info = self.serverSocket.accept()
            con = Connection(clientSocket, info, self.socCount)
            t = threading.Thread(self.handle(con))
            # t.start()
            self.socCount = self.socCount+1

    def handle(self, con: Connection):
        con.controll()
        sleep(0.5)

        del con
        print("free controller")


if __name__ == "__main__":
    runner = Runner()
    runner.startServer()
    pass
