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

bcrypt = Bcrypt(app)

# --------------------------------------------------
# SOCKET.IO
# --------------------------------------------------

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

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


@socketio.on('send_argument')
def send_argument(data):

    print("New Argument:", data)

    socketio.emit(
        'receive_argument',
        {
            'username': data.get('username'),
            'argument': data.get('argument')
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

debug=True
    
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)