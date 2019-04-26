from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ou812'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):

        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):

        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')      


@app.route('/blog', methods=[ 'GET'])
def list_blogs():

    if request.args.get("id"):

        blog_id = request.args.get("id")
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template("oneblog.html", blog_title=blog.title, blog_body=blog.body ,blog_id=blog.id)
    else:
        blogs = Blog.query.all()
        return render_template("blog.html", title="Build a Blog", blogs=blogs)

@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method =="POST":
        title_error = ''
        entry_error = ''
        blog_title = request.form["blog_title"]
        blog_body = request.form["blog_body"]
        blog_owner = session['username']

        if  not blog_title:
            title_error = "Please enter a title for your blog post."
            return render_template("newpost.html", blog_title=blog_title, blog_body=blog_body, title_error=title_error, entry_error=entry_error)

        if not blog_body:
            entry_error = "Please enter a blog."
            return render_template("newpost.html", blog_title=blog_title, blog_body=blog_body, title_error=title_error, entry_error=entry_error)

        new_owner = User.query.filter_by(username=blog_owner).first()
        new_blog = Blog(title=blog_title, body=blog_body, owner=new_owner)
        #new_blog = Blog("blog", "abc", "123")
        db.session.add(new_blog)
        db.session.commit()
        blog_id = str(new_blog.id)
        return redirect('/blog?id='+ blog_id)
    else:
        return render_template("newpost.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    name_error = ''
    password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if user and user.password != password:
            password_error = "You have entered an incorrect password. Please try again."
            return render_template("/login.html", username=username, password='', name_error=name_error, password_error=password_error)
        else:
            name_error = "Invalid username."
            return render_template("login.html", username= '', password='', name_error=name_error, password_error=password_error)

    return render_template('login.html')


@app.route('/signup', methods=['Post', 'Get'])
def signup():
    if request.method == 'POST':
        name_error = ''
        password_error = ''
        verify_error = ''
        empty_error = ''
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]

        if not username or not password or not verify:
            empty_error = "One or more fields have been left empty. Please try again."
            render_template("signup.html", username=username, password='', verify='', name_error=name_error, password_error=password_error, verify_error=verify_error, empty_error=empty_error)

        if len(username) <= 2:
            name_error = "Username must contain at least three characters."
            return render_template("signup.html", username='', password='', verify='', name_error=name_error, password_error=password_error, verify_error=verify_error, empty_error=empty_error)

        if len(password) <= 2:
            password_error = "Password must contain least three characters."
            return render_template("signup.html", username=username, password='', verify='', name_error=name_error, password_error=password_error, verify_error=verify_error, empty_error=empty_error)

        if verify != password:
            verify_error = "Password verification does not match password. Please try again."
            return render_template("signup.html", username=username, password='', verify='', name_error=name_error, password_error=password_error, verify_error=verify_error, empty_error=empty_error)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            name_error = "A user with that name already exists. Please try again."
            return render_template("signup.html", username='', password='', verify='', name_error=name_error, password_error=password_error, verify_error=verify_error, empty_error=empty_error)
            
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    else:
        return render_template("signup.html")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run() 