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
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)