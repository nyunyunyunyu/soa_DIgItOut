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
        cookie = "SINAGLOBAL=1235433884430.6768.1430467351374; wb_publish_vip_2243006675=1; wb_bub_hot_5894427394=1; un=soadigitout@itispxm.com; myuid=5894427394; UOR=,,www.google.com.hk; YF-Page-G0=f70469e0b5607cacf38b47457e34254f; _s_tentry=-; Apache=8905100007286.064.1463722207724; ULV=1463722207739:24:3:2:8905100007286.064.1463722207724:1463500634206; YF-V5-G0=d45b2deaf680307fa1ec077ca90627d1; login_sid_t=79f68dfea5288dec7ccfc85f90279308; YF-Ugrow-G0=169004153682ef91866609488943c77f; SUS=SID-5894427394-1463989169-GZ-rw4j8-cf39c09610a7383c46b8a8691fd7201c; SUE=es%3D0e94e7489b4e57f97e41c15066e22a8d%26ev%3Dv1%26es2%3D83e78fa0bb20b7c192e0df2abaa6b7bf%26rs0%3DP1SyU%252BCEDt9RLimVJJwOhRPT3L2OgOO%252FWEgM9n19ySrTovZQcQccZA7Dh3XH6Uu2lGh7kq9TSI6HZgITOk0l4pHGtATJ746I%252Fm6auLSH9xlbTmIhIOX21HS9EyhMJUDQ4W2oc%252FSKNGgn%252BG9NX0tFTmfkq%252FNi5BnstpiO1PoGFjM%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1463989169%26et%3D1464075569%26d%3Dc909%26i%3D201c%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26uid%3D5894427394%26name%3Dsoadigitout%2540itispxm.com%26nick%3Ddigitout%26fmp%3D%26lcp%3D; SUB=_2A256RsPhDeTxGeNG4lYV8inPwjiIHXVZNbIprDV8PUNbuNBeLU73kW9LHetDCOiyqLcYZzcHm4NBqZm87X4Zsg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFSmMZEdn1kmBrdvnWgNJZF5JpX5K2hUgL.Fo-R1KBXeoM01KBt; SUHB=06ZVejbtcampjD; ALF=1495525168; SSOLoginState=1463989169"
        self.cookdic = dict(Cookie=cookie)

    def __init__(self):
        self.updateCookie()
        self.client = pymongo.MongoClient(constant.MONGODB_HOST, constant.MONGODB_PORT)
        if (not 'soa' in self.client.database_names() or not 'weibo' in self.client['soa'].collection_names()):
            self.client['soa']['weibo'].create_index([('uid', pymongo.ASCENDING)], unique=True)

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
            req = requests.get(toUrl, cookies=self.cookdic, timeout=100)
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
            s = json.loads(self.get_content(inputUrl + str(i)).text)
            # showjson(s['cards'][0]['card_group'][0],0)
            # showjson(s['cards'][0]['card_group'][0]['mblog']['url_struct'][0]['url_title'],0)
            # showjson(s['cards'][0]['card_group'][0]['mblog']['url_struct'][0],0)
            if 'card_group' not in s['cards'][0]:
                continue
            # print s
            # weibo_list = [k['mblog'] for k in s['cards'][0]['card_group']]
            weibo_list = []
            for k in s['cards'][0]['card_group']:
                if 'mblog' in k:
                    weibo_list.append(k['mblog'])
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
                        print weibo['url_struct'][0]['short_url']
                        content = self.get_content(weibo['url_struct'][0]['short_url'])
                        if content:
                            short_url_data = content.text
                            # location.replace("http://weibo.com/p/10040484566?retcode=6102");
                            pattern = u'location.replace\("([^"]*)"\)'
                            # print short_url_data
                            # m = re.search(pattern, short_url_data)
                            # if m:
                            #     gotourl = m.group(1)
                            #     print gotourl
                            url_data = short_url_data
                            # print url_data
                            # print url_data
                            # if url_data == short_url_data:
                            #     print 'fuck'
                            # src="http://place.weibo.com/index.php?_p=place_page&amp;_a=poi_map_right&amp;poiid=120.62851_27.79679&amp;circle=1&amp;radius=11000"
                            # url_data = 'src="http://place.weibo.com/index.php?_p=place_page&amp;_a=poi_map_right&amp;poiid=120.62851_27.79679&amp;'
                            # 地址数据
                            pattern = u'poiid=([^\&]*)\&amp'
                            mm = re.search(pattern, url_data)
                            if mm:
                                print "ok"
                                print mm.group(1)
                                # print mm.group(1)
                                # print url_data
                                my_weibo['location_name'] = weibo['url_struct'][0]['url_title']
                                [lon, lat] = mm.group(1).split('_')
                                my_weibo['location_lon'] = lon
                                my_weibo['location_lat'] = lat
                                # print my_weibo['location']
                                # <src="http://place.weibo.com/index.php?_p=place_page&amp;_a=poi_map_right&amp;poiid=1013247614"
                                # poiObject.lon = 116.307620521;
                                # poiObject.lat = 39.9841806635;
                                # else:
                                #     print 'checkin'
                                #     pattern = u'http:\/\/place.weibo.cn\/poih5?act=poi&amp;do=claim_freesettle&amp;poiid='
                                #     mmm = re.search(pattern, url_data)
                                #     if mmm:
                                #         print 'ok2'
                # if 'url_struct' in weibo:
                #     if weibo['url_struct'][0]['url_type'] == 36:
                #         # showjson(weibo['url_struct'],0)
                #         print weibo['url_struct'][0]['short_url']
                #         short_url_data = get_content(weibo['url_struct'][0]['short_url'], cookdic).text
                #         # location.replace("http://weibo.com/p/10040484566?retcode=6102");
                #         pattern = u'location.replace\("([^"]*)"\)'
                #         m = re.search(pattern, short_url_data)
                #         if m:
                #             gotourl = m.group(1)
                #             print gotourl
                #             url_data = get_content(gotourl, cookdic).text
                #             print url_data
                #             # print url_data
                #             # if url_data == short_url_data:
                #             #     print 'fuck'
                #             # src="http://place.weibo.com/index.php?_p=place_page&amp;_a=poi_map_right&amp;poiid=120.62851_27.79679&amp;circle=1&amp;radius=11000"
                #             # url_data = 'src="http://place.weibo.com/index.php?_p=place_page&amp;_a=poi_map_right&amp;poiid=120.62851_27.79679&amp;'
                #             pattern = u'poiid'
                #             mm = re.search(pattern, url_data)
                #             if mm:
                #                 print "ok"
                #                 # print mm.group(1)
                #             # print url_data
                #         my_weibo['location'] = weibo['url_struct'][0]['url_title']
                if 'created_at' in weibo:
                    my_weibo['created_at'] = weibo['created_at']
                if 'thumbnail_pic' in weibo:
                    my_weibo['thumbnail_pic'] = weibo['thumbnail_pic']
                if 'bmiddle_pic' in weibo:
                    my_weibo['bmiddle_pic'] = weibo['bmiddle_pic']
                if 'original_pic' in weibo:
                    my_weibo['original_pic'] = weibo['original_pic']
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
        return {'uid': inputid, 'updated_at': time.time(), 'weibo_list': self.get_weibo(inputid)}

    def crawl(self, inputid):
        # 'info_dict':get_info(inputid),
        # cookdic = login.getCookies([{'no':username, 'psw':password}])[0]
        if constant.CACHE_ENABLE:
            return self.get_result(inputid)
        find_row = self.client['soa']['weibo'].find_one({'uid': inputid})
        if (find_row):
            weibo_len = len(find_row['weibo_list'])
            days = (time.time() - find_row['updated_at']) / (60 * 60 * 24)
            if(len <= 50 or days > 14):
                res = self.get_result(inputid)
                self.client['soa']['weibo'].replace_one({'uid':inputid}, res)
                return res
            else:
                return find_row
        else:
            res = self.get_result(inputid)
            self.client['soa']['weibo'].insert_one(res)
            return res
        # 'info_dict':get_info(inputid),


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python spider.py <uid>"
        exit()
    print "spider test begin ~~"
    print "----------"
    my_spider = Spider()
    my_weibo_list = my_spider.crawl(sys.argv[1])
    # showjson(my_weibo_list,0)

    # wd = open('./website/static/my_weibo_list.json', 'w')
    # wd.write(json.dumps(my_weibo_list))
    # wd.close()
    print len(my_weibo_list['weibo_list'])

    print 'done...'
