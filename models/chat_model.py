from database.db import db
from datetime import datetime


class ChatMessage(db.Model):

    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # NULL = global chat, set = debate-specific chat
    debate_id = db.Column(
        db.Integer,
        db.ForeignKey('debates.id'),
        nullable=True
    )
