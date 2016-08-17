#!/usr/bin/env python
# coding=utf-8

import os
import requests
import re
import time
import xml.dom.minidom
import json
import sys
import math
import subprocess
import ssl
import threading


DEBUG = True

if DEBUG == True: 
    import pdb 


MAX_GROUP_NUM = 35 # 每组人数

QRImagePath = os.getcwd() + '/qrcode.jpg'

tip = 0
uuid = ''

base_uri = ''

redirect_uri = ''

skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
deviceId = 'e' + repr(random.random())[2:17]

BaseRequest = {}

ContactList = []
My = []

def getUUID():
    global uuid
    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'lang': 'zh_CN',
        '_': int(time.time()*1000),
    }

    r= myRequests.get(url=url, params=params)
    r.encoding = 'utf-8'
    data = r.text

    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
    pm = re.search(regx, data)
    code = pm.group(1)
    uuid = pm.group(2)

    if code == '200':
        return True

    return False

def showQRImage():
    global tip
    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
    't': 'webwx',
    '_': int(time.time()*1000),
    }

    r= myRequests.get(url=url, params=params)

    tip = 1
    f = open(QRImagePath, 'wb')
    f.write(r.content)
    f.close()

    if sys.platform.find('darwin') >= 0:
        os.system('open %s' % QRImagePath)
    elif sys.platform.find('linux') >= 0:
        os.system('xdg-open %s' % QRImagePath)
    else:
        os.system('call %s' % QRImagePath)

    print('请使用微信扫描二维码以登录')

def waitForLogin():
    global tip, base_uri, redirect_uri
    url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (tip, uuid, int(time.time()*1000))
    r= myRequests.get(url=url)
    r.encoding = 'utf-8'
    data = r.text

    regx = r'window.code=(\d+);'
    pm = re.search(regx, data)

    code = pm.group(1)

    if code == '201': #已扫描
        print('成功扫描,请在手机上点击确认以登录')
        tip = 0
    elif code == '200': #已登录
        print('正在登录...')
        regx = r'window.redirect_uri="(\S+?)";'
        pm = re.search(regx, data)
        redirect_uri = pm.group(1) + '&fun=new'
        base_uri = redirect_uri[:redirect_uri.rfind('/')]
    elif code == '408': #超时
        pass

    return code


def login():
    global skey, wxsid, wxuin, pass_ticket, BaseRequest
    r= myRequests.get(url=redirect_uri)
    r.encoding = 'utf-8'
    data = r.text

    if DEBUG == True:
        f = open(os.getcwd() + '/login.json', 'w')
        f.write(str(data))
        f.close()

    doc = xml.dom.minidom.parseString(data)
    root = doc.documentElement

    for node in root.childNodes:
        if node.nodeName == 'skey':
            skey = node.childNodes[0].data
        elif node.nodeName == 'wxsid':
            wxsid = node.childNodes[0].data
        elif node.nodeName == 'wxuin':
            wxuin = node.childNodes[0].data
        elif node.nodeName == 'pass_ticket':
            pass_ticket = node.childNodes[0].data
    
    if skey == '' or wxsid == '' or wxuin == '' or pass_ticket == '':
        return False

    BaseRequest = {
    'Uin': int(wxuin),
    'Sid': wxsid,
    'Skey': skey,
    'DeviceID': deviceId,
    }

    return True

def webwxinit():
    url = (base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time()*1000) ) )
    params  = {'BaseRequest': BaseRequest }
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url, data=json.dumps(params),headers=headers)
    r.encoding = 'utf-8'
    data = r.json()


    if DEBUG == True:
        f = open(os.getcwd() + '/webwxinit.json', 'w')
        f.write(str({"url":url})+str({"params":params})+str(data))
        f.close()

    global ContactList, My
    dic = data
    ContactList = dic['ContactList']
    My = dic['User']
    ErrMsg = dic['BaseResponse']['ErrMsg']
    if len(ErrMsg) > 0:
        print(ErrMsg)

    Ret = dic['BaseResponse']['Ret']
    if Ret != 0:
        return False

    return True


def webwxgetcontact():
    url = (base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time()*1000) ) )
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url,headers=headers)
    r.encoding = 'utf-8'
    data = r.json()

    if DEBUG == True:
        #pdb.set_trace()
        f = open(os.getcwd() + '/webwxgetcontact.json', 'w')
        f.write(str({"url":url})+str(data))
        f.close()

    dic = data
    MemberList = dic['MemberList']
    # 倒序遍历,不然删除的时候出问题..
    SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage', 'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp', 'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin', 'weixin', 'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'officialaccounts', 'notification_messages', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm', 'notification_messages']
    for i in range(len(MemberList) - 1, -1, -1):
        Member = MemberList[i]
        if Member['VerifyFlag'] & 8 != 0: # 公众号/服务号
            MemberList.remove(Member)
        elif Member['UserName'] in SpecialUsers: # 特殊账号
            MemberList.remove(Member)
        elif Member['UserName'].find('@@') != -1: # 群聊
            MemberList.remove(Member)
        elif Member['UserName'] == My['UserName']: # 自己
            MemberList.remove(Member)

    return MemberList

