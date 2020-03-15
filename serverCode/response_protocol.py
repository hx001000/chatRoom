from serverCode.config import *


class ResponseProtocol(object):
    '''服务器响应协议的格式化字符串处理'''

    @staticmethod
    def responseLoginResult(result, nickName, userName):
        '''
        生成用户登录的结果字符串
        :param result:      0 成功 1 失败
        :param nickName:    昵称 登录失败为空
        :param userName:    用户名 登录失败为空
        :return:            返回给用户的登录结果
        '''
        return DELIMITER.join(RESPONSE_LOGIN, result, nickName, userName)

    @staticmethod
    def responseChat(nickName, message):
        '''
        生成返回给用户的消息字符串
        :param nickName:    发送消息的用户昵称
        :param message:     消息正文
        :return:
        '''
        return DELIMITER.join(RESPONSE_CHAT, nickName, message)

