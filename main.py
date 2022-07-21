from flask import Flask, render_template, make_response, request, redirect
from sqla_wrapper import SQLAlchemy
import uuid
import hashlib
import os

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
db = SQLAlchemy(db_url)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    salary = db.Column(db.Integer, unique=False)
    password = db.Column(db.String, unique=False)
    session_token = db.Column(db.String, unique=True)

db.create_all()

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    salary = request.form.get("user-salary")
    password = request.form.get("user-password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter_by(name=name).first()

    if not user:
        user = User(name=name, salary=salary, password=hashed_password)
        user.save()

    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    elif hashed_password == user.password:
        session_token = str(uuid.uuid4())
        print("created session token:", session_token)

        user.session_token = session_token
        user.save()

        response = make_response(redirect('/'))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response

@app.route("/")
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("index.html", user=user)

if __name__ == '__main__':
    app.run()
