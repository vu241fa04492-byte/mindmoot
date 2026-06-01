from database.db import db

class Argument(db.Model):

    __tablename__ = 'arguments'

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    round_type = db.Column(
        db.String(50),
        default='opening'
    )

    debate_id = db.Column(
        db.Integer,
        db.ForeignKey('debates.id')
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )