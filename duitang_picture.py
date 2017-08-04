# -*- coding: utf-8 -*-
"""
Created on 2017/7/18 15:04

@author: luoxiang
"""
import requests
import urllib.parse
import threading
import os
# set the maximum thread rock, otherwise the CPU will red or system halted
thread_lock = threading.BoundedSemaphore(value=10)

class Spider(object):
    def __init__(self, url):
        self.url = url

    def get_page(self, url):
        page = requests.get(url)
        page = page.content.decode('utf-8')
        # the return of content is bytes, decode it to str
        return page

    def pages_from_duitang(self, kw):
        pages = []
        kw = urllib.parse.quote(kw)
        for index in range(0, 120, 24):
            u = self.url.format(kw,index)
            page = self.get_page(u)
            pages.append(page)
        return pages

    def findall_in_page(self, page, startpart, endpart):
        all_string = []
        end = 0
        while page.find(startpart, end) != -1:
            start = page.find(startpart, end) + len(startpart)
            end = page.find(endpart, start)
            string = page[start:end]
            all_string.append(string)
        return all_string

    def image_urls_from_pages(self,pages):
        image_urls = []
        for page in pages:
            urls = self.findall_in_page(page,'path":"','"')
            #extend不同与append直接加入一个列表，而是将新加入的列表合并在原列表的后面形成一个列表，相当于+=操作
            image_urls.extend(urls)
        return image_urls

    def download_images(self,path,url,num):
        response = requests.get(url)
        path = path + str(num) + '.jpg'
        with open(path,'wb') as f:
            f.write(response.content)
        #下载完成后解锁
        # print('第{}张图片下载完成'.format(num))
        thread_lock.release()

if __name__ == '__main__':
    url = 'https://www.duitang.com/napi/blog/list/by_search/?kw={}&start={}&limit=24'
    spider = Spider(url)
    kw = input('请输入想要爬取图片内容的关键字：')
    path = './images/' + kw + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    pages = spider.pages_from_duitang(kw)
    image_urls = spider.image_urls_from_pages(pages)
    num = 0
    for image_url in image_urls:
        num += 1
        print('正在下载第{}张图片...'.format(num))
        thread_lock.acquire()
        t = threading.Thread(target=spider.download_images,args=(path,image_url,num))
        t.start()
    print('完成下载120张图片')