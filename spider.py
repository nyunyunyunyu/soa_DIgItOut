# -*- coding:utf-8 -*-
import constant
import requests
import gzip
import StringIO
import sys
from bs4 import BeautifulSoup
import time
import re
import json
import sys
import login
import pymongo
import image_detect


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
        cookie = "SINAGLOBAL=1235433884430.6768.1430467351374; wb_publish_vip_2243006675=1; wb_bub_hot_5894427394=1; YF-Page-G0=f70469e0b5607cacf38b47457e34254f; _s_tentry=-; Apache=8905100007286.064.1463722207724; ULV=1463722207739:24:3:2:8905100007286.064.1463722207724:1463500634206; YF-V5-G0=d45b2deaf680307fa1ec077ca90627d1; login_sid_t=79f68dfea5288dec7ccfc85f90279308; YF-Ugrow-G0=169004153682ef91866609488943c77f; WBStore=8ca40a3ef06ad7b2|undefined; WBtopGlobal_register_version=f81ab92b992b2688; un=soadigitout@itispxm.com; myuid=5894427394; UOR=,,login.sina.com.cn; SUS=SID-5894427394-1464667177-GZ-sqp28-ffc75c2bfc64a57aad9d045a74f6201c; SUE=es%3D00d6679771275c2e057bc0da1c13564e%26ev%3Dv1%26es2%3Dcbf7a97147067ee71f306224bb6ce004%26rs0%3DL70x13AZCaJVMXovpxuHvvlrpGEtQlesaaWFZDyNIUlYTGJa65LNJbN3twnw4H76k7RDYQAAUEFnFvNMoGjoEIJZaPiLKZ97tZMGs92OpiH3HrpV6NSc3ENRMqWuDScTgN8OQQeAt1qkM8AjQmNm%252BYU4HzHBYH9L%252B8NwFuWV%252FNs%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1464667177%26et%3D1464753577%26d%3Dc909%26i%3D201c%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26uid%3D5894427394%26name%3Dsoadigitout%2540itispxm.com%26nick%3Ddigitout%26fmp%3D%26lcp%3D; SUB=_2A256SXx5DeTxGeNG4lYV8inPwjiIHXVZP-qxrDV8PUNbuNBeLXPkkW9LHetmTf4qSt43xZywDnS8rVNl5qENYA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFSmMZEdn1kmBrdvnWgNJZF5JpX5K2hUgL.Fo-R1KBXeoM01KB2dJLoI7y.IgUDUsvfU5tt; SUHB=0YhB9HZhcgnYO6; ALF=1496203176; SSOLoginState=1464667177"
        self.cookdic = dict(Cookie=cookie)

    def __init__(self):
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

        try:
            req = requests.get(toUrl, cookies=self.cookdic, timeout=1)
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

    def impRe(self, target):
        info_dict = {}
        pattern = u'昵称:([^\|]*)\|'
        m = re.search(pattern, target)
        if m:
            info_dict['name'] = m.group(1)

        pattern = u'性别:([^\|])'
        m = re.search(pattern, target)
        if m:
            info_dict['sex'] = m.group(1)

        pattern = u'地区:([^\|]*)'
        m = re.search(pattern, target)
        if m:
            info_dict['hometown'] = m.group(1)
        return info_dict

    def get_info(self, inputid):
        time_now = int(time.time())
        inputUrl = constant.HOME_PAGE + inputid + constant.INFO_PAGE
        tmpContent = self.get_content(inputUrl)
        soup = BeautifulSoup(tmpContent.text, "html.parser")

        divlabel = soup.find_all('div', 'tip')
        personalInfo = divlabel[0].next_sibling.get_text('|', strip=True)
        schoolInfo = divlabel[1].next_sibling.get_text()
        info_dict = self.impRe(personalInfo)
        # get_weibo(inputid)
        return info_dict

    def get_result(self, inputid):
        return {'uid': inputid, 'updated_at': time.time(), 'weibo_list': self.get_weibo(inputid),
                        'info_dict': self.get_info(inputid),}

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
