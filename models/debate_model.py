from database.db import db

class Debate(db.Model):

    __tablename__ = 'debates'

    id = db.Column(db.Integer, primary_key=True)

    topic = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text)

    status = db.Column(db.String(20), default='active')

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    arguments = db.relationship(
        'Argument',
        backref='debate',
        lazy=True
    )

    votes = db.relationship(
        'Vote',
        backref='debate',
        lazy=True
    )

