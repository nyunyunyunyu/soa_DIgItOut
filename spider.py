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
import sys

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

def impRe(target):
    info_dict = {}
    pattern = u'昵称:([^\|]*)\|'
    m = re.search(pattern,target)
    if m:
        info_dict['name'] = m.group(1)

    pattern = u'性别:([^\|])'
    m = re.search(pattern,target)
    if m:
        info_dict['sex'] = m.group(1)

    pattern = u'地区:([^\|]*)'
    m = re.search(pattern,target)
    if m:
        info_dict['hometown'] = m.group(1)
    return info_dict

def get_info(inputid):
    time_now = int(time.time())
    inputUrl = home_page + inputid + info_page
    print inputUrl
    tmpContent = get_content(inputUrl)
    soup = BeautifulSoup(tmpContent.text, "html.parser")
    # time.sleep(1)
    divlabel = soup.find_all('div','tip')
    personalInfo = divlabel[0].next_sibling.get_text('|',strip=True)
    schoolInfo = divlabel[1].next_sibling.get_text()
    info_dict = impRe(personalInfo)
    # get_weibo(inputid)
    return info_dict

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
        if 'card_group' not in s['cards'][0]:
            continue
        weibo_list = [k['mblog'] for k in s['cards'][0]['card_group']]
        for weibo in weibo_list:
            my_weibo = {}
            # showjson(weibo, 0)
            # text
            if 'text' in weibo:
                my_weibo['text'] = weibo['text']
            # mobile phone
            if 'source' in weibo:
                my_weibo['source'] = weibo['source']
            # pics
            # if 'pics' in weibo:
            #     my_weibo['pics_url'] = [pics['url'] for pics in weibo['pics']]
                # print weibo['pics'][0]['url']
            if 'url_struct' in weibo:
                if weibo['url_struct'][0]['url_type'] == 36:
                    my_weibo['location'] = weibo['url_struct'][0]['url_title']
            if 'created_at' in weibo:
                my_weibo['created_at'] = weibo['created_at']
            if 'thumbnail_pic' in weibo:
                my_weibo['thumbnail_pic'] = weibo['thumbnail_pic']
            if 'bmiddle_pic' in weibo:
                my_weibo['bmiddle_pic'] = weibo['bmiddle_pic']
            if 'original_pic' in weibo:
                my_weibo['original_pic'] = weibo['original_pic']
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

def spider(inputid):
    return {'info_dict':get_info(inputid), 'weibo_list':get_weibo(inputid)}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python spider.py <uid>"
        exit
    print "spider test begin ~~"
    print "----------"
    my_weibo_list = spider(sys.argv[1])
    showjson(my_weibo_list,0)