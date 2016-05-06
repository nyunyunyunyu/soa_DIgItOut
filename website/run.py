#-*- coding:utf-8 -*-
from __future__ import print_function, unicode_literals
from bosonnlp import BosonNLP


from flask import *
from flask.ext.bootstrap import Bootstrap
import requests
import json
import re
import chardet
import time
import datetime

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
    # d = json.loads(request.form.get('data'))
    # print d['text']
    # if d is None:
    #     abort(400) # missing arguments
    # headers = {  "Content-Type" : "application/json", "Accept": "application/json", "X-Token": "EGO3bf5q.5590.K4UZUWYVnTIQ"}
    # url = 'http://api.bosonnlp.com/keywords/analysis'
    # r = requests.post(url, data=json.dumps(d['text']), headers=headers)
    # print (r.text)
    # ans = r.text
    # return jsonify({ 'data': ans }), 201
    rd = open('./static/my_weibo_list.json', 'r')
    my_weibo_list = json.loads(rd.read())
    rd.close()

    alltext = u''
    import pdb
    # pdb.set_trace()
    for item in my_weibo_list['weibo_list']:
        text = re.sub(r'<[^>]*>', '', item['text'])
        alltext += text

    # alltext = u'地区地区昵称地区'

    # headers = {  "Content-Type" : "application/json", "Accept": "application/json", "X-Token": "EGO3bf5q.5590.K4UZUWYVnTIQ"}
    # url = 'http://api.bosonnlp.com/keywords/analysis'
    # r = requests.post(url, data=json.dumps(alltext).encode('utf-8'), headers=headers)
    # print chardet.detect(r.text)

    # sentiment
    nlp = BosonNLP('EGO3bf5q.5590.K4UZUWYVnTIQ')
    ans = nlp.extract_keywords(alltext, top_k=40)
    for weight, word in ans:
        print(weight, word)

    # time
    # week = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': []}
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
        # week[ w ].append( ti[1] )
        # timepoint.append( [int(w), int(ti[1].split(':')[0])*60+int(ti[1].split(':')[1]) ] )
        temp_time[ int(w) ][ int(ti[1].split(':')[0]) ] += 1

    timepoint = []
    for i in range(7):
        for j in range(24):
            timepoint.append([i, j, temp_time[i][j]])

    return jsonify({ 'ans': ans, 'time': timepoint }), 201
    
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

