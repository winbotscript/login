# -*- coding: utf-8 -*-
from linepy import *
from akad.ttypes import LoginRequest
import AuthService
from thrift.protocol import TCompactProtocol
from thrift.transport  import THttpClient
from datetime import datetime
import os.path
import requests, os, sys, json

line = LINE('u4065ccdd5d00682951a70115d51c3321:aWF0OiAxNTUzMjMzNjExMjU2Cg==..7rdkseFptNs1TH+HmlP60p2LAM8=',systemName='iPhone OS',appName='IOS\t10.4.2\tiPhone OS\t13.2.2')
line.log("Auth Token : " + str(line.authToken))
class LineNotify:
    def __init__(self, access_token, name=None):
        self.name = name
        self.accessToken = access_token

        if access_token:
            self.enable = True
            self.headers = {"Authorization": "Bearer " + access_token}
        else:
            self.enable = False
            self.headers = {}

    def on(self):
        self.enable = True

    def off(self):
        self.enable = False

    def format(self, message):
        if self.name:
            message = '[{0}] {1}'.format(self.name, message)

        return message

    def send(self, message, image_path=None, sticker_id=None, package_id=None):
        if not self.enable:
            return
        files = {}
        params = {"message": self.format(message)}
        if image_path and os.path.isfile(image_path):
            files = {"imageFile": open(image_path, "rb")}
        if sticker_id and package_id:
            params = {**params, "stickerId": sticker_id, "stickerPackageId": package_id}
        requests.post("https://notify-api.line.me/api/notify", headers=self.headers, params=params, files=files)

oepoll = OEPoll(line)
kontol = LineNotify('x1hbak83TsSv6TyKwudzsLX3ZCJC3jggWJpivHVAnJI')
def get_connect(path,service=None,headers=None):
        if(headers is not None):
            headers.update({"x-lpqs" : path})

        sport = THttpClient.THttpClient('https://gwx.line.naver.jp'+path)
        sport.setCustomHeaders(headers)
        ebot = service(TCompactProtocol.TCompactProtocol(sport))
        return ebot

def get_token(system_name="",header=None):
        Qr = get_connect('/api/v4/TalkService.do',service=AuthService.Client,headers=header)
        qr = Qr.getAuthQrcode(True, system_name, True)
        kontol.send(qr.callbackUrl)
        header.update({'X-Line-Access':qr.verifier})
        getAccessKey = json.loads(requests.session().get('https://gwx.line.naver.jp/Q', headers=header).text)
        QR = get_connect('/api/v4p/rs',service=AuthService.Client,headers=header)
        req = LoginRequest()
        req.type = 1
        req.identityProvider = 1
        req.keepLoggedIn = True
        req.accessLocation = "8.8.8.8"
        req.systemName = system_name
        req.verifier =  qr.verifier
        req.e2eeVersion = 1
        res = QR.loginZ(req)
        ret = " Get token dul "
        ret += "\n- AppName: {}".format(header['X-Line-Application'])
        ret += "\n- authToken: {}".format(res.authToken)
        return ret

def RECEIVE_MESSAGE(op):
    msg = op.message
    text = msg.text
    msg_id = msg.id
    receiver = msg.to
    sender = msg._from
    if msg.contentType == 0:
        if msg.toType == 2:
            if str(text).lower() == '.test':
                kontol.send('\nyes bos')
            if str(text).lower() == '.rebot':
                kontol.send('\nyes bos rebooooooot')
                python3 = sys.executable
                os.execl(python3, python3, *sys.argv)
            if str(text).lower() == 'gettoken':
                try:
                    header = {'User-Agent': "Line/10.4.2 iPad4,1 9.3.3",'X-Line-Application': "IOSIPAD 10.4.2 iPhone OS 13.2.2","x-lal" : "ja-US_US"}
                    a = get_token(system_name="iPhone OS",header=header)
                    kontol.send(str(a))
                except:pass

def NOTIFIED_INVITE_INTO_GROUP(op):
    if op.param3 in line.getProfile().mid:
        line.acceptGroupInvitation(op.param1)

oepoll.addOpInterruptWithDict({
    OpType.RECEIVE_MESSAGE: RECEIVE_MESSAGE
})
oepoll.addOpInterruptWithDict({
    OpType.NOTIFIED_INVITE_INTO_GROUP: NOTIFIED_INVITE_INTO_GROUP
})

while True:
    oepoll.trace()
