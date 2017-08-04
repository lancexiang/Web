# -*- coding: utf-8 -*-
"""
Created on 2017/7/18 19:10

@author: luoxiang
"""

import web
import requests
import json
import time
url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'

def getFaceInfo(image_url):
    data = {
        'api_key':'D-vqzVO92D4QAbpRq0C24mxBRBZtHebF',
        'api_secret':'OwqHoziHWJORmR3rqlhZ9865Rn7u0WCd',
        'image_url':image_url,
        'return_attributes':'gender,age,smiling,emotion'
    }
    html = requests.post(url,data=data).content.decode('utf-8')
    html = json.loads(html)
    gender = html['faces'][0]['attributes']['gender']['value']
    age = html['faces'][0]['attributes']['age']['value']
    smile = html['faces'][0]['attributes']['smile']['value']
    emotion = html['faces'][0]['attributes']['emotion']
    return gender,age,smile,emotion
#路由
urls = (
    '/','Index',
)
render = web.template.render('templates')
class Index(object):
    def GET(self):
        #方法一，直接用open将前端网页呈现，但不好修改数据，几乎已被弃用
        # return open('templates/index.html').read()
        # 方法二，用集成模板
        #应该是版本不兼容问题，web是python2的模块，本来应该会自动在index.html首部添加$ def with(imgurl="static/images/zjl.jpg")
        #和相关img标签内自动改为src="$:imgurl"，python3中使用web模块则未出现此种变化，需手动添加
        return render.index()
    def POST(self):
        faceInfo = ('Male', 30, 2.766,{'disgust': 0.182, 'anger': 0.053, 'neutral': 70.665, 'sadness': 27.433, 'happiness': 0.177,'fear': 1.337, 'surprise': 0.153})
        text = 'Gender:{}<br>Age:{}<br>Smile:{}<br>Emotion:{}'.format(*faceInfo)
        return text
        #因为我没有服务器，此处只能显示默认值了, 所以上传文件的功能没有做好
        # input = web.input()#获取请求数据
        # img_path = input.get('path',None)# input是一个字典，如果是路径则它有path值
        # if img_path != None:
        #     # 表示是网址，而不是上传文件
        #     # path = 'your_sever/{}'.format(img_path)
        #     # faceInfo = getFaceInfo(path)
        #     faceInfo = ('Male', 30, 2.766, {'disgust': 0.182, 'anger': 0.053, 'neutral': 70.665, 'sadness': 27.433, 'happiness': 0.177, 'fear': 1.337, 'surprise': 0.153})
        #     text = 'Gender:{}<br>Age:{}<br>Smile:{}<br>Emotion:{}'.format(*faceInfo)
        #     return text
        # else:
        #     img_file = input.get('file')
        #     filepath = 'static/face_images/{}.jpg'.format(time.time())
        #     with open(filepath,'wb') as f:
        #         f.write(img_file)
        #     return render.index(filepath)
if __name__ == '__main__':
    web.application(urls,globals()).run()