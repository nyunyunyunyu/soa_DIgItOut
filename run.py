#-*- coding:utf-8 -*-
# from __future__ import print_function, unicode_literals
# from bosonnlp import BosonNLP


from flask import *
from flask.ext.bootstrap import Bootstrap
import requests
import json
import re
#import chardet
import time
import datetime

from vendor.spider import *
from vendor.image_detect import *

# ...
app = Flask(__name__)

bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html', title="DigItOut | Home")


@app.route("/api/piccluster", methods=['POST'])
def api_piccluster():
    d = json.loads(request.form.get('data'))
    if d is None:
        abort(400) # missing arguments

    print d['username']

    my_spider = Spider()
    idstr = my_spider.username_to_uid( d['username'] )
    latest, my_weibo_list = my_spider.crawl( idstr )
    print "Picture Cluster..."
    image_detect.get_grouping_result(my_weibo_list, latest)
    group, face_info = get_grouping_result(my_weibo_list, latest)
    url_list = []
    for series in group:
        print series
        each_list = []
        for no in series:
            each_list.append(face_info[no]['url'])
        url_list.append( list(set(each_list)) )
    # print url_list

    return jsonify({ 'url_list': url_list}), 201


@app.route('/api/wordcloud', methods = ['POST'])
def api_wordcloud():
    d = json.loads(request.form.get('data'))
    if d is None:
        abort(400) # missing arguments

    usrname_str = d['text']
    print (usrname_str)
    my_spider = Spider()
    uid_str = my_spider.username_to_uid( usrname_str )
    print uid_str
    latest, my_weibo_list = my_spider.crawl( uid_str )

    # rd = open('./static/my_weibo_list.json', 'r')
    # my_weibo_list = json.loads(rd.read())
    # rd.close()

    alltext = u''

    # import pdb
    # pdb.set_trace()

    person_info = my_weibo_list['info_dict']
    lon, lat = [], []
    for item in my_weibo_list['weibo_list']:
        text = re.sub(r'<[^>]*>', '', item['text'])
        alltext += text
        if (item.has_key('location_lon') and item.has_key('location_lon')):
            lo = float(item['location_lon'])
            la = float(item['location_lat'])
            if(len(lon)==0):
                lon.append(lo)
                lat.append(la)
                print '----'
            else:
                if abs(lo-lon[-1])<0.2 and abs(la-lat[-1])<0.2:
                    continue
                else:
                    lon.append(lo)
                    lat.append(la)
                    print '----'
    print lon
    print lat

    # 437c5088a88bbf2a3e1ffc15abb469a2
    data = {'appkey': '258bbb3f7adf4c0e7fb74129d59865e9', 'text': alltext[0:600]}
    #
    url = 'http://qingyu.thunlp.org/api/KeywordExtract'
    r = requests.post(url, data=data)
    ans = json.loads(r.text)['Result']
    # print ans[0]
    # time
    weekchart = [0]*7
    daychart = [0]*24
    temp_time = [[0]*24, [0]*24, [0]*24, [0]*24, [0]*24, [0]*24, [0]*24]
    for item in my_weibo_list['weibo_list']:
        if not '-' in item['created_at']:
            continue
        s = item['created_at'].encode('utf-8')
        ti = s.split(' ')
        date = ti[0].split('-')
        if len(date)==2:
            w = str(datetime.datetime(int(time.strftime('%Y')), int(date[0]),int(date[1])).strftime("%w"))
        elif len(date)==3:
            w = str(datetime.datetime(int(date[0]),int(date[1]),int(date[2])).strftime("%w"))
        weekchart[ (7-int(w)) %7 ] += 1
        daychart[ (24-int(ti[1].split(':')[0])) %24 ] += 1
        temp_time[ int(w) ][ int(ti[1].split(':')[0]) ] += 1

    timepoint = []
    for i in range(7):
        for j in range(24):
            timepoint.append([i, j, temp_time[i][j]])

    print weekchart
    print daychart

    return jsonify({ 'ans': ans, 'time': timepoint, 'week': weekchart, 'day': daychart, 'lon':lon, 'lat':lat, 'person':person_info}), 201


#@app.route('/user/<username>')
#def show_user_profile(username):
#    # show the user profile for that user
#    return 'User %s' % username

#@app.route('/post/<int:post_id>')#int, float, path
#def show_post(post_id):
#    # show the post with the given id, the id is an integer
#    return 'Post %d' % post_id

#@app.route('/login', methods=['GET', 'POST'])
#def login():
#    if request.method == 'POST':
#        do_the_login()
#    else:
#        show_the_login_form()

#url_for('static', filename='style.css')

#@app.route('/user/')

# @app.route('/user/<name>')
# def user(name=None):
#     return render_template('user.html', name=name)

if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True) #app.run(host='0.0.0.0')
