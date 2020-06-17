import socket
import ModelRunner as mr
import threading
import os
from time import sleep
import datetime
model_delaytime: str = "5s\n"
buffer_size: int = 1024
time_size: int = 110250
# 24648


class Connection:
    socket: socket.socket
    fileDir: str = './recorded/'

    def __init__(self, connection, info, count, saveMode):
        super().__init__()
        self.socket = connection
        self.info = info
        self.count: int = count
        self.saveMode: bool = saveMode == 1
        print("connected with", info)

    def recieveFile(self) -> bool:
        try:
            size: int = 0
            # recieve file Size
            received = self.socket.recv(2048)
            dataSize: int = int(received[2:])
            # write File
            file = open(self.fileName, "wb")
            received = self.socket.recv(dataSize)
            while True:
                size += len(received)
                file.write(received)
                if not size < dataSize:
                    break
                received = self.socket.recv(dataSize)
            file.close()
            print(self.info, dataSize, "bytes recieved")
            return True
        except Exception as e:
            print("E-start-----------\n",
                  self.info, str(datetime.datetime.now()) + "\n", e,
                  "\nE-end-----------")
            return False

    def controll(self):
        self.socket.sendall(model_delaytime.encode('utf-8'))
        self.fileName = self.fileDir+str(self.count)+"temp.wav"
        print(self.info, "fileName : ", self.fileName)
        while True:
            time: str = datetime.datetime.now().strftime('%m%d%H%M')+"_"
            if self.saveMode:  # update fileName
                recived: int = int(self.socket.recv(2048)[2:])-1
                print(recived)
                if recived == -1:  # urser cancel send file
                    return
                className: str = mr.getClassName(recived)
                self.fileName = self.fileDir+time + str(self.count)+"_"+className+".wav"
            if not self.recieveFile():  # Fail to recieve File
                self.socket.close()
                break
            result, label = mr.classifyFromFile(self.fileName)
            # foramting String for Receiver
            sendString = label + ' '+' '.join(result)+"\n"
            self.socket.sendall(sendString.encode('utf-8'))
            print(self.info, "send data : ", sendString)
            sleep(0.5)
            if not self.saveMode:
                os.remove(self.fileName)


class Runner:
    socCount: int = 0
    host: str
    port: int
    fileName: str
    socket: socket.socket
    accessPin: int = 5523

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
            # run thread with handle function
            t = threading.Thread(target=self.handle, args=(clientSocket, info,))
            t.daemon = True
            t.start()
            self.socCount = self.socCount+1

    def handle(self, socket, info):
        passNum: int = 0
        types: int = 0
        try:
            # saveMode : 1 NonSave : 0
            types = int(socket.recv(1024)[2:])
            sleep(0.5)
            # Authorize
            passNum = int((socket.recv(1024)[2:]))
            print(types, passNum)
        finally:
            if not (passNum == self.accessPin):  # Authorize fail
                socket.send("fail\n".encode())
                socket.close()
                return
        con = Connection(socket, info, self.socCount, types)
        con.controll()
        del con
        print("free controller")


if __name__ == "__main__":
    runner = Runner()
    runner.startServer()
    pass
