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

from spider import *

# ...
app = Flask(__name__)

bootstrap = Bootstrap(app)

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

@app.route('/')
def index():
    return render_template('index.html', title="DigItOut | Home")



@app.route('/api/wordcloud', methods = ['POST'])
def api_wordcloud():
    d = json.loads(request.form.get('data'))
    if d is None:
        abort(400) # missing arguments
    # headers = {  "Content-Type" : "application/json", "Accept": "application/json", "X-Token": "EGO3bf5q.5590.K4UZUWYVnTIQ"}
    # url = 'http://api.bosonnlp.com/keywords/analysis'
    # r = requests.post(url, data=json.dumps(d['text']), headers=headers)
    # print (r.text)
    # ans = r.text
    # return jsonify({ 'data': ans }), 201

    id_str = d['text']
    print (id_str)

    my_spider = Spider()
    latest, my_weibo_list = my_spider.crawl( my_spider.username_to_uid( id_str ) )

    print my_spider.username_to_uid( id_str )


    # rd = open('./static/my_weibo_list.json', 'r')
    # my_weibo_list = json.loads(rd.read())
    # rd.close()

    alltext = u''
    import pdb
    pdb.set_trace()

    for item in my_weibo_list['weibo_list']:
        text = re.sub(r'<[^>]*>', '', item['text'])
        alltext += text

    # alltext = u'地区地区昵称地区'

    # headers = {  "Content-Type" : "application/json", "Accept": "application/json", "X-Token": "EGO3bf5q.5590.K4UZUWYVnTIQ"}
    # url = 'http://api.bosonnlp.com/keywords/analysis'
    # r = requests.post(url, data=json.dumps(alltext).encode('utf-8'), headers=headers)
    # print chardet.detect(r.text)

    # sentiment
    # nlp = BosonNLP('EGO3bf5q.5590.K4UZUWYVnTIQ')
    # ans = nlp.extract_keywords(alltext, top_k=40)
    # for weight, word in ans:
    #     print(weight, word)

    # 437c5088a88bbf2a3e1ffc15abb469a2
    data = {'appkey': '258bbb3f7adf4c0e7fb74129d59865e9', 'text': alltext[0:600]}
    #
    url = 'http://qingyu.thunlp.org/api/KeywordExtract'
    r = requests.post(url, data=data)
    print (r.text)
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

    return jsonify({ 'ans': ans, 'time': timepoint, 'week': weekchart, 'day': daychart}), 201

# @app.route('/user/<name>')
# def user(name=None):
#     return render_template('user.html', name=name)

# @app.route("/login",methods=['POST','GET'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin123':
#                 error= "sorry"
#         else:
#             return redirect(url_for('index'))
#     return render_template('login.html',error=error)

if __name__ == '__main__':
    app.debug = True
    app.run() #app.run(host='0.0.0.0')
