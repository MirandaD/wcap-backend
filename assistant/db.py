from pymongo import MongoClient

class DB():
    def get_login_info_by_uuid(self, uuid):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['wacp-dev']
        return db.loginInfo.find_one({'uuid': uuid})
