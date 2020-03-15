from serverCode.server_socket import ServerSocket
from serverCode.socket_wrapper import SocketWrapper
from threading import Thread
from serverCode.config import *
from serverCode.response_protocol import ResponseProtocol
from serverCode.db import DB


class Server():
    '''服务器核心类'''

    def __init__(self):

        self.serverSocket = ServerSocket()        # 创建一个服务器套接字
        self.clients = {}
        # 创建请求的ID和处理方法之间的关联字典
        self.handleFunctionDict = {}
        self.idBindingFunction(REQUEST_LOGIN, self.requestLoginHandle)
        self.idBindingFunction(REQUEST_CHAT, self.requestChatHandle)
        self.db = DB()

    def idBindingFunction(self, requestId, handleFunction):
        '''请求id与处理方法绑定'''
        self.handleFunctionDict[requestId] = handleFunction

    def startUp(self):

        while True:
            # 建立连接
            print("服务器接收连接...")
            connect, addr = self.serverSocket.accept()
            # 客户端套接字包装对象
            clientSocket = SocketWrapper(connect)
            # 使用新的线程收发消息
            Thread(target=lambda :self.requestHandle(clientSocket)).start()

    def requestHandle(self, clientSocket):
        '''处理客户端请求消息'''
        while True:
            recvMessage = clientSocket.receiveData()
            if not recvMessage:
                self.removeOfflineUser(clientSocket)
                break
            clientSocket.sendData("接收到的消息是：{}".format(recvMessage))

            # 解析数据
            parseDict = self.parseRequestMsg(recvMessage)
            # 分析请求类型 根据请求类型调用相应的处理函数
            handleFunction = self.handleFunctionDict.get(parseDict["requestId"])
            if handleFunction:
                handleFunction(clientSocket, parseDict)

    def removeOfflineUser(self, clientSocket):
        print("客户端下线...")
        for username, info in self.clients.items():
            if info["sock"] == clientSocket:
                del self.clients[username]
        clientSocket.close()

    def parseRequestMsg(self, recvMessage):
        '''
        解析客户端发送过来的请求数据
        :param recvMessage: 登录信息：0001|username|password 聊天信息：0002|username|message
        :return:
        '''
        print("解析客户端请求数据")
        requestList = recvMessage.split(DELIMITER)
        requestDict = {}
        requestDict["requestId"] = requestList[0]

        if requestDict["requestId"] == REQUEST_LOGIN:
            requestDict["username"] = requestList[1]
            requestDict["password"] = requestList[2]

        elif requestDict["requestId"] == REQUEST_CHAT:
            requestDict["username"] = requestList[1]
            requestDict["message"] = requestList[2]

        return requestDict

    def requestLoginHandle(self, clientSocket, requestData):

        print("处理用户登录请求")
        userName = requestData.get("username")
        passWord = requestData.get("password")
        # 检查用户信息
        result, nickName, userName = self.checkUserLogin(userName, passWord)
        # 如果登录成功则需要保存当前用户
        if result == "1":
            self.clients[userName] = {"sock":clientSocket, "nickName":nickName}
        # 拼接返回给客户端的消息
        responseInfo = ResponseProtocol.responseLoginResult(result, nickName, userName)
        # 把消息发送给客户端
        clientSocket.sendData(responseInfo)

    def checkUserLogin(self, username, password):
        '''检查用户是否登录成功，并返回检查结果'''
        resultInfo = self.db.queryFromDb("select * from users where user_name={}".format(username))
        # 用户不存在
        if not resultInfo:
            return '0', '', username
        # 密码错误
        if password != resultInfo.get("user_password"):
            return '0', '', username
        # 登录成功
        return '1', resultInfo.get("user_nickname"), username

    def requestChatHandle(self, clientSocket, requestData):
        '''处理聊天请求 并将聊天内容发送给所有用户'''
        userName = requestData.get("username")
        message = requestData.get("message")
        nickName = self.clients[userName]['nickName']
        responseMsg = ResponseProtocol.responseChat(nickName, message)

        # 将消息转发给当前在线用户
        for user, info in self.clients.items():
            # 不需要向发送消息的账号转发数据
            if clientSocket == self.clients[userName]["sock"]:
                continue
            info["sock"].sendData(responseMsg)
