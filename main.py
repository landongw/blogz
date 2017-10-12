"""This app runs a blog with multiple users. NOTE: reset, db user/pass,
secret key, and password hashing before use. """

import re
from datetime import datetime
from flask import Flask, request, escape, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = ("mysql+pymysql://blogz:"
                                         "WR34Y9MD3PICfHO9"
                                         "@localhost:8889/blogz")
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "3AqR6cKGTJ7FRkn.VTtw3"
db = SQLAlchemy(app)


class Blog(db.Model):
    """ Creates the Blog table and constructor """

    post_id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(1000))
    post_body = db.Column(db.String(50000))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __init__(self, owner, post_title, post_body, pub_date=None):
        self.owner = owner
        self.post_title = post_title
        self.post_body = post_body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date


class User(db.Model):
    """ Creates the User table and constructor """

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


def is_not_empty(value):
    """ Tests if a field is not empty """

    if (re.compile('.')).match(value):
        return True


def has_no_spaces(value):
    """ Tests if the field contains blank spaces """

    if not (re.compile(r'\s')).search(value):
        return True


def passwords_match(password1, password2):
    """ Tests if the passwords match """

    if re.compile(password1).match(password2):
        return True


def is_valid_length(value):
    """ Tests if the input is of valid length ( > 3 and < 200) """

    if re.compile('^.{3,200}$').match(value):
        return True


def is_email(email):
    """ Tests if the input is a valid email format """

    if (re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
            .match(email)):
        return True


@app.before_request
def require_login():
    """ Requires login to access protected content """

    allowed_routes = ['blog_page', 'register', 'login', 'single_post', 'index', 'blog_index', 'blog_page']

    if request.endpoint not in allowed_routes and 'username' not in session and '/static/' not in request.path:
        return redirect('/login')
    elif request.endpoint is 'login' and 'username' in session:
        return redirect('/blog')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """ Handles user login """

    username_error = ""
    password_error = ""
    username = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username  # Use redis in production
            return redirect('/newpost')
        elif user and not check_pw_hash(password, user.pw_hash):
            password_error = 'Password incorrect.'
        elif not user:
            username_error = 'User does not exist.'
        else:
            pass

    return render_template('login.html',
                           username_error=username_error,
                           password_error=password_error,
                           username=username)


@app.route('/signup', methods=['POST', 'GET'])
def register():
    """ Handles user signup """

    username_error = ""
    password_error = ""
    verify_error = ""
    username = ""
    password = ""
    verify = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        new_user = User(username, password)

        # CHECKS FOR EMPTY FIELDS
        if not is_not_empty(username):
            username = ""
            username_error += "This field cannot be empty. "

        if not is_not_empty(password):
            password = ""
            password_error += "This field cannot be empty. "

        if not is_not_empty(verify):
            verify = ""
            verify_error += "This field cannot be empty. "

        # CHECKS IF VALID LENGTH
        if not is_valid_length(username):
            username_error += "Must be between 3 and 200 characters long. "

        if not is_valid_length(password):
            password = ""
            password_error += "Must be between 3 and 200 characters long. "

        if not is_valid_length(verify):
            verify = ""
            verify_error += "Must be between 3 and 200 characters long. "

        # CHECKS FOR SPACES
        if not has_no_spaces(username):
            username_error += "May not contain spaces. "

        if not has_no_spaces(password):
            password = ""
            password_error += "May not contain spaces. "

        if not has_no_spaces(verify):
            verify = ""
            verify_error += "May not contain spaces. "

        # CHECKS IF PASSWORDS MATCH
        if not passwords_match(password, verify):
            password = ""
            verify = ""
            password_error += "Passwords do not match. "

        # CHECKS FOR EXISTING USER
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = "User already exists."

        if not existing_user and not password_error and not username_error and not verify_error:
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            pass

    return render_template('/signup.html',
                           username=username,
                           username_error=username_error,
                           password_error=password_error,
                           verify_error=verify_error)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """ Logs the user out """

    del session['username']
    return redirect('/blog')


@app.route('/')
def index():
    """ Displays the home page with all users """

    users = User.query.all()
    return render_template('index.html', title="Home", users=users)


@app.route('/blog', methods=['GET'])
def blog_page(user_id=0):
    """ Returns the main blog page """

    user_id = request.args.get('user_id', user_id)

    if not user_id:
        titles = Blog.query.all()
        return render_template('blog_index.html', title="Blog Name", titles=titles)
    elif user_id:
        owner = User.query.get(user_id)
        titles = Blog.query.filter(Blog.owner_id == user_id)
        return render_template('user_blog.html', title="User Blog", user_id=user_id, titles=titles, owner=owner)


@app.route('/newpost')
def new_post_index():
    """ Returns a template to submit a new post """

    return render_template('/new_post.html', title="New Post")


@app.route('/newpost', methods=['GET', 'POST'])
def submit_new_post():
    """ Submits the new post to the database and
    redirects the user to the new post """

    owner = User.query.filter_by(username=session['username']).first()
    print("OWNER ID: ", owner.username)
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
            create_post = Blog(owner, post_title, post_body)
            db.session.add(create_post)
            db.session.commit()
            obj = db.session.query(Blog).order_by(Blog.post_id.desc()).first()
            post_id = str(obj.post_id)
            return redirect("/single-post/?post_id=" + post_id)
        return render_template('new_post.html', title="New Post",
                               title_error=title_error,
                               post_title=post_title,
                               body_error=body_error,
                               post_body=post_body)


# @app.route('/single-post/<int:id>')
@app.route('/single-post/')
def single_post(post_id=0):
    """ Returns a template with a single post page """

    post_id = request.args.get('post_id', post_id)
    post = Blog.query.get(post_id)

    return render_template('single_post.html', post=post)
    # return "post_id is {}".format(post_id)

if __name__ == '__main__':
    app.run()
