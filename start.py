import itchat
import bottle
import os
from pymongo import MongoClient
from bottle import route, run, response, abort, hook
from assistant.auth import Auth
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
app = bottle.app()
auth = Auth()
@itchat.msg_register(itchat.content.TEXT)
def print_contentm(msg):
    print(msg['Text'])

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
@route('/')

@route('/get-qrcode', method='GET')
def get_qrcode():
    try:
        qrcodeUrl = 'https://login.weixin.qq.com/l/' + itchat.get_QRuuid()
        return qrcodeUrl
    except (RuntimeError, TypeError, NameError):
        print('[get_qrcode] error')
        abort(500, 'Something is wrong with the server.')

@route('/check-login/<uuid>', method='GET')
def check_login(uuid):
    try:
        result = auth.check_login(uuid=uuid)
        print(result)
        if result == uuid:
            return 'Succeed'
        elif result == '400':
            return 'OK'
        elif result == '408':
            return 'OK'
        else:
            abort(500, result)
    except (RuntimeError, TypeError, NameError) as e:
        print('[check-login] error', e)
        abort(500, 'Something is wrong with the server.')

# @route('/get-user-info')
if os.environ.get('APP_LOCATION') == 'heroku':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    app.run(host='localhost', port=3001, debug=True)

