import db
import pydash
import datetime

class User():
    def __init__(self):
        self.DB = db.DB()
    def validate_basic_info(self):
        if self.username and self.email and self.password and self.wechatId:
            return True
        return False

    def create_user(self, userInfo):
        self.username = pydash.get(userInfo, 'username')
        self.email = pydash.get(userInfo, 'email')
        self.password = pydash.get(userInfo, 'password')
        self.wechatId = pydash.get(userInfo, 'wechatId')
        newUser = {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'wechatId': self.wechatId,
            'created': datetime.datetime.now(),
            'lastLogin': datetime.datetime.min,
            'loginInfo': None
        }
        savedUserId = self.DB.create_user(newUser)
        return savedUserId

    def find_user_by_id(self, userId):
        userInfo = self.DB.find_user_by_id(userId)
        if not userInfo:
            return False
        return userInfo
        
    def find_user_by_email_password(self, email, password):
        userInfo = self.DB.find_user(password=password, email=email)
        if userInfo:
            return userInfo
        else:
            return None
        
