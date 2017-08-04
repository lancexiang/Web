# -*- coding: utf-8 -*-
"""
Created on 2017/4/1215:18

@author: luoxiang
"""
import urllib.parse as parse
import urllib.request as request
import os
import re

class Spider(object):
    def __init__(self,word,number):
        urls =[]
        # for the reason of using XHR web technology, need store defferents url address
        word = ''.join(word.split(' '))#处理空格
        word = parse.quote(word)
        url = 'http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord={word}&cl=2' \
                   '&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word={word}&face=0&istype=2nc=1&pn={pn}&rn=30'
        for x in range(int(number)//30+1):
            urls.append(url.format(word=word,pn=x*30))
            # by analyzing，pn present the number of the first image，load 30 images per url in urls
        self.urls = urls

    def getpagehtmls(self):#打开urls中的各个url，并将其网页内容返回在htmls
        htmls = []
        for url in self.urls:
            req = request.Request(url)
            req.add_header('user-agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36')
            res = request.urlopen(req)
            html = res.read().decode('utf-8')
            htmls.append(html)
        return htmls

    def decode(self,url):
        # the address of baidu picture have been encrypted, and i find the decryption for it, as following:
        intab = "wkv1ju2it3hs4g5rq6fp7eo8dn9cm0bla"
        outtab = "abcdefghijklmnopqrstuvw1234567890"
        trantab = str.maketrans(intab, outtab)
        newurl = url.replace('_z2C$q',':').replace('_z&e3B','.').replace('AzdH3F','/')
        return newurl.translate(trantab)

    def getimageurls(self):
        imageurls = []
        pattern = re.compile(r'"objURL":"(.*?)"')
        for html in self.getpagehtmls():
            imageurl = re.findall(pattern,html)
            imageurls.append(imageurl)
        for item in imageurls:
            for index,value in enumerate(item):
                item[index] = self.decode(value)
        return imageurls

    def saveImg(self,path):
        # store image to disk orderly
        self.path = path
        path = path.strip()  # strip(rm)删除字符串头尾带rm的字符，默认空格为\n,\t,\r,''
        isexist = os.path.exists(path)
        if not isexist:
            os.mkdir(path)
        imageurls = self.getimageurls()
        for i in range(int(number)):
            filename = self.path + str(i+1) + '.jpg'
            req = request.Request(imageurls[i//30][i%29])
            req.add_header('user-agent',
                           'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36')
            try:
                res = request.urlopen(req)
            except request.HTTPError as e:
                if e.code == 404 or e.code == 403:
                    continue
            except request.URLError as e:
                if hasattr(e,'reason'):
                    continue
            with open(filename,'wb') as f:
                f.write(res.read())

if __name__ == '__main__':
    context = input('请输入要下载图片的内容：')
    number = input('请输入要下载图片的数量：')
    spider = Spider(context,number)
    spider.saveImg('./'+context+'/')