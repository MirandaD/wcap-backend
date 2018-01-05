from . import DB

class Massager():
    def __init__():
        self.db = DB()
    def get_msg(self, uuid):
        loginInfo = self.db.get_login_info_by_uuid(uuid)
        url = '%s/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (
        self.loginInfo['url'], self.loginInfo['wxsid'],
        self.loginInfo['skey'],self.loginInfo['pass_ticket'])
        data = {
            'BaseRequest' : self.loginInfo['BaseRequest'],
            'SyncKey'     : self.loginInfo['SyncKey'],
            'rr'          : ~int(time.time()), }
        headers = {
            'ContentType': 'application/json; charset=UTF-8',
            'User-Agent' : config.USER_AGENT }
        r = self.s.post(url, data=json.dumps(data), headers=headers, timeout=config.TIMEOUT)
        dic = json.loads(r.content.decode('utf-8', 'replace'))
        if dic['BaseResponse']['Ret'] != 0: return None, None
        self.loginInfo['SyncKey'] = dic['SyncCheckKey']
        self.loginInfo['synckey'] = '|'.join(['%s_%s' % (item['Key'], item['Val'])
            for item in dic['SyncCheckKey']['List']])
        return dic['AddMsgList'], dic['ModContactList']