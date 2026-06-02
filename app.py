from flask import Flask, render_template
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

from config import Config
from database.db import db

from routes.auth_routes import auth_bp
from routes.debate_routes import debate_bp

from models.user_model import User
from models.debate_model import Debate
from models.argument_model import Argument
from models.vote_model import Vote

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

# FIX: single Bcrypt instance bound to app.
# auth_service.py previously created its own unbound Bcrypt() which caused
# password hashing and checking to be inconsistent, breaking login.
bcrypt = Bcrypt(app)

# --------------------------------------------------
# SOCKET.IO
# --------------------------------------------------


socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

# --------------------------------------------------
# BLUEPRINTS
# --------------------------------------------------

app.register_blueprint(auth_bp)
app.register_blueprint(debate_bp)

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route('/')
def home():
    return render_template('index.html')

# --------------------------------------------------
# SOCKET EVENTS
# --------------------------------------------------

@socketio.on('connect')
def handle_connect():
    print("User Connected")


@socketio.on('disconnect')
def handle_disconnect():
    print("User Disconnected")


@socketio.on('join_debate')
def join_debate(data):

    print("User Joined Debate Room")

    socketio.emit(
        'join_message',
        {
            'message': 'A user joined the debate'
        }
    )


# FIX: send_argument now saves the argument to the database.
# Previously it only broadcast via WebSocket — arguments were lost on refresh.
@socketio.on('send_argument')
def send_argument(data):

    from flask_jwt_extended import decode_token

    print("New Argument:", data)

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
        }
    )

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
        debug=False,
        allow_unsafe_werkzeug=True
    )