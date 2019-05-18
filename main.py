from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="template")
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:money@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "Y82ono(of$i0f"


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_user = db.Column(db.String(15), db.ForeignKey("user.username"))
    blog_title = db.Column(db.String(35), unique=True)
    blog_body = db.Column(db.String(2000))

    def __init__(self, b_user, blog_title, blog_body):
        self.b_user = b_user
        self.blog_title = blog_title
        self.blog_body = blog_body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(10))
    blogs = db.relationship("Blog", backref = "b_user")

    def __init__(self, username, password):
        self.username = username
        self.password = password
     



@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", title="Build-A-Blog", users=users)


@app.route("/newpost", methods = ["GET", "POST"])
def newpost():

    title_error=""
    body_error=""
    author = session["username"]
    # author_id = User.query.get(author)

    if request.method =='POST':
        blog_title = request.form["blog_title"]
        blog_body = request.form["blog_body"]

        #Title Validation
        if blog_title == "":
            title_error = "Please Fill In The Title"
        
        #Body Validation
        if blog_body == "":
            body_error = "Please Fill In The Body"


        if title_error == "" and body_error =="":
            new_blog = Blog(author, blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return render_template("postpage.html", blog=new_blog, author=author)
        else:
            return render_template("newpost.html", title_error=title_error, body_error=body_error)
    return render_template("newpost.html", title="Build-A-Blog")


@app.before_request
def require_login():
    blocked_routes = ["newpost"]
    if request.endpoint in blocked_routes and "username" not in session:
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["username"] = username
            flash("Logged in")
            return redirect("/")
        else:
            flash("User password incorrect, or user does not exist", "error")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]
        current_user = User.query.filter_by(username=username).first()
        if not current_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/newpost")
        else:
            return "<h1>This user already exists.</h1>"
    return render_template("signup.html")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/singleuser")
def singleuser():
    identity = int(request.args.get("id"))
    users = User.query.get(identity)
    blogz = Blog.query.filter_by(blog_user=users.username).all()
    return render_template("singleuser.html", users=users, blogz=blogz)

@app.route("/view")
def view():
    return render_template("view.html")



# @app.route("/", methods = ["GET"])
# def blog():
#     blogz = Blog.query.all()
#     return render_template("view.html", title="Build-A-Blog", blogz=blogz)

@app.route("/postpage")
def postpage():
    identity = int(request.args.get("id"))
    bl = Blog.query.get(identity)
    username = User.query.get(bl.blog_user)
    return render_template("postpage.html", blog=bl, username=username)

if __name__ == "__main__":
    app.run()