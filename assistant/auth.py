import re
import requests
import json, xml.dom.minidom
import time
import itchat
from pymongo import MongoClient
from . import config

class Auth():
    def __init__(self):
        self.requests = requests.Session()
    def check_login(self, uuid):
        print('hey, good here')
        url = '%s/cgi-bin/mmwebwx-bin/login' % config.BASE_URL
        localTime = int(time.time())
        params = 'loginicon=true&uuid=%s&tip=1&r=%s&_=%s' % (
            uuid, int(-localTime / 1579), localTime)
        headers = { 'User-Agent' : config.USER_AGENT }
        r = self.requests.get(url, params=params, headers=headers)
        regx = r'window.code=(\d+)'
        data = re.search(regx, r.text)
        if data and data.group(1) == '200':
            savedLoginInfo = self.process_login_info(r.text, uuid)
            if savedLoginInfo:
                return '200'
            else:
                return '400'
        elif data:
            return data.group(1)
        else:
            return '400'

    def save_login_info(self, loginInfo):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['wacp-dev']
        inserted = db.loginInfo.insert_one(loginInfo)
        return inserted

    def get_login_info_by_uuid(self, uuid):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['wacp-dev']
        return db.loginInfo.find_one({'uuid': uuid})

    def web_init(self, loginInfo):
        url = '%s/webwxinit' % loginInfo['url']
        params = {
            'r': int(-time.time() / 1579),
            'pass_ticket': loginInfo['pass_ticket'], }
        data = { 'BaseRequest': loginInfo['BaseRequest'], }
        headers = {
            'ContentType': 'application/json; charset=UTF-8',
            'User-Agent' : config.USER_AGENT, }
        r = self.requests.post(url, params=params, data=json.dumps(data), headers=headers)
        dic = json.loads(r.content.decode('utf-8', 'replace'))
        print('great!!!!!')
        # deal with login info
        itchat.utils.emoji_formatter(dic['User'], 'NickName')
        loginInfo['InviteStartCount'] = int(dic['InviteStartCount'])
        loginInfo['User'] = dic['User']
        loginInfo['SyncKey'] = dic['SyncKey']
        loginInfo['cookieJar'] = self.requests.cookies.get_dict()
        loginInfo['synckey'] = '|'.join(['%s_%s' % (item['Key'], item['Val'])
            for item in dic['SyncKey']['List']])
        return loginInfo

    def process_login_info(self, loginContent, uuid):
        ''' when finish login (scanning qrcode)
        * syncUrl and fileUploadingUrl will be fetched
        * deviceid and msgid will be generated
        * skey, wxsid, wxuin, pass_ticket will be fetched
        '''
        loginInfo = {}
        loginInfo['BaseRequest'] = {}
        loginInfo['uuid'] = uuid
        regx = r'window.redirect_uri="(\S+)";'
        loginInfo['url'] = re.search(regx, loginContent).group(1)
        headers = { 'User-Agent' : config.USER_AGENT }
        r = self.requests.get(loginInfo['url'], headers=headers, allow_redirects=False)
        loginInfo['url'] = loginInfo['url'][:loginInfo['url'].rfind('/')]
        for indexUrl, detailedUrl in (
                ("wx2.qq.com"      , ("file.wx2.qq.com", "webpush.wx2.qq.com")),
                ("wx8.qq.com"      , ("file.wx8.qq.com", "webpush.wx8.qq.com")),
                ("qq.com"          , ("file.wx.qq.com", "webpush.wx.qq.com")),
                ("web2.wechat.com" , ("file.web2.wechat.com", "webpush.web2.wechat.com")),
                ("wechat.com"      , ("file.web.wechat.com", "webpush.web.wechat.com"))):
            fileUrl, syncUrl = ['https://%s/cgi-bin/mmwebwx-bin' % url for url in detailedUrl]
            if indexUrl in loginInfo['url']:
                loginInfo['fileUrl'], loginInfo['syncUrl'] = \
                    fileUrl, syncUrl
                break
        else:
            loginInfo['fileUrl'] = loginInfo['syncUrl'] = loginInfo['url']
            loginInfo['deviceid'] = 'e' + repr(random.random())[2:17]
            loginInfo['BaseRequest'] = {}
        for node in xml.dom.minidom.parseString(r.text).documentElement.childNodes:
            if node.nodeName == 'skey':
                loginInfo['skey'] = loginInfo['BaseRequest']['Skey'] = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                loginInfo['wxsid'] = loginInfo['BaseRequest']['Sid'] = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                loginInfo['wxuin'] = loginInfo['BaseRequest']['Uin'] = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                loginInfo['pass_ticket'] = loginInfo['BaseRequest']['DeviceID'] = node.childNodes[0].data
        if not all([key in loginInfo for key in ('skey', 'wxsid', 'wxuin', 'pass_ticket')]):
            print('Your wechat account may be LIMITED to log in WEB wechat, error info:\n%s' % r.text)
            return False
        loginInfo = self.web_init(loginInfo)
        savedLoginInfo = self.save_login_info(loginInfo)
        return savedLoginInfo