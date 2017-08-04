# -*- coding: utf-8 -*-
"""
Created on 2017/4/1514:54

@author: luoxiang
"""

import xlwt
import sqlite3
from bs4 import BeautifulSoup
import requests

class Spider(object):
    def __init__(self):
        self.logurl = 'http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fjwxt.xidian.edu.cn%2Fcaslogin.jsp'
        self.gradeurl = 'http://jwxt.xidian.edu.cn/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2016-2017%D1%A7%C4%EA%B5%DA%D2%BB%D1%A7%C6%DA(%C1%BD%D1%A7%C6%DA)'
        self.session = requests.Session()

    def login(self,username,password):
        html = self.session.get(self.logurl)
        bsObj = BeautifulSoup(html.text, 'lxml')
        lt_value = bsObj.find(attrs={"name": "lt"})['value']
        exe_value = bsObj.find(attrs={"name": "execution"})['value']
        postdatas = {'username': username,
                     'password': password,
                     'submit': '',
                     'lt': lt_value,
                     'execution': exe_value,
                     '_eventId': 'submit',
                     'rmShown': '1'}
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0"}
        req = self.session.post(url = self.logurl,data=postdatas,headers=headers)
        res = self.session.get(self.logurl)
        bsObj = BeautifulSoup(res.text,'lxml')
        if bsObj.title.string.strip() == '学分制综合教务':
            # keyword after login
            print('登录成功,正在查询成绩...')
            return True
        elif bsObj.title.string.strip() == '统一身份认证平台':
            print('用户名或密码错误，请重新输入！')
            return False
        elif bsObj.title.string.strip() == '错误信息':
            print('数据库忙，正在为你重新登录...')
            self.session = requests.Session()
            return self.login(username,password)
        else:
            print('未知错误')

    def store_into_database(self):
        # store grade to database
        print('正在写入成绩...')
        conn = sqlite3.connect('grade.db')
        c = conn.cursor()#游标变量，不是很懂，感觉和C语言读写文件的指针类似，会随着动作而移动到动作处
        html = self.session.get(self.gradeurl)
        bsObj = BeautifulSoup(html.text,'lxml')
        datas = bsObj.find_all(name='table', attrs={'class': 'titleTop2'})#这个类标签包含了所有学期的成绩
        for i,seme in enumerate(datas):
            ths = seme.find_all('th')
            title = []
            for ith,th in enumerate(ths):
                th = th.string.strip()
                if th == '学分' or th == '成绩':
                    title.append(th + ' real')
                else:
                    title.append(th + ' text')
            command = '''CREATE TABLE {0} ('''.format('table' + str(i+1))
            for ith,th in enumerate(title):
                command += th
                if ith < len(title)-1:
                    command += ','
            command += ')'
            try:
                c.execute(command)
                conn.commit()
            except sqlite3.OperationalError as e:
                print(e)
                print(command)
                pass
            tds = seme.find_all('td', attrs={"align": "center"})
            grade = []
            num = 0
            for td in tds:
                if td.string:
                    if td.string.strip()!='':
                        grade.append("'" + td.string.strip() + "'")
                    else:
                        grade.append("' '")
                else:
                    grade.append("'" + td.find('p').string.strip() + "'")
                num += 1
                if num == len(ths):
                    command = '''INSERT INTO {0} VALUES ('''.format('table' + str(i+1))
                    for index,value in enumerate(grade):
                        command += value
                        if index < len(ths)-1:
                            command += ','
                    command += ')'
                    try:
                        c.execute(command)
                        conn.commit()
                    except sqlite3.OperationalError as e:
                        print(e)
                        print(command)
                        exit(-2)
                    num = 0
                    grade = []
        c.close()
        conn.close()
        print('写入成功')
        return True

    def store_into_xls(self):
        print('正在写入成绩...')
        file = xlwt.Workbook()
        table = file.add_sheet('grades', cell_overwrite_ok=True)
        def set_style(name, height, bold=False):
            style = xlwt.XFStyle()
            font = xlwt.Font()
            font.name = name  # 'Times New Roman'
            font.bold = bold
            font.color_index = 4
            font.height = height
            style.font = font
            return style
        row = 0
        html = self.session.get(self.gradeurl)
        bsObj = BeautifulSoup(html.text, "lxml")
        datas = bsObj.find_all("table", attrs={"class": "titleTop2"})
        for seme in datas:
            ths = seme.find_all('th')
            for col, th in enumerate(ths):
                # print(th.string.strip(), end='   ')
                table.write(row, col, th.string.strip(), set_style('Times New Roman', 220, True))
            row += 1
            subs = seme.findAll('td', attrs={"align": "center"})
            col_iter = 0
            len_ths = len(ths)
            for sub in subs:
                if sub.string:
                    # print(sub.string.strip(), end='   ')
                    table.write(row, col_iter, sub.string.strip())
                else:
                    # print(sub.find('p').string.strip(), end='   ')
                    table.write(row, col_iter, sub.find('p').string.strip())
                col_iter += 1
                if col_iter == len_ths:
                    # print('\n')
                    row += 1
                    col_iter = 0
            file.save('grade.xls')
        print('写入成功')
        return True

if __name__ == '__main__':
    spider = Spider()
    username = input('请输入学号:')
    password = input('请输入密码:')
    if spider.login(username, password):
        spider.store_into_xls()