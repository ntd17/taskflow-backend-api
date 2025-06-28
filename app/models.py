from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    boards = db.relationship('Board', secondary='user_board', back_populates='members')

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lists = db.relationship('List', backref='board', lazy=True, cascade="all, delete-orphan")
    members = db.relationship('User', secondary='user_board', back_populates='boards')

class UserBoard(db.Model):
    __tablename__ = 'user_board'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), primary_key=True)

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    cards = db.relationship('Card', backref='list', lazy=True, cascade="all, delete-orphan")
    position = db.Column(db.Integer, nullable=False, default=0)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
