# -*- coding: utf-8 -*-
"""
Created on 2017/4/1515:58

@author: luoxiang
"""

# -*- coding: utf-8 -*-
"""
Created on 2017/4/1514:54

@author: luoxiang
"""
import http.cookiejar as cookielib
import urllib.parse as parse
import urllib.request as request
import hashlib
import getpass
from bs4 import BeautifulSoup

class ruisi(object):
    def __init__(self,username,password):
        self.loginurl = 'http://rs.xidian.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'#登录界面提交数据的request
        self.mainurl = 'http://rs.xidian.edu.cn/portal.php'
        self.signurl = 'http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1'#签到提交数据的页面
        self.goldurl = 'http://rs.xidian.edu.cn/home.php?mod=spacecp&ac=credit&showcredit=1'
        self.postdata = parse.urlencode({'username':username,
                                         'password':password,# md5 value
                                         'quickforward':'yes',
                                         'handlekey':'ls'
                                        }).encode('utf-8')
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
        self.cookies = cookielib.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cookies))#构造带有cookies的opener用于打开登录后的页面

    def login(self):
        req = request.Request(url=self.loginurl,data=self.postdata,headers=self.headers)
        res = self.opener.open(req)
        html = self.opener.open(self.mainurl).read().decode('utf-8')
        self.obj = BeautifulSoup(html,'lxml')
        if self.obj.find(attrs={'target': "_blank", 'title': "访问我的空间"}).string == '我心尧摆':
            return True
        else:
            return False

    def sign(self):
        formhash = self.obj.find(attrs={'name':'formhash'})['value']
        postdata = parse.urlencode({'formhash':formhash,
                                    'qdxq':'kx',
                                    'qdmode':'1',
                                    "todaysay":"a happday'",
                                    'fastreply':'0'}).encode('utf-8')
        req = request.Request(url=self.signurl,data=postdata,headers=self.headers)
        res = self.opener.open(req)

    def getgold(self):
        req = request.Request(self.goldurl)
        html = self.opener.open(req)
        html = BeautifulSoup(html,'lxml')
        gold = html.find(name='li',attrs={'class':'xi1 cl'})
        return gold

if __name__ == '__main__':
    username = input('请输入睿思用户ID:')
    password = getpass.getpass('请输入睿思用户密码:')
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    password = md5.hexdigest()
    user = ruisi(username,password)
    # this is a bug i find occasionaly, ^*^
    times = int(input('请输入要签到的次数:'))
    print('预计可获得金币:%d~%d'%(times*1,times*15))
    if user.login():
        for i in range(times):
            user.sign()
        print('签到完成')
    else:
        print('登录失败,请检查用户和密码是否正确后重新尝试...')