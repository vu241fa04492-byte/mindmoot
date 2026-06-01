from database.db import db

class Vote(db.Model):

    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)

    vote_type = db.Column(
        db.String(20),
        nullable=False
    )

    debate_id = db.Column(
        db.Integer,
        db.ForeignKey('debates.id')
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )