from pymongo import MongoClient
from bson.objectid import ObjectId
import os

class DB():
    def __init__(self):
        self.mongoConnectionStr = 'mongodb://localhost:27017/'
        print os.environ.get('APP_LOCATION')
        if os.environ.get('APP_LOCATION') == 'heroku':
            self.mongoConnectionStr = 'mongodb://mirandaLi:lisirui1020@cluster0-shard-00-00-eluxi.mongodb.net:27017,cluster0-shard-00-01-eluxi.mongodb.net:27017,cluster0-shard-00-02-eluxi.mongodb.net:27017/admin?readPreference=primary&ssl=true'
        self.client = MongoClient(self.mongoConnectionStr)
        self.db = self.client['wacp-dev']
        self.LoginInfo = self.db.loginInfo
        self.Messages = self.db.Messages
        self.User = self.db.User
    def get_login_info_by_uuid(self, uuid):
        client = MongoClient(self.mongoConnectionStr)
        db = client['wacp-dev']
        return db.loginInfo.find_one({'uuid': uuid})
    def create_user(self,userInfo):
        res = self.User.insert_one(userInfo)
        return res.inserted_id
    def find_user(self,email, password):
        res = self.User.find_one({'email': email, 'password': password})
        return res
    def find_user_by_id(self, userId):
        res = self.User.find_one({'_id': ObjectId(userId)})
        return res
