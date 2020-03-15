

class SocketWrapper():
    '''客户端套接字包装类'''

    def __init__(self, connect):
        self.connect = connect

    def receiveData(self):
        try:
            return self.connect.recv(512).decode("utf-8")
        except:
            return ""

    def sendData(self, message):
        return self.connect.send(message.encode("utf-8"))

    def close(self):
        self.connect.close()