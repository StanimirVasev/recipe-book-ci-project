import os
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


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if username or email is already in use
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # Show error message if username is already in use
        if existing_user:
            flash("Username already in use. Please try again.", 'flash-message--error')
            return redirect(url_for("register"))

        existing_email = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})
        # Show error message if email address is already in use
        if existing_email:
            flash("Email already in use. Please try again.", 'flash-message--error')
            return redirect(url_for("register"))

        # Registers new user in MongoDB

        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
            }
        mongo.db.users.insert_one(register)

        # Put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("You account has been created successfully!", 'flash-message--success')
        return redirect(url_for(
            "profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if user exists in the db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Check if password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Hello, {}! It's great to see you online!".format(request.form.get("username")), 'flash-message--success')
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # Show error message if incorrect password is used
                flash("Incorrect password. Please try again.", 'flash-message--error')
                return redirect(url_for("login"))

        else:
            # Show error message if incorrect username is used
            flash("Incorrect username. Please try again.", 'flash-message--error')
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Get user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Remove user from session cookie
    flash("You have been logged out!"'flash-message--success')
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_recipe")
def add_recipe():
  # Allows users to add new recipes
  categories = mongo.db.categories.find().sort("category_name", 1)
  cuisines = mongo.db.cuisines.find().sort("cuisine_name", 1)
  return render_template("add_recipe.html", categories=categories, cuisines=cuisines)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)