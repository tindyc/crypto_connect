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
        flash("Registration Successful!")
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
                flash("Welcome, {}".format(request.form.get("username")))
            else:
                # invalid password
                flash("Incorrect Username/Password!")
                return redirect(url_for("login"))
        else:
            # username doesn't exist/is incorrect
            flash("Incorrect Usernname/Password")
            return redirect(url_for("login"))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)