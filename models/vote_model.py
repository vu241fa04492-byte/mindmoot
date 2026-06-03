from database.db import db
from datetime import datetime


class Vote(db.Model):

    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)

    vote_type = db.Column(
        db.String(20),
        nullable=False
    )

    # FIX: store creation time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    debate_id = db.Column(
        db.Integer,
        db.ForeignKey('debates.id'),
        nullable=False
    )

    # FIX: argument_id was completely missing — votes never linked to arguments
    argument_id = db.Column(
        db.Integer,
        db.ForeignKey('arguments.id'),
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # FIX: unique constraint prevents same user voting twice on same argument
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'debate_id', 'argument_id',
            name='uq_user_debate_argument_vote'
        ),
    )
