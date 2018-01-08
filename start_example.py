import itchat, time, sys


import itchat

c = itchat.auto_login()
# def send(self, msg, toUserName=None, mediaId=None)
print c
r = itchat.send_msg(msg='succeed!', toUserName='filehelper')
print r
r2 = itchat.send_raw_msg(msgType=1, content='123', toUserName='filehelper')
print r2