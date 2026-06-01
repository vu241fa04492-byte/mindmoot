from flask import Blueprint, request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from services.debate_service import (
    create_debate_service,
    get_all_debates_service,
    get_single_debate_service,
    delete_debate_service,
    submit_argument_service,
    get_debate_arguments_service,
    vote_debate_service,
    debate_results_service
)

debate_bp = Blueprint('debate_bp', __name__)

# ---------------- CREATE DEBATE ----------------

@debate_bp.route('/debates', methods=['POST'])
@jwt_required()
def create_debate():
    """
    Create Debate
    ---
    tags:
      - Debates
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            title:
              type: string
            description:
              type: string
            topic:
              type: string
    responses:
      201:
        description: Debate created successfully
    """
    data = request.json
    current_user = get_jwt_identity()

    return create_debate_service(
        data,
        current_user
    )


# ---------------- GET ALL DEBATES ----------------

@debate_bp.route('/debates', methods=['GET'])
def get_all_debates():
    """
    Get All Debates
    ---
    tags:
      - Debates
    responses:
      200:
        description: List of all debates
    """
    return get_all_debates_service()


# ---------------- GET SINGLE DEBATE ----------------

@debate_bp.route('/debates/<int:debate_id>', methods=['GET'])
def get_single_debate(debate_id):
    """
    Get Single Debate
    ---
    tags:
      - Debates
    parameters:
      - name: debate_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Debate details
    """
    return get_single_debate_service(
        debate_id
    )


# ---------------- DELETE DEBATE ----------------

@debate_bp.route('/debates/<int:debate_id>', methods=['DELETE'])
@jwt_required()
def delete_debate(debate_id):
    """
    Delete Debate
    ---
    tags:
      - Debates
    security:
      - Bearer: []
    parameters:
      - name: debate_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Debate deleted successfully
    """
    current_user = get_jwt_identity()

    return delete_debate_service(
        debate_id,
        current_user
    )


# ---------------- SUBMIT ARGUMENT ----------------

@debate_bp.route('/arguments', methods=['POST'])
@jwt_required()
def submit_argument():
    """
    Submit Argument
    ---
    tags:
      - Arguments
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            debate_id:
              type: integer
            content:
              type: string
    responses:
      201:
        description: Argument submitted successfully
    """
    data = request.json

    current_user = get_jwt_identity()

    return submit_argument_service(
        data,
        current_user
    )


# ---------------- GET DEBATE ARGUMENTS ----------------

@debate_bp.route(
    '/debates/<int:debate_id>/arguments',
    methods=['GET']
)
def get_debate_arguments(debate_id):
    """
    Get Debate Arguments
    ---
    tags:
      - Arguments
    parameters:
      - name: debate_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: List of debate arguments
    """
    return get_debate_arguments_service(
        debate_id
    )


# ---------------- VOTE API ----------------

@debate_bp.route('/vote', methods=['POST'])
@jwt_required()
def vote_debate():
    """
    Vote On Debate Argument
    ---
    tags:
      - Voting
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            argument_id:
              type: integer
    responses:
      201:
        description: Vote submitted successfully
    """
    data = request.json

    current_user = get_jwt_identity()

    return vote_debate_service(
        data,
        current_user
    )


# ---------------- RESULTS API ----------------

@debate_bp.route(
    '/debates/<int:debate_id>/results',
    methods=['GET']
)
def debate_results(debate_id):
    """
    Debate Results
    ---
    tags:
      - Results
    parameters:
      - name: debate_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Debate results and winner
    """
    return debate_results_service(
        debate_id
    )