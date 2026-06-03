from database.db import db
from datetime import datetime


class Argument(db.Model):

    __tablename__ = 'arguments'

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    round_type = db.Column(
        db.String(50),
        default='opening'
    )

    # FIX: store creation time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    debate_id = db.Column(
        db.Integer,
        db.ForeignKey('debates.id'),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # FIX: votes relationship so arguments can be voted on
    votes = db.relationship(
        'Vote',
        backref='argument',
        lazy=True,
        cascade='all, delete-orphan'
    )
