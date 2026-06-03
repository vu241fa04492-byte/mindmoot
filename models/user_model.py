from database.db import db


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # FIX: added unique=True to prevent duplicate usernames
    username = db.Column(db.String(100), unique=True, nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), default='user')

    debates = db.relationship(
        'Debate',
        backref='creator',
        lazy=True
    )

    arguments = db.relationship(
        'Argument',
        backref='user',
        lazy=True
    )

    votes = db.relationship(
        'Vote',
        backref='user',
        lazy=True
    )

    chat_messages = db.relationship(
        'ChatMessage',
        backref='sender',
        lazy=True
    )
