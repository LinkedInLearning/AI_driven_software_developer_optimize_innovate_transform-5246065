import os
import uuid

import click
from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user
from marshmallow import Schema, fields, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f"sqlite:///{os.path.join(BASE_DIR, 'statuses.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()

login_manager.init_app(app)


class Author(db.Model):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    handle = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    slug = Column(String, default=lambda: str(uuid.uuid4()))
    status = db.relationship('Status', backref='author', lazy='dynamic')

    def set_password(self, password):
        raise NotImplementedError('Must implement with hashing')

    def check_password(self, password):
        return NotImplementedError('Must implement with hash check')

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Status(db.Model):
    __tablename__ = 'statuse'
    id = Column(Integer, primary_key=True)
    slug = Column(String, default=lambda: str(uuid.uuid4()))
    text = Column(String(length=55))
    author_id = db.Column(Integer, db.ForeignKey('authors.id'))


def init_db():
    db.create_all()
    click.secho('DB created succesful', bg='green')


@app.cli.command('create_db')
def create_db():
    init_db()


@app.cli.command('seed_db')
def seed_db():
    author = Author(handle='foo', email='fooo@example.com', password='passs')
    status_1 = Status(text='foooo', author_id=author.id)
    status_2 = Status(text='foooo baz', author_id=author.id)
    db.session.add(author)
    db.session.add(status_1)
    db.session.add(status_2)


class RegesterAuthorSchema(Schema):
    handle = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True)


class LoginAuthorSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(load_only=True)


@login_manager.user_loader
def load_user(user_id):
    return Author.query.filter_by(id=user_id).first()


@app.post('/register')
def register():
    try:
        schema = RegesterAuthorSchema()
        data = schema.load(request.json)
        email = data['email']
        author_exists = Author.query.filter_by(email=email).first()
        if author_exists:
            return jsonify(message='cannot create user'), 409

        handle = data['handle']
        author = Author(handle=handle, email=email)
        author.set_password(data['password'])
        db.session.add(author)
        db.session.commit()
        return jsonify(message='registration successful'), 201

    except ValidationError as error:
        return jsonify(error.messages), 409


@app.post('/login')
def login():
    try:
        schema = LoginAuthorSchema()
        data = schema.load(request.json)
        email = data['email']
        author = Author.query.filter_by(email=email).first()
        if not author:
            return jsonify(message='wrong credentials')
        if author.check_password(data['password']):
            login_user(author)
            return jsonify(message='success'), 200
        else:
            return jsonify(message='wrong credentials'), 401  # TODO status
    except ValidationError as error:
        return jsonify(error.messages), 409


@app.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify(message='success'), 200


@app.get('/confidential')
@login_required
def confidential():
    return jsonify(
        [
            {'secret_one': 'The moon is made of cheese.'},
            {'secret_two': 'The tooth fairy is real.'},
        ]
    )


app.run(debug=True)