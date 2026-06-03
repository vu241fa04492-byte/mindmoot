from flask import Blueprint, request, current_app

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
    debate_results_service,
    get_leaderboard_service
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
    return create_debate_service(data, current_user)


# ---------------- GET ALL DEBATES (with Search & Filter) ----------------

@debate_bp.route('/debates', methods=['GET'])
def get_all_debates():
    """
    Get All Debates
    ---
    tags:
      - Debates
    parameters:
      - name: search
        in: query
        type: string
        description: Keyword search in topic or description
      - name: status
        in: query
        type: string
        description: Filter by status (active/closed)
      - name: topic
        in: query
        type: string
        description: Filter by topic keyword
    responses:
      200:
        description: List of all debates
    """
    # ENHANCEMENT 3: read query params for search/filter
    search = request.args.get('search')
    status = request.args.get('status')
    topic = request.args.get('topic')

    return get_all_debates_service(search=search, status=status, topic=topic)


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
    return get_single_debate_service(debate_id)


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
    return delete_debate_service(debate_id, current_user)


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
    return submit_argument_service(data, current_user)


# ---------------- GET DEBATE ARGUMENTS ----------------

@debate_bp.route('/debates/<int:debate_id>/arguments', methods=['GET'])
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
    return get_debate_arguments_service(debate_id)


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
            debate_id:
              type: integer
            vote_type:
              type: string
    responses:
      201:
        description: Vote submitted successfully
    """
    data = request.json
    current_user = get_jwt_identity()

    # ENHANCEMENT 1: pass socketio so vote_debate_service can broadcast
    socketio = current_app.extensions.get('socketio')
    return vote_debate_service(data, current_user, socketio=socketio)


# ---------------- RESULTS API ----------------

@debate_bp.route('/debates/<int:debate_id>/results', methods=['GET'])
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
    return debate_results_service(debate_id)


# ---------------- LEADERBOARD API ----------------

@debate_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    """
    User Leaderboard
    ---
    tags:
      - Leaderboard
    parameters:
      - name: limit
        in: query
        type: integer
        description: Number of top users to return (default 10)
    responses:
      200:
        description: Top debaters ranked by votes received
    """
    # ENHANCEMENT 2: leaderboard endpoint
    limit = request.args.get('limit', 10, type=int)
    return get_leaderboard_service(limit=limit)
