from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku
from flask_cors import CORS
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import os

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

db = SQLAlchemy(app)
ma = Marshmallow(app)
heroku = Heroku(app)
CORS(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=False)
    recommend = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, author, review, recommend, user_id):
        self.title = title
        self.author = author
        self.review = review
        self.recommend = recommend
        self.user_id = user_id

class BookSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "author", "review", "recommend", "user_id")

book_schema = BookSchema()
multiple_book_schema = BookSchema(many=True)


@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON.")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    possible_duplicate = db.session.query(User).filter(User.username == username).first()
    if possible_duplicate is not None:
        return jsonify("Error: Username Taken")

    encrypted_password = bcrypt.generate_password_hash(password).decode("utf-8")

    record = User(username, encrypted_password)

    db.session.add(record)
    db.session.commit()

    return jsonify("User Added")

@app.route("/user/verify", methods=["POST"])
def verify_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON.")

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    record = db.session.query(User).filter(User.username == username).first()

    if record is None:
        return jsonify("User NOT Verified")

    if bcrypt.check_password_hash(record.password, password) == False:
        return jsonify("User NOT Verified")

    return jsonify("User Verified")

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(all_users))

@app.route("/user/get/<id>", methods=["GET"])
def get_user_by_id(id):
    user = db.session.query(User).filter(User.id == id).first()
    return jsonify(user_schema.dump(user))

@app.route("/user/get/username/<username>", methods=["GET"])
def get_user_by_username(username):
    user = db.session.query(User).filter(User.username == username).first()
    return jsonify(user_schema.dump(user))

@app.route("/book/add", methods=["POST"])
def add_book():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON.")

    post_data = request.get_json()
    title = post_data.get("title")
    author = post_data.get("author")
    review = post_data.get("review")
    recommend = post_data.get("recommend")
    user_id = post_data.get("user_id")

    record = Book(title, author, review, recommend, user_id)

    db.session.add(record)
    db.session.commit()

    return jsonify("Book Added")

@app.route("/book/get", methods=["GET"])
def get_all_books():
    all_books = db.session.query(Book).all()
    return jsonify(multiple_book_schema.dump(all_books))

@app.route("/book/get/<id>", methods=["GET"])
def get_book_by_id(id):
    book = db.session.query(Book).filter(Book.id == id).first()
    return jsonify(book_schema.dump(book))

@app.route("/book/get/user/<user_id>", methods=["GET"])
def get_all_books_by_user(user_id):
    all_books = db.session.query(Book).filter(Book.user_id == user_id).all()
    return jsonify(multiple_book_schema.dump(all_books))

@app.route("/book/update/<id>", methods=["PUT"])
def update_book(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON.")

    put_data = request.get_json()
    title = put_data.get("title")
    author = put_data.get("author")
    review = put_data.get("review")
    recommend = put_data.get("recommend")

    record = db.session.query(Book).filter(Book.id == id).first()

    if record is None:
        return jsonify(f"Error: No existing book with id {id}.")

    if title:
        record.title = title

    if author:
        record.author = author

    if review:
        record.review = review

    if recommend:
        record.recommend = recommend

    db.session.commit()

    return jsonify("Book Updated")

@app.route("/book/delete/<id>", methods=["DELETE"])
def delete_book(id):
    book = db.session.query(Book).filter(Book.id == id).first()
    db.session.delete(book)
    db.session.commit()
    return jsonify("Book Deleted")


if __name__ == "__main__":
    app.run(debug=True)