from flask import Flask, render_template, request, redirect, url_for, session
from password_generator import generate_password
from user import User
from account import Account

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_password", methods=["POST"])
def generate_password():
    length = int(request.form.get("length"))
    password = generate_password(length)
    session["password"] = password
    return redirect(url_for("index"))

@app.route("/create_account", methods=["POST"])
def create_account():
    username = request.form.get("username")
    email = request.form.get("email")
    password = session.get("password")
    user = User(username, email)
    account = Account(user, password)
    # code to save the account to the database
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)