from models.debate_model import Debate
from database.db import db
from models.argument_model import Argument
from models.vote_model import Vote

def create_debate_service(data, user_id):

    topic = data.get('topic')

    description = data.get('description')

    if not topic:

        return {
            "message": "Topic is required"
        }, 400

    debate = Debate(
        topic=topic,
        description=description,
        user_id=int(user_id)          # FIX: JWT identity is string, cast to int
    )

    db.session.add(debate)

    db.session.commit()

    return {
        "message": "Debate Created Successfully",
        "debate_id": debate.id
    }, 201


def get_all_debates_service():

    debates = Debate.query.all()

    output = []

    for debate in debates:

        output.append({
            "id": debate.id,
            "topic": debate.topic,
            "description": debate.description,
            "status": debate.status,
            "created_by": debate.creator.username
        })

    return output, 200

def get_single_debate_service(debate_id):

    debate = Debate.query.get(debate_id)

    if not debate:

        return {
            "message": "Debate not found"
        }, 404

    return {
        "id": debate.id,
        "topic": debate.topic,
        "description": debate.description,
        "status": debate.status,
        "created_by": debate.creator.username
    }, 200

def delete_debate_service(debate_id, user_id):

    debate = Debate.query.get(debate_id)

    if not debate:

        return {
            "message": "Debate not found"
        }, 404

    # Check ownership
    if debate.user_id != int(user_id):            # FIX: cast user_id to int

        return {
            "message": "Unauthorized Access"
        }, 403

    db.session.delete(debate)

    db.session.commit()

    return {
        "message": "Debate Deleted Successfully"
    }, 200



def submit_argument_service(data, user_id):

    content = data.get('content')

    round_type = data.get('round_type', 'opening')

    debate_id = data.get('debate_id')

    if not content or not debate_id:

        return {
            "message": "content and debate_id are required"
        }, 400

    # Check debate exists
    debate = Debate.query.get(debate_id)

    if not debate:

        return {
            "message": "Debate not found"
        }, 404

    argument = Argument(
        content=content,
        round_type=round_type,
        debate_id=int(debate_id),
        user_id=int(user_id)          # FIX: cast user_id to int
    )

    db.session.add(argument)

    db.session.commit()

    return {
        "message": "Argument Submitted Successfully",
        "argument_id": argument.id
    }, 201

def get_debate_arguments_service(debate_id):

    debate = Debate.query.get(debate_id)

    if not debate:

        return {
            "message": "Debate not found"
        }, 404

    arguments = Argument.query.filter_by(
        debate_id=debate_id
    ).all()

    output = []

    for argument in arguments:

        output.append({
            "id": argument.id,
            "content": argument.content,
            "round_type": argument.round_type,
            "username": argument.user.username
        })

    return output, 200

def vote_debate_service(data, user_id):

    debate_id = data.get('debate_id')

    vote_type = data.get('vote_type')

    if not debate_id or not vote_type:

        return {
            "message": "debate_id and vote_type are required"
        }, 400

    if vote_type not in ('for', 'against'):

        return {
            "message": "vote_type must be 'for' or 'against'"
        }, 400

    # Check debate exists
    debate = Debate.query.get(debate_id)

    if not debate:

        return {
            "message": "Debate not found"
        }, 404

    # Prevent duplicate voting
    existing_vote = Vote.query.filter_by(
        debate_id=int(debate_id),
        user_id=int(user_id)          # FIX: cast user_id to int
    ).first()

    if existing_vote:

        return {
            "message": "You already voted"
        }, 400

    vote = Vote(
        debate_id=int(debate_id),
        user_id=int(user_id),         # FIX: cast user_id to int
        vote_type=vote_type
    )

    db.session.add(vote)

    db.session.commit()

    return {
        "message": "Vote Submitted Successfully",
        "vote_id": vote.id
    }, 201

def debate_results_service(debate_id):

    debate = Debate.query.get(debate_id)

    if not debate:

        return {
            "message": "Debate not found"
        }, 404

    total_for = Vote.query.filter_by(
        debate_id=debate_id,
        vote_type='for'
    ).count()

    total_against = Vote.query.filter_by(
        debate_id=debate_id,
        vote_type='against'
    ).count()

    return {
        "debate_topic": debate.topic,
        "votes_for": total_for,
        "votes_against": total_against
    }, 200
