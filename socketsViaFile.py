import socket
import ModelRunner as mr
from array import array
import threading
import numpy as np
model_delaytime: str = "5s\n"
buffer_size: int = 1024
time_size: int = 110250
host_name: str = '192.9.45.72'
port_num: int = 3389

# 24648

socCount: int = 0


class Runner:
    socCount: int = 0

    def __init__(self):
        self.serverSocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((host_name, port_num))
        self.serverSocket.listen()
        print('start NC Server')
        while True:
            clientSocket, info = self.serverSocket.accept()
            self.socCount = self.socCount+1
            print(str(self.socCount)+" connected")
            t = threading.Thread(self.socketSub(clientSocket, self.socCount))
            t.start()

    def recieveFile(self, clientSocket, socCount):
        # fileName = clientSocket.recv(1024).decode()
        fileName = "temp.wav"
        fileName = str(socCount)+fileName
        print("fileName : "+fileName)
        lines = clientSocket.recv(1024)
        lines = lines.decode(encoding='utf-8', errors='replace')
        print(len(lines), lines.strip(), type(lines))
        print(int(lines.strip()))
        # print(lines.)
        # print(lines.split())
        # lines = int(lines)
        try:
            data = clientSocket.recv(1024)

            with open(fileName, 'wb')as file:
                i = 0
                while str(i) != str(lines.strip()):
                    i += 1
                    print(i)
                    file.write(data)
                    data = clientSocket.recv(1024)
                file.write(data)
            print("recieved!!!")

        except Exception as e:
            print('Error!!', e)
        return fileName

    def socketSub(self, clientSocket, socCount):
        try:
            clientSocket.send(model_delaytime.encode('utf-8'))
            fileName = self.recieveFile(clientSocket, socCount)
            result = mr.roadWav(fileName)
            print(result+" asd")
            clientSocket.send((result+"\nendData").encode('utf-8'))

        except Exception as e:
            print(e)


if __name__ == "__main__":
    runner = Runner()

    pass
