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
        cookie = "SINAGLOBAL=9680108074098.826.1461898907956; wb_publish_vip_2031727173=4; wb_bub_hot_5894427394=1; YF-Ugrow-G0=b02489d329584fca03ad6347fc915997; YF-V5-G0=2a21d421b35f7075ad5265885eabb1e4; _s_tentry=login.sina.com.cn; Apache=5034842943168.573.1463327257571; ULV=1463327257606:3:2:1:5034842943168.573.1463327257571:1462236550964; YF-Page-G0=f1bc83fe81b7ae21d6ba1fa7afc24fde; TC-Page-G0=a1e213552523eaff2a80326cc1068982; login_sid_t=1ebbc46ab3073f2bc84ca0c7e9bedfaa; myuid=5894427394; lzstat_uv=23978883723075672468|2893156; lzstat_ss=2356230116_1_1463524403_2893156; wb_g_minivideo_5894427394=1; wvr=6; TC-V5-G0=866fef700b11606a930f0b3297300d95; TC-Ugrow-G0=0149286e34b004ccf8a0b99657f15013; UOR=www.aizhan.com,widget.weibo.com,gre.tiandaoedu.com; WBStore=8ca40a3ef06ad7b2|undefined; WBtopGlobal_register_version=60539f809b40ed0d; SUS=SID-5894427394-1464508713-GZ-d2ty5-577721388825c5d13fd4092d245420e6; SUE=es%3D5255a9bf667cbe44420de378f7ffc539%26ev%3Dv1%26es2%3D2249dabf2dbfcbfe546e77e64852357d%26rs0%3Dlndjx7LIB1WEd88by7pu68e%252F0zx48cVBhHsaOQuKYCH7meFsxCcsCerWCNvY%252FpSPEhA6VtTMBC%252BydQbm8OeuVjZ1SfWa57G0MeLZnH%252FEowFwq%252BfcbVZtblF2QUCQEKpthEjgmOi8MEktkAA4sA3g%252FErNerDUl3GyoQaf78%252BPdU8%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1464508713%26et%3D1464595113%26d%3Dc909%26i%3D20e6%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D2%26st%3D0%26uid%3D5894427394%26name%3Dsoadigitout%2540itispxm.com%26nick%3Ddigitout%26fmp%3D%26lcp%3D; SUB=_2A256TtF5DeTxGeNG4lYV8inPwjiIHXVZOkWxrDV8PUNbuNBeLUfzkW9LHeuO44aUtMi19nM3in2D4znQ_iPlFw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFSmMZEdn1kmBrdvnWgNJZF5JpX5K2hUgL.Fo-R1KBXeoM01KB2dJLoI7y.IgUDUsvfU5tt; SUHB=0A0ZpEZot003ds; ALF=1465113513; SSOLoginState=1464508713; un=soaDigItOut@itispxm.com"
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
        return {'uid': inputid, 'updated_at': time.time(), 'weibo_list': self.get_weibo(inputid)}

    def crawl(self, inputid):
        # 'info_dict':get_info(inputid),
        # cookdic = login.getCookies([{'no':username, 'psw':password}])[0]
        if not constant.CACHE_ENABLE:
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
