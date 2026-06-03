from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.chat_model import ChatMessage
from models.user_model import User

chat_bp = Blueprint('chat_bp', __name__)


# ---------------- GET GLOBAL CHAT HISTORY ----------------

@chat_bp.route('/chat/global', methods=['GET'])
@jwt_required()
def get_global_chat():
    """
    Get Global Chat History
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - name: limit
        in: query
        type: integer
        description: Number of messages to return (default 50)
    responses:
      200:
        description: List of global chat messages
    """
    limit = request.args.get('limit', 50, type=int)
    messages = (
        ChatMessage.query
        .filter_by(debate_id=None)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return _serialize_messages(messages), 200


# ---------------- GET DEBATE CHAT HISTORY ----------------

@chat_bp.route('/chat/debate/<int:debate_id>', methods=['GET'])
@jwt_required()
def get_debate_chat(debate_id):
    """
    Get Debate Chat History
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - name: debate_id
        in: path
        required: true
        type: integer
      - name: limit
        in: query
        type: integer
        description: Number of messages to return (default 50)
    responses:
      200:
        description: List of debate chat messages
    """
    limit = request.args.get('limit', 50, type=int)
    messages = (
        ChatMessage.query
        .filter_by(debate_id=debate_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return _serialize_messages(messages), 200


def _serialize_messages(messages):
    output = []
    for m in messages:
        username = m.sender.username if m.sender else 'Unknown'
        output.append({
            'id': m.id,
            'content': m.content,
            'username': username,
            'user_id': m.user_id,
            'debate_id': m.debate_id,
            'created_at': m.created_at.isoformat() if m.created_at else None
        })
    return output
