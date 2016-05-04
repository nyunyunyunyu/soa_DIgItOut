#-*- coding:utf-8 -*-
from constant import *
import requests
import gzip
import StringIO
import sys
from bs4 import BeautifulSoup
import time
import re
import json

def get_content(toUrl):
    """ Return the content of given url
        Args:
            toUrl: aim url
            count: index of this connect
        Return:
            content if success
            'Fail' if fail
    """

    cookdic = dict(Cookie=cookie)

    try:
        req = requests.get(toUrl,cookies = cookdic, timeout=100)
    except:
        return None
    if req.status_code != requests.codes.ok:
        print "haven't get 200, status_code is: "+str(req.status_code);
        sys.exit(-1)
    return req

def get_weibo(inputid):
    time_now = int(time.time())
    # inputUrl = home_page + inputid +'/profile'
    inputUrl = 'http://m.weibo.cn/page/json?containerid=100505'+inputid+'_-_WEIBO_SECOND_PROFILE_WEIBO&page='
    tmpContent = get_content(inputUrl+'1')
    s = json.loads(tmpContent.text)
        # print a.keys()
    # showjson(s, 0)
    if 'maxPage' in s['cards'][0]:
        maxPage = s['cards'][0]['maxPage']
    else:
        maxPage = 1
    my_weibo_list = []
    for i in xrange(1,maxPage+1):
        s = json.loads(get_content(inputUrl+str(i)).text)
        # showjson(s['cards'][0]['card_group'][0],0)
        # showjson(s['cards'][0]['card_group'][0]['mblog']['url_struct'][0]['url_title'],0)
        # showjson(s['cards'][0]['card_group'][0]['mblog']['url_struct'][0],0)
        weibo_list = [k['mblog'] for k in s['cards'][0]['card_group']]
        for weibo in weibo_list[0:10]:
            my_weibo = {}
            # showjson(weibo, 0)
            # text
            if 'text' in weibo:
                my_weibo['text'] = weibo['text']
            # mobile phone
            if 'source' in weibo:
                my_weibo['source'] = weibo['source']
            # pics
            if 'pics' in weibo:
                my_weibo['pics_url'] = [pics['url'] for pics in weibo['pics']]
                # print weibo['pics'][0]['url']
            if 'url_struct' in weibo:
                if weibo['url_struct'][0]['url_type'] == 36:
                    my_weibo['location'] = weibo['url_struct'][0]['url_title']
            if 'created_at' in weibo:
                my_weibo['created_at'] = weibo['created_at']
            my_weibo_list.append(my_weibo)
                    # my_weibo['url_type'] = weibo['url_struct'][0]['url_type']
    # showjson(my_weibo_list, 0)
    return my_weibo_list
        # for my_weibo in my_weibo_list:
        #     print my_weibo
            


def showjson(s, count):
    ss = '----'
    sss = '****'
    if not isinstance(s, dict) and not isinstance(s, list):
        print ss*count, s
    if isinstance(s, dict):
        for key in s:
            print sss*count, key
            showjson(s[key], count+1)
    if isinstance(s, list):
        for i in s:
            showjson(i, count+1)

def spider(inputid = '5677086105'):
    return get_weibo(inputid)


if __name__ == "__main__":
    print "spider test begin ~~"
    print "----------"
    my_weibo_list = spider()
    showjson(my_weibo_list,0)