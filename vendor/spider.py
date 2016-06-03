# -*- coding:utf-8 -*-
import time
import re
import json
import sys

import requests
from bs4 import BeautifulSoup
import pymongo

import image_detect
import constant



def showjson(s, count):
    ss = '----'
    sss = '****'
    if not isinstance(s, dict) and not isinstance(s, list):
        print ss * count, s
    if isinstance(s, dict):
        for key in s:
            print sss * count, key
            showjson(s[key], count + 1)
    if isinstance(s, list):
        for i in s:
            showjson(i, count + 1)


class Spider:
    def updateCookie(self):
        cookie = "UOR=www.baidu.com,blog.sina.com.cn,; U_TRS1=000000ac.8d4336b2.566566a9.84409797; vjuids=-d91bc0168.1517c190932.0.c439402b; SGUID=1449485994499_40122227; SINAGLOBAL=59.66.131.172_1449485993.969333; Apache=59.66.131.245_1464931299.610667; ULV=1464931303353:77:5:5:59.66.131.245_1464931299.610667:1464931299687; vjlast=1464931307; lxlrtst=1464923568_o; lxlrttp=1464923568; sso_info=v02m4a4vZy2vaGZhqWnmpeRr52XkKWNg4GpnYals5yHoa2Lpo2vm5KZtY-WoaqRlKW3jIa5iJumqLWMpaGQlJahtpaWrYmdtISljLSQpYy0kKaat5i9jJDAwA==; SUB=_2AkMgDZVNdcNhrAZZkfwRzmzhZYlH-jzEiebBAn7tJhMyAhh77kwtqSWr62ki6J9TxNk2FWrrISuc5oFNjQ..; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WFSmMZEdn1kmBrdvnWgNJZF5JpV8NSaqgxD9cLXdNHXBsLXIPS7wsXVqcv_"
        self.cookdic = dict(Cookie=cookie)

    def __init__(self):
        self.cccccc = 1
        self.updateCookie()
        self.client = pymongo.MongoClient(constant.MONGODB_HOST, constant.MONGODB_PORT)
        if (not 'soa' in self.client.database_names() or not 'weibo' in self.client['soa'].collection_names()):
            self.client['soa']['weibo'].create_index([('uid', pymongo.ASCENDING)], unique=True)

    def clear_cache(self):
        self.client['soa']['weibo'].remove()

    def get_content(self, toUrl):
        """ Return the content of given url
            Args:
                toUrl: aim url
                count: index of this connect
            Return:
                content if success
                'Fail' if fail
        """
        if(self.cccccc % 20 == 0):
            time.sleep(2)
            self.cccccc = 0
        try:
            req = requests.get(toUrl, cookies=self.cookdic, timeout=1)
            self.cccccc += 1
        except:
            return None
        if req.status_code != requests.codes.ok:
            print "haven't get 200, status_code is: " + str(req.status_code);
            sys.exit(-1)
        return req

    def get_weibo(self, inputid):
        time_now = int(time.time())
        # inputUrl = home_page + inputid +'/profile'
        inputUrl = 'http://m.weibo.cn/page/json?containerid=100505' + inputid + '_-_WEIBO_SECOND_PROFILE_WEIBO&page='
        tmpContent = self.get_content(inputUrl + '1')
        s = json.loads(tmpContent.text)
        # print a.keys()
        # showjson(s, 0)
        if 'maxPage' in s['cards'][0]:
            maxPage = s['cards'][0]['maxPage']
        else:
            maxPage = 1
        my_weibo_list = []
        for i in xrange(1, maxPage + 1):
            print "Page %d" % i
            tmp = self.get_content(inputUrl + str(i))
            if tmp is None:
                continue
            print tmp.text
            s = json.loads(tmp.text)

            if 'card_group' not in s['cards'][0]:
                continue
            # print s
            # weibo_list = [k['mblog'] for k in s['cards'][0]['card_group']]
            weibo_list = []

            for k in s['cards'][0]['card_group']:
                if 'mblog' in k:
                    weibo_list.append(k['mblog'])
            print 'len(weibo_list)', len(weibo_list)
            for weibo in weibo_list:
                my_weibo = {}
                # showjson(weibo, 0)
                # text

                if 'text' in weibo:
                    my_weibo['text'] = weibo['text']
                # mobile phone
                if 'source' in weibo:
                    my_weibo['source'] = weibo['source']
                if 'url_struct' in weibo:
                    if weibo['url_struct'][0]['url_type'] == 36:
                        # showjson(weibo['url_struct'],0)
                        # print weibo['url_struct'][0]['short_url']
                        content = self.get_content(weibo['url_struct'][0]['short_url'])
                        if content:
                            short_url_data = content.text
                            pattern = u'location.replace\("([^"]*)"\)'
                            url_data = short_url_data
                            # 地址数据
                            pattern = u'poiid=([^\&]*)\&amp'
                            mm = re.search(pattern, url_data)
                            if mm:
                                print "type 1 ok"
                                # print mm.group(1)
                                    # print mm.group(1)
                                # print url_data
                                my_weibo['location_name'] = weibo['url_struct'][0]['url_title']
                                [lon,lat] = mm.group(1).split('_')
                                my_weibo['location_lon'] = lon
                                my_weibo['location_lat'] = lat
                                # print my_weibo['location']
                                # <src="http://place.weibo.com/index.php?_p=place_page&amp;_a=poi_map_right&amp;poiid=1013247614"
                                # poiObject.lon = 116.307620521;
                                # poiObject.lat = 39.9841806635;
                            else:
                                # print 'checkin'
                                # print url_data
                                pattern = u'poiid=([^\']*)\''
                                mmm = re.search(pattern, url_data)
                                if mmm:
                                    # print mmm.group(1)
                                    placeid = mmm.group(1)
                                    print 'type 2 ok2'
                                    url = "http://place.weibo.com/index.php?_p=place_page&_a=poi_map_right&poiid="+placeid
                                    # newcookiedic = login.getCookies([{'no':username, 'psw':password}])[0]
                                    content = self.get_content(url)
                                    if content:
                                        # print '*'*100
                                        # print content.text
                                        p1 = u'poiObject.lon = ([^;]*);'
                                        m1 = re.search(p1, content.text)
                                        p2 = u'poiObject.lat = ([^;]*);'
                                        m2 = re.search(p2, content.text)
                                        if m1 and m2:
                                            lon = m1.group(1)
                                            lat = m2.group(1)
                                            my_weibo['location_name'] = weibo['url_struct'][0]['url_title']
                                            my_weibo['location_lon'] = lon
                                            my_weibo['location_lat'] = lat
                if 'created_at' in weibo:
                    my_weibo['created_at'] = weibo['created_at']
                thumbnail_url = 'http://ww1.sinaimg.cn/thumbnail/'
                bmiddle_url = 'http://ww1.sinaimg.cn/bmiddle/'
                original_url = 'http://ww1.sinaimg.cn/large/'
                if 'pics' in weibo:
                    pics_list = []
                    for pic in weibo['pics']:
                        pics_list.append({'thumbnail_pic':thumbnail_url+pic['pid'], 'bmiddle_pic':bmiddle_url+pic['pid'], 'original_pic':original_url+pic['pid']})
                    my_weibo['pics'] = pics_list
                # if 'thumbnail_pic' in weibo:
                #     my_weibo['thumbnail_pic'] = weibo['thumbnail_pic']
                # if 'bmiddle_pic' in weibo:
                #     my_weibo['bmiddle_pic'] = weibo['bmiddle_pic']
                # if 'original_pic' in weibo:
                #     my_weibo['original_pic'] = weibo['original_pic']
                my_weibo_list.append(my_weibo)

        showjson(my_weibo_list, 0)
        return my_weibo_list

    def get_info(self, inputid):
        res=requests.get('https://api.weibo.com/2/users/show.json',
                         params={'source': constant.WEIBO_API_KEY, 'uid': inputid},
                         cookies=self.cookdic)
        info_dict = json.loads(res.text)
        # get_weibo(inputid)
        return info_dict

    def get_result(self, inputid):
        return {'uid': inputid, 'updated_at': time.time(), 'weibo_list': self.get_weibo(inputid),
                        'info_dict': self.get_info(inputid),}

    def username_to_uid(self, username):
        res=requests.get('https://api.weibo.com/2/users/show.json',
                         params={'source': constant.WEIBO_API_KEY, 'screen_name': username},
                         cookies=self.cookdic)
        return json.loads(res.text)['idstr']

    def crawl(self, inputid):
        # 'info_dict':get_info(inputid),
        # cookdic = login.getCookies([{'no':username, 'psw':password}])[0]
        if not constant.CACHE_ENABLE:
            return True, self.get_result(inputid)
        find_row = self.client['soa']['weibo'].find_one({'uid': inputid})
        if (find_row):
            weibo_len = len(find_row['weibo_list'])
            days = (time.time() - find_row['updated_at']) / (60 * 60 * 24)
            if(len <= 50 or days > 14):
                res = self.get_result(inputid)
                self.client['soa']['weibo'].replace_one({'uid':inputid}, res)
                return True, res
            else:
                return False, find_row
        else:
            res = self.get_result(inputid)
            self.client['soa']['weibo'].insert_one(res)
            return True, res

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python spider.py <uid>"
        exit()
    print "spider test begin ~~"
    print "----------"
    my_spider = Spider()
    latest, my_weibo_list = my_spider.crawl(sys.argv[1])
    image_detect.get_grouping_result(my_weibo_list, latest)
    # showjson(my_weibo_list,0)

    # wd = open('./website/static/my_weibo_list.json', 'w')
    # wd.write(json.dumps(my_weibo_list))
    # wd.close()
    print len(my_weibo_list['weibo_list'])

    print 'done...'
