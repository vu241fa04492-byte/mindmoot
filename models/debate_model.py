from database.db import db
from datetime import datetime


class Debate(db.Model):

    __tablename__ = 'debates'

    id = db.Column(db.Integer, primary_key=True)

    topic = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text)

    status = db.Column(db.String(20), default='active')

    # FIX: store creation time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    # FIX: cascade so deleting a debate removes its arguments & votes
    arguments = db.relationship(
        'Argument',
        backref='debate',
        lazy=True,
        cascade='all, delete-orphan'
    )

    votes = db.relationship(
        'Vote',
        backref='debate',
        lazy=True,
        cascade='all, delete-orphan'
    )
