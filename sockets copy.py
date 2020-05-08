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


def runServer():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((host_name, port_num))
        serverSocket.listen()
        while True:
            clientSocket, addr_info = serverSocket.accept()
            print("connected")
            t = threading.Thread(socketSub(clientSocket))
            t.start()
    return 0


def socketSub(clientSocket):
    try:
        clientSocket.send(model_delaytime.encode('utf-8'))
        # data = bytearray()
        data = None
        while True:
            # data.extend(clientSocket.recv(buffer_size))
            arr = []
            for a in range(0, 6):
                for i in range(0, 216):
                    print(a, i)
                    data = clientSocket.recv(buffer_size)
                    try:
                        arr = np.append(arr, np.frombuffer(
                            data, dtype=np.float64))
                    except Exception as e:
                        pass
            result = mr.input_from_android(arr)
            print(result)
            #     if len(data) > time_size:
            #         print(type(data))
            #         # print(array(data))
            #         # print("-----")
            #         result = mr.getInputFromAndroid(data[:time_size])
            #         data = data[time_size:]
            #         print(result)
            # clientSocket.sendall(result.encode('utf-8'))
    except Exception as e:
        print(e)
        print('terminate')


if __name__ == "__main__":
    print("start NC server")
    runServer()

    pass
