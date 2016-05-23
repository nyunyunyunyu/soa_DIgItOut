# -*- coding:utf-8 -*-
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
import login


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
    def __init__(self):
        self.cookie = "SINAGLOBAL=9680108074098.826.1461898907956; wb_publish_vip_2031727173=4; wb_bub_hot_5894427394=1; YF-Ugrow-G0=b02489d329584fca03ad6347fc915997; YF-V5-G0=2a21d421b35f7075ad5265885eabb1e4; _s_tentry=login.sina.com.cn; Apache=5034842943168.573.1463327257571; ULV=1463327257606:3:2:1:5034842943168.573.1463327257571:1462236550964; YF-Page-G0=f1bc83fe81b7ae21d6ba1fa7afc24fde; TC-Ugrow-G0=370f21725a3b0b57d0baaf8dd6f16a18; TC-Page-G0=a1e213552523eaff2a80326cc1068982; TC-V5-G0=ffc89a27ffa5c92ffdaf08972449df02; login_sid_t=1ebbc46ab3073f2bc84ca0c7e9bedfaa; myuid=5894427394; UOR=www.aizhan.com,widget.weibo.com,login.sina.com.cn; SUS=SID-5894427394-1463492620-GZ-kiuoz-1fc0200559879aee440b2430283c2161; SUE=es%3Da1802f75c5ae011bfd01b028431d781e%26ev%3Dv1%26es2%3D379a04ee0329d81efd4b1b6d55695c86%26rs0%3DF7PrH9J4nF32pB1mHLGHSPeRXA1v0XQw020cRvtjlUK%252F5unHTZYwR5NcZ3%252BglwU5stca6N8Ys8AELbapHju9eJ%252FmGRQoHVIm5CBTJGuFA5QDUKBK0kTSgnEmQ%252FHoqcS6SQkY2uQNVLmpMWjOFmKx%252BJAKSNlgDjWcmSNm5mygkzw%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1463492620%26et%3D1463579020%26d%3Dc909%26i%3D2161%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D2%26st%3D0%26uid%3D5894427394%26name%3Dsoadigitout%2540itispxm.com%26nick%3Ddigitout%26fmp%3D%26lcp%3D; SUB=_2A256P1BcDeTxGeNG4lYV8inPwjiIHXVZTcaUrDV8PUNbuNBeLVqtkW9LHeuKWr-9jL2byC7J1ffaV4-jX1xV-A..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFSmMZEdn1kmBrdvnWgNJZF5JpX5K2hUgL.Fo-R1KBXeoM01KBt; SUHB=04W-9u9K83Swbj; ALF=1495028620; SSOLoginState=1463492620; un=soaDigItOut@itispxm.com; wvr=6; lzstat_uv=23978883723075672468|2893156; lzstat_ss=2356230116_1_1463524403_2893156; WBtopGlobal_register_version=60539f809b40ed0d"
        cookdic = dict(Cookie=self.cookie)

    def get_content(self, toUrl):
        """ Return the content of given url
            Args:
                toUrl: aim url
                count: index of this connect
            Return:
                content if success
                'Fail' if fail
        """

        # cookdic = dict(Cookie=cookie)

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
                # my_weibo['url_type'] = weibo['url_struct'][0]['url_type']
        showjson(my_weibo_list, 0)
        return my_weibo_list
        # for my_weibo in my_weibo_list:
        #     print my_weibo

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
        inputUrl = home_page + inputid + info_page
        tmpContent = self.get_content(inputUrl)
        soup = BeautifulSoup(tmpContent.text, "html.parser")
        # time.sleep(1)
        divlabel = soup.find_all('div', 'tip')
        personalInfo = divlabel[0].next_sibling.get_text('|', strip=True)
        schoolInfo = divlabel[1].next_sibling.get_text()
        info_dict = self.impRe(personalInfo)
        # get_weibo(inputid)
        return info_dict

    def crawl(self, inputid):
        # 'info_dict':get_info(inputid),
        # cookdic = login.getCookies([{'no':username, 'psw':password}])[0]

        return {'weibo_list': self.get_weibo(inputid)}
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

    print 'done...'
