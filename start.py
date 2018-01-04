import itchat
import bottle
from bottle import route, run, response, abort
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
@itchat.msg_register(itchat.content.TEXT)
def print_contentm(msg):
    print(msg['Text'])
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
        result = itchat.check_login(uuid=uuid)
        if result == '200':
            return 'OK'
        elif result == '400':
            abort(400)
        else:
            abort(500, result)
    except (RuntimeError, TypeError, NameError):
        print('[check-login] error')
        abort(500, 'Something is wrong with the server.')

app.install(EnableCors())
if os.environ.get('APP_LOCATION') == 'heroku':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    app.run(host='localhost', port=8080, debug=True)

