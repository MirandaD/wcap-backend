import os, platform

VERSION = '1.3.10'
BASE_URL = 'https://login.weixin.qq.com'
OS = platform.system() # Windows, Linux, Darwin
DIR = os.getcwd()
DEFAULT_QR = 'QR.png'
TIMEOUT = (10, 60)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'

#default config:
MONGODB_URL = 'mongodb://localhost:27017/'
BACKEND_URL = 'http://loaclhost:3001'
BACKEND_HOST = 'localhost'
BACKEND_PORT = 3001
if os.environ.get('APP_LOCATION')=='prod' or os.environ.get('APP_LOCATION')=='heroku':
  MONGODB_URL = 'mongodb://mirandaLi:lisirui1020@cluster0-shard-00-00-eluxi.mongodb.net:27017,cluster0-shard-00-01-eluxi.mongodb.net:27017,cluster0-shard-00-02-eluxi.mongodb.net:27017/admin?readPreference=primary&ssl=true'
  BACKEND_URL = 'https://wcap-backend.herokuapp.com'
  BACKEND_HOST = '0.0.0.0'
  BACKEND_PORT = int(os.environ.get("PORT", 5000))