from models.user_model import User
from database.db import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity

# Use a single Bcrypt instance tied to the app via current_app context
bcrypt = Bcrypt()

def register_service(data):

    username = data.get('username')

    email = data.get('email')

    password = data.get('password')

    if not username or not email or not password:

        return {
            "message": "Username, email and password are required"
        }, 400

    # Check email already exists
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:

        return {
            "message": "Email already exists"
        }, 400

    # Password hashing using app-bound bcrypt
    from flask import current_app
    from flask_bcrypt import generate_password_hash

    hashed_password = generate_password_hash(password).decode('utf-8')

    user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    db.session.add(user)

    db.session.commit()

    return {
        "message": "User Registered Successfully"
    }, 201

def login_service(data):

    email = data.get('email')

    password = data.get('password')

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user:

        return {
            "message": "Invalid Email"
        }, 401

    # Check password using app-bound bcrypt
    from flask_bcrypt import check_password_hash

    password_check = check_password_hash(user.password, password)

    if not password_check:

        return {
            "message": "Invalid Password"
        }, 401

    # Create JWT token
    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "Login Successful",
        "token": access_token,
        "username": user.username
    }, 200

def profile_service():

    # Get current user id from token
    current_user_id = get_jwt_identity()

    # Find user
    user = User.query.get(int(current_user_id))

    if not user:

        return {
            "message": "User not found"
        }, 404

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }, 200
