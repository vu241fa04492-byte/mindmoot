from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from services.auth_service import (
    register_service,
    login_service,
    profile_service
)

auth_bp = Blueprint('auth_bp', __name__)



# Register API
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register User
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            username:
              type: string
              example: vennela
            email:
              type: string
              example: vennela@gmail.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
    """
    data = request.json
    return register_service(data)


# Login API
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login User
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            email:
              type: string
              example: vennela@gmail.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.json
    return login_service(data)


# Protected Profile API
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    User Profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: User profile details
      401:
        description: Unauthorized
    """
    return profile_service()