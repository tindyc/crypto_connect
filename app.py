import os
from datetime import date, datetime
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


date = date.today()


# Renders home page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


# Register user in the db
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if user already in db
        existing_user = mongo.db.users.find_one(
                        {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("register"))

        # check if email already in db
        existing_email = mongo.db.users.find_one(
                        {"email": request.form.get("email").lower()})

        if existing_email:
            flash("Email address already registered!")
            return redirect(url_for("register"))

        # add user details to db
        register = {
            "firstname": request.form.get("firstname").lower(),
            "lastname": request.form.get("lastname").lower(),
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "connections": [],
            "date_created": date.strftime("%d %b %Y")
        }
        mongo.db.users.insert_one(register)

        # put the user into a session cookie
        session["user"] = request.form.get("username").lower()
        flash("Sign Up Successful!")
        return redirect(url_for("my_profile", username=session["user"]))

    return render_template("register.html")


# Log existing user into site
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if user already in db
        existing_user = mongo.db.users.find_one(
                        {"username": request.form.get("username").lower()})
        # ensure password matches
        if existing_user:
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                return redirect(url_for("my_profile",
                                username=session["user"]))
            else:
                # invalid password
                flash("Incorrect Username/Password!")
                return redirect(url_for("login"))
        else:
            # username doesn't exist/is incorrect
            flash("Incorrect Usernname/Password")
            return redirect(url_for("login"))

    return render_template("login.html")


# Logs user out of their account
@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Displays all member profiles in the db
@app.route("/members")
def members():
    profiles = list(mongo.db.profiles.find())
    return render_template("members.html", profiles=profiles)


# Display full member profile
@app.route("/profile_detail/<profile_id>")
def profile_detail(profile_id):
    profile = mongo.db.profiles.find_one({"_id": ObjectId(profile_id)})
    return render_template("profile_detail.html",
                           profile=profile)


# Add profile form
@app.route("/add_profile", methods=["GET", "POST"])
def add_profile():
    if request.method == "POST":
        # default values if fields are left blank
        default_img = ("profile_image.png")
        profile = {
            "member_type": request.form.get("member_type"),
            "fullname": request.form.get("fullname"),
            "birthday": request.form.get("birthday"),
            "location": request.form.get("location"),
            "job_title": request.form.get("job_title"),
            "experience": request.form.get("experience"),
            "interests": request.form.get("interests"),
            "image": request.form.get("image") or default_img,
            "created_by": session["user"],
            "date_created": date.strftime("%d %b %Y")
        }
        mongo.db.profiles.insert_one(profile)
        flash("Your Profile Has Been Added")
        return redirect(url_for("my_profile", username=session["user"]))

    profiles = mongo.db.profiles.find().sort("fullname", 1)
    return render_template("add_profile.html", profiles=profiles)


# Update profile form
@app.route("/update_profile/<profile_id>", methods=["GET", "POST"])
def update_profile(profile_id):
    if request.method == "POST":
        # default values if fields are left blank
        default_img = ("profile_image.png")
        update = {
            "member_type": request.form.get("member_type"),
            "fullname": request.form.get("fullname"),
            "birthday": request.form.get("birthday"),
            "location": request.form.get("location"),
            "job_title": request.form.get("job_title"),
            "experience": request.form.get("experience"),
            "interest": request.form.get("interest"),
            "image": request.form.get("image") or default_img,
            "created_by": session["user"],
            "date_created": date.strftime("%d %b %Y")
        }
        mongo.db.profiles.update({"_id": ObjectId(profile_id)}, update)
        flash("Your Profile Has Been Updated")
        return redirect(url_for("my_profile", username=session["user"]))

    profile = mongo.db.profiles.find_one({"_id": ObjectId(profile_id)})
    profiles = mongo.db.profiles.find().sort("fullname", 1)
    return render_template("update_profile.html", profile=profile,
                           profiles=profiles)


# Display members personal profile page
@app.route("/my_profile/<username>", methods=["GET", "POST"])
def my_profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        my_profile = list(mongo.db.profiles.find(
                {"created_by": session["user"]}))
        user = mongo.db.users.find_one({"username": session["user"]})
        connections = user["connections"]
        my_connections = []
        for con in connections:
            connection = mongo.db.profiles.find_one({"_id": ObjectId(con)})
            if connection is not None:
                my_connections.append(connection)
        return render_template("profile.html", username=username,
                               user=user, profiles=my_profile,
                               my_connections=my_connections)
    return redirect(url_for('login'))


# Add another member as a connection
@app.route("/add_connection/<profile_id>", methods=["GET", "POST"])
def add_connection(profile_id):
    if request.method == "POST":
        user = mongo.db.users.find_one({"username": session["user"].lower()})
        connections = mongo.db.users.find_one(user)["connections"]
        # if member is already connected
        if ObjectId(profile_id) in connections:
            flash("You are already connected!")
            return redirect(url_for("members"))
        # otherwise adds member to users connections
        mongo.db.users.update_one(
             user, {"$push": {
                "connections": ObjectId(profile_id)}})
        flash("You are now connected!")
        return redirect(url_for("members"))


# Allows user to remove a connection
@app.route("/remove_connection/<profile_id>", methods=["GET", "POST"])
def remove_connection(profile_id):
    if request.method == "POST":
        user = mongo.db.users.find_one({"username": session["user"].lower()})
        mongo.db.users.update_one(user, {
            "$pull": {"connections": ObjectId(profile_id)}})
        flash("Connection removed!")
        return redirect(url_for("my_profile", username=session["user"]))


# Allows user to search all members in the db and returns the result
@app.route("/search", methods=["GET", "POST"])
def search():
    search = request.form.get("search")
    profiles = list(mongo.db.profiles.find({"$text": {"$search": search}}))
    return render_template("members.html", profiles=profiles)


# Displays all blog posts  in the db
@app.route("/blogs")
def blogs():
    blogs = list(mongo.db.blogs.find())
    return render_template("blogs.html", blogs=blogs)


# Display blog post
@app.route("/blog_detail/<blog_id>")
def blog_detail(blog_id):
    blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    return render_template("blog_detail.html",
                           blog=blog)


# Allow users to add a blog post to db
@app.route("/add_blog", methods=["GET", "POST"])
def add_blog():
    if request.method == "POST":
        # default values if fields are left blank
        default_img = ("blog_image.png")
        blog = {
            "blog_title": request.form.get("blog_title"),
            "content": request.form.get("content"),
            "image": request.form.get("image") or default_img,
            "created_by": session["user"],
            "date_created": date.strftime("%d %b %Y"),
        }
        mongo.db.blogs.insert_one(blog)
        flash("Your Blog Post Has Been Added")
        return redirect(url_for("blogs", username=session["user"]))

    blog = mongo.db.blogs.find().sort("blog_title", 1)
    return render_template("add_blog.html", blogs=blogs)


# Update blog post
@app.route("/edit_blog/<blog_id>", methods=["GET", "POST"])
def edit_blog(blog_id):
    if request.method == "POST":
        # default values if fields are left blank
        default_img = ("blog_image.png")
        update = {
            "blog_title": request.form.get("blog_title"),
            "content": request.form.get("content"),
            "image": request.form.get("image") or default_img,
            "created_by": session["user"],
            "date_created": date.strftime("%d %b %Y")
        }
        mongo.db.blogs.update({"_id": ObjectId(blog_id)}, update)
        flash("Your Blog Post has been updated")
        return redirect(url_for("blogs", username=session["user"]))

    blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    blogs = mongo.db.blogs.find().sort("blog_title", 1)
    print(blog)
    return render_template("edit_blog.html", blog=blog, blogs=blogs)


# Allow users to delete blog post
@app.route("/delete_blog/<blog_id>")
def delete_blog(blog_id):
    mongo.db.blogs.remove({"_id": ObjectId(blog_id)})
    flash("Blog Post has been deleted")
    return redirect(url_for("blogs", username=session["user"]))


messages = []


@app.route('/chat', methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user = mongo.db.users.find_one({"username": session["user"].lower()})

    if "user" in session:
        return redirect(session["user"])
    return render_template("chat.html")


# Add message
def add_messages(username, message):
    """Add messages to the `messages` list"""
    now = datetime.now().strftime("%H:%M %d %b %Y")
    messages_dict = {"timestamp": now, "from": username, "message": message}

    messages.append(messages_dict)


# Display chat messages
@app.route('/<username>', methods=["GET", "POST"])
def user(username):
    if request.method == "POST":
        username = session["user"]
        message = request.form["message"]
        add_messages(username, message)
        return redirect(session["user"])

    return render_template("chat.html", username=username,
                           chat_messages=messages)


# Send message
@app.route('/<username>/<message>')
def send_message(username, message):
    """Create a new message and redirect back to the chat page"""
    add_messages(username, message)
    return redirect('chat' + username)


# 404 error page
@app.errorhandler(404)
def page_not_found(e):
    """
    Renders a custom 404 error page with a button
    that takes the user back to the home page.
    """
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
