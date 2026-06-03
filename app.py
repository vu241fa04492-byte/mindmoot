from flask import Flask, render_template
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, join_room, leave_room
from flask_bcrypt import Bcrypt

from config import Config
from database.db import db

from routes.auth_routes import auth_bp
from routes.debate_routes import debate_bp
from routes.chat_routes import chat_bp

from models.user_model import User
from models.debate_model import Debate
from models.argument_model import Argument
from models.vote_model import Vote
from models.chat_model import ChatMessage

# --------------------------------------------------
# FLASK APP
# --------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

db.init_app(app)

# --------------------------------------------------
# SWAGGER
# --------------------------------------------------

swagger = Swagger(app)

# --------------------------------------------------
# JWT
# --------------------------------------------------

jwt = JWTManager(app)

# --------------------------------------------------
# BCRYPT
# --------------------------------------------------

bcrypt = Bcrypt(app)

# --------------------------------------------------
# SOCKET.IO
# --------------------------------------------------

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

app.extensions['socketio'] = socketio

# --------------------------------------------------
# BLUEPRINTS
# --------------------------------------------------

app.register_blueprint(auth_bp)
app.register_blueprint(debate_bp)
app.register_blueprint(chat_bp)

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route('/')
def home():
    return render_template('index.html')

# --------------------------------------------------
# SOCKET EVENTS — DEBATE ROOMS
# --------------------------------------------------

@socketio.on('connect')
def handle_connect():
    print("User Connected")


@socketio.on('disconnect')
def handle_disconnect():
    print("User Disconnected")


@socketio.on('join_debate')
def join_debate(data):
    debate_id = data.get('debate_id')
    if debate_id:
        room = f"debate_{debate_id}"
        join_room(room)
        print(f"User joined room: {room}")
    socketio.emit(
        'join_message',
        {'message': 'A user joined the debate'},
        room=f"debate_{debate_id}" if debate_id else None
    )


@socketio.on('leave_debate')
def leave_debate(data):
    debate_id = data.get('debate_id')
    if debate_id:
        leave_room(f"debate_{debate_id}")


@socketio.on('send_argument')
def send_argument(data):
    from flask_jwt_extended import decode_token
    debate_id = data.get('debate_id')
    content = data.get('argument')
    token = data.get('token')
    round_type = data.get('round_type', 'opening')
    saved = False

    if debate_id and content and token:
        try:
            with app.app_context():
                decoded = decode_token(token)
                user_id = int(decoded['sub'])
                debate = Debate.query.get(int(debate_id))
                if debate and debate.status == 'active':
                    argument = Argument(
                        content=content,
                        round_type=round_type,
                        debate_id=int(debate_id),
                        user_id=user_id
                    )
                    db.session.add(argument)
                    db.session.commit()
                    saved = True
        except Exception as e:
            print("Error saving socket argument:", e)

    socketio.emit(
        'receive_argument',
        {
            'username': data.get('username'),
            'argument': content,
            'saved': saved
        },
        room=f"debate_{debate_id}" if debate_id else None
    )

# --------------------------------------------------
# SOCKET EVENTS — GLOBAL CHAT
# --------------------------------------------------

@socketio.on('join_global_chat')
def join_global_chat():
    join_room('global_chat')
    print("User joined global chat")


@socketio.on('leave_global_chat')
def leave_global_chat():
    leave_room('global_chat')


@socketio.on('send_chat_message')
def send_chat_message(data):
    from flask_jwt_extended import decode_token

    token = data.get('token')
    content = data.get('content', '').strip()
    debate_id = data.get('debate_id')  # None = global chat

    if not token or not content:
        return

    try:
        with app.app_context():
            decoded = decode_token(token)
            user_id = int(decoded['sub'])
            user = User.query.get(user_id)

            if not user:
                return

            msg = ChatMessage(
                content=content,
                user_id=user_id,
                debate_id=int(debate_id) if debate_id else None
            )
            db.session.add(msg)
            db.session.commit()

            payload = {
                'id': msg.id,
                'content': content,
                'username': user.username,
                'user_id': user_id,
                'debate_id': debate_id,
                'created_at': msg.created_at.isoformat()
            }

            # Broadcast to the right room
            if debate_id:
                socketio.emit('receive_chat_message', payload, room=f"debate_{debate_id}")
            else:
                socketio.emit('receive_chat_message', payload, room='global_chat')

    except Exception as e:
        print("Chat error:", e)

# --------------------------------------------------
# CREATE TABLES
# --------------------------------------------------

with app.app_context():
    db.create_all()

# --------------------------------------------------
# RUN APP
# --------------------------------------------------

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True
    )
