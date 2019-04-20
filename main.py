from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):

        self.title = title
        self.body = body


@app.route('/blog', methods=[ 'GET'])
def index():

    if request.args.get("id"):

        #blogs = Blog.query.all()
        #return render_template("blog.html", title="Build a Blog", blogs=blogs)

    #else:
        blog_id = request.args.get("id")
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template("oneblog.html", blog_title=blog.title, blog_body=blog.body ,blog_id=blog.id)
    else:
        blogs = Blog.query.all()
        return render_template("blog.html", title="Build a Blog", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    #blog_title = ""
    #log_body = ""

    if request.method =="POST":
        title_error = ''
        entry_error = ''
        blog_title = request.form["blog_title"]
        blog_body = request.form["blog_body"]

        if  not blog_title:
            title_error = "Please enter a title for your blog post."
            return render_template("newpost.html", blog_title=blog_title, blog_body=blog_body, title_error=title_error, entry_error=entry_error)

        if not blog_body:
            entry_error = "Please enter a blog post."
            return render_template("newpost.html", blog_title=blog_title, blog_body=blog_body, title_error=title_error, entry_error=entry_error)

        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog')

    else:
        #blog_title = ""
        #blog_body = ""
        return render_template("newpost.html")#blog_title=blog_title, blog_body=blog_body)

if __name__ == '__main__':
    app.run()