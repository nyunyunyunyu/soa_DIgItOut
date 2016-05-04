from flask import *
from flask.ext.bootstrap import Bootstrap
import requests
import json

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
    print d['text']
    if d is None:
        abort(400) # missing arguments
    headers = {  "Content-Type" : "application/json", "Accept": "application/json", "X-Token": "EGO3bf5q.5590.K4UZUWYVnTIQ"}
    url = 'http://api.bosonnlp.com/keywords/analysis'
    r = requests.post(url, data=json.dumps(d['text']), headers=headers)
    print (r.text)
    ans = r.text
    return jsonify({ 'data': ans }), 201
    

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
