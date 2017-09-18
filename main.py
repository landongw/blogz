"""This script runs a simple blog website"""

from flask import Flask, request, escape, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import re
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:WR34Y9MD3PICfHO9@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(1000))
    post_body = db.Column(db.String(50000))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, post_title, post_body, pub_date=None):
        self.owner = owner
        self.post_title = post_title
        self.post_body = post_body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120)) # TODO: hash this later
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/blog', methods=['GET'])
def blog_page():
    titles = Blog.query.all()
    return render_template('blog_index.html', title="Blog Name", titles=titles)

@app.route('/newpost')
def index():
    return render_template('/new_post.html')

def is_not_empty(value):
    if (re.compile('.')).match(value):
        return True

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():

    owner = User.query.filter_by(id=session['id']).first()

    title_error = ""
    body_error = ""

    if request.method == 'POST':
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        if not is_not_empty(post_title):
            title_error += "This field cannot be empty. "

        if not is_not_empty(post_body):
            body_error += "This field cannot be empty. "

        if not title_error and not body_error:
            new_post = Blog(post_title, post_body, owner)
            db.session.add(new_post)
            db.session.commit()
            obj = db.session.query(Blog).order_by(Blog.id.desc()).first()
            post_id = str(obj.id)
            return redirect("/single-post/?id=" + post_id)
        else:
            return render_template('new_post.html', title="New Post", 
                                   title_error=title_error, post_title=post_title, 
                                   body_error=body_error, post_body=post_body)

# @app.route('/single-post/<int:id>')
@app.route('/single-post/')
def single_post(id = 0):
    id = request.args.get('id', id)
    post = Blog.query.get(id)

    return render_template('single_post.html', post=post)
    # return "id is {}".format(id)

if __name__ == '__main__':
    app.run()