def createChatroom(UserNames):
    MemberList = []
    for UserName in UserNames:
        MemberList.append({'UserName': UserName})

    #https://wx.qq.com/cgi-bin/mmwebwx-bin/
    url = base_uri + '/webwxcreatechatroom?r=%s&pass_ticket=%s' % (int(time.time()*1000),pass_ticket)
    headers = {'content-type': 'application/json; charset=UTF-8'}
    params = {
    'BaseRequest': BaseRequest,
    'MemberCount': len(MemberList),
    'MemberList': MemberList,
    'Topic': '',
    }

    r = myRequests.post(url=url,headers=headers,params=json.dumps(params))
    r.encoding = 'utf-8'
    data = r.json()

    if DEBUG == True:
        #pdb.set_trace()
        f = open(os.getcwd() + '/createChatroom.json', 'w')
        f.write(str({"url":url})+str({"params":params})+str(data))
        f.close()

    dic = data
    ChatRoomName = dic['ChatRoomName']
    MemberList = dic['MemberList']
    DeletedList = []
    for Member in MemberList:
        if Member['MemberStatus'] == 4: #被对方删除了
            DeletedList.append(Member['UserName'])

    ErrMsg = dic['BaseResponse']['ErrMsg']
    if len(ErrMsg) > 0:
        print(ErrMsg)

    return (ChatRoomName, DeletedList)

def deleteMember(ChatRoomName, UserNames):
    url = base_uri + '/webwxupdatechatroom?fun=delmember&pass_ticket=%s' % (pass_ticket)
    headers = {'content-type': 'application/json; charset=UTF-8'}
    params = {
    'BaseRequest': BaseRequest,
    'ChatRoomName': ChatRoomName,
    'DelMemberList': UserNames,
    }

    r = myRequests.post(url=url,params=json.dumps(params),headers=headers)
    r.encoding = 'utf-8'
    data = r.json()

    if DEBUG == True:
        #pdb.set_trace()
        f = open(os.getcwd() + '/webwxupdatechatroom.json', 'w')
        f.write(str({"url":url})+str({"params":params})+str(data))
        f.close()

    dic = data
    ErrMsg = dic['BaseResponse']['ErrMsg']
    if len(ErrMsg) > 0:
        print(ErrMsg)

    Ret = dic['BaseResponse']['Ret']
    if Ret != 0:
        return False

    return True

def addMember(ChatRoomName, UserNames):
    url = base_uri + '/webwxupdatechatroom?fun=addmember&pass_ticket=%s' % (pass_ticket)
    headers = {'content-type': 'application/json; charset=UTF-8'}
    params = {
    'BaseRequest': BaseRequest,
    'ChatRoomName': ChatRoomName,
    'AddMemberList': UserNames,
    }

    r = myRequests.post(url=url,params=json.dumps(params),headers=headers)
    r.encoding = 'utf-8'
    data = r.json()

    if DEBUG == True:
        #pdb.set_trace()
        f = open(os.getcwd() + '/addMember.json', 'w')
        f.write(str({"url":url})+str({"params":params})+str(data))
        f.close()

    dic = data
    MemberList = dic['MemberList']
    DeletedList = []
    for Member in MemberList:
        if Member['MemberStatus'] == 4: #被对方删除了
            DeletedList.append(Member['UserName'])

    ErrMsg = dic['BaseResponse']['ErrMsg']
    if len(ErrMsg) > 0:
        print(ErrMsg)

    return DeletedList

def main():
    global myRequests
    
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}
    myRequests = requests.Session()
    myRequests.headers.update(headers)

    if getUUID() == False:
        print('获取uuid失败')
        return

    showQRImage()
    time.sleep(1)

    while waitForLogin() != '200':
        pass

    os.remove(QRImagePath)

    if login() == False:
        print('登录失败')
        return

    if webwxinit() == False:
        print('初始化失败')
        return

    MemberList = webwxgetcontact()

    MemberCount = len(MemberList)
    print('通讯录共%s位好友' % MemberCount)

    ChatRoomName = ''
    result = []
    
    for i in range(0, int(math.ceil(MemberCount / float(MAX_GROUP_NUM)))):
        
        UserNames = []
        NickNames = []
        DeletedList = ''
        for j in range(0, MAX_GROUP_NUM):
            if i * MAX_GROUP_NUM + j >= MemberCount:
                break

            Member = MemberList[i * MAX_GROUP_NUM + j]
            UserNames.append(Member['UserName'])
            NickNames.append(Member['NickName'])
    
        print('第%s组...' % (i + 1))
        print(NickNames)
        print ('回车键继续...')
    
        # 新建群组/添加成员
        if ChatRoomName == '':
            (ChatRoomName, DeletedList) = createChatroom(UserNames)
        else:
            DeletedList = addMember(ChatRoomName, UserNames)

        DeletedCount = len(DeletedList)
        if DeletedCount > 0:
            result += DeletedList

        print('找到%s个被删好友' % DeletedCount)
        input()

        # 删除成员
        #deleteMember(ChatRoomName, UserNames)
        # todo 删除群组

    resultNames = []
    for Member in MemberList:
        if Member['UserName'] in result:
            NickName = Member['NickName']
            if Member['RemarkName'] != '':
                NickName += '(%s)' % Member['RemarkName']

            resultNames.append(NickName.encode('utf-8'))

    print('---------- 被删除的好友列表 ----------')
    print(resultNames)
    print('-----------------------------------')

# windows下编码问题修复
class UnicodeStreamFilter: 
    def __init__(self, target): 
        self.target = target 
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding 
    
    def write(self, s): 
        if type(s) == str: 
            s = s.decode('utf-8') 
            s = s.encode(self.encode_to, self.errors).decode(self.encode_to) 
            self.target.write(s) 


if sys.stdout.encoding == 'cp936': 
        sys.stdout = UnicodeStreamFilter(sys.stdout)

if __name__ == '__main__' :
    print('本程序的查询结果可能会引起一些心理上的不适,请小心使用...')
    print('回车键继续...')
    main()
    print('回车键结束')