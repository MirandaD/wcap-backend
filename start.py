import itchat
import bottle
import os
from pymongo import MongoClient
from bottle import route, run, response, abort, hook, request
from assistant.auth import Auth
from assistant.user import User
from bson import json_util
import json
import assistant.config as config
PORT_NUMBER = 3001

class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

app = bottle.app()
# app.install(EnableCors())
auth = Auth()
User = User()

@hook('after_request')
def _enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
@route('/', method='GET')
def defaultSuccessReturn():
  return 'N/A request'

@route('/get-qrcode/<userId>', method='GET')
def get_qrcode(userId):
    # try:
        userInfo = User.find_user_by_id(userId=userId)
        if userInfo:
            qrcodeUrl = 'https://login.weixin.qq.com/l/' + itchat.get_QRuuid()
            return qrcodeUrl
        else:
            response.status = 401
            return 'Unauthorized'
    # except (RuntimeError, TypeError, NameError) as e:
    #     print('[get_qrcode] error', e)
    #     abort(500, 'Something is wrong with the server.')

@route('/check-login/<uuid>', method=['OPTIONS', 'GET'])
@enable_cors
def handleGet():
    print 'here'
@route('/check-login/<uuid>', method=['OPTIONS', 'POST'])
@enable_cors
def check_login(uuid):
    try:
        requestBody = request.body.read()
        customReply = request.json.get('customReply')
        userId = request.json.get('userId')
        userInfo = User.find_user_by_id(userId=userId)
        if userInfo==None:
            response.status =401
            return 'Unauthorized'
        print customReply
        print requestBody[0]
        result = auth.check_login(uuid=uuid, customReply=customReply)
        print(result)
        if result == '200':
            response.status = 200
            return 'Succeed'
        elif result == '400':
            response.status = 400
            return 'Please scan the qr code before check login.'
        elif result == '408':
            response.status = 408
            return 'Please press confirm on your mobile and check again.'
        else:
            print 'here'
            response.status = 500
            return 'Server Error, please retry'
    except (RuntimeError, TypeError, NameError) as e:
        print('[check-login] error', e)
        response.status = 500
        return 'Server Error, please retry'

@route('/create-user', method=['OPTIONS', 'POST'])
@enable_cors
def create_user():
    try:
        requestBody = request.body.read()
        userInfo = request.json.get('userInfo')
        createdId = User.create_user(userInfo)
        print createdId
        if not createdId == None:
            response.status = 200
            return createdId
        else:
            response.status = 400
            return 'Failed'
    except (RuntimeError, TypeError, NameError) as e:
        print('Unexpected error', e)
        response.status = 500
        return 'Server Error'

@route('/login', method=['OPTIONS', 'POST'])
@enable_cors
def login_user():
    try:
        email = request.json.get('email')
        password = request.json.get('password')
        userFound = User.find_user_by_email_password(email=email, password=password)
        if userFound!=None and userFound['password'] == password:
           response.status = 200
           userFound['password'] = None
           return json.dumps(userFound, indent=4, sort_keys=True, default=str)
        else:
           response.status = 401
           return 'User not exist'
    except (RuntimeError, TypeError, NameError) as e:
        print('Unexpected error', e)
        response.status = 500
        return 'Server Error'

app.run(host=config.BACKEND_HOST, port=config.BACKEND_PORT)

