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
        user_id=int(user_id)
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

        # FIX: guard against orphaned debate (creator deleted) to prevent crash
        created_by = debate.creator.username if debate.creator else "Unknown"

        output.append({
            "id": debate.id,
            "topic": debate.topic,
            "description": debate.description,
            "status": debate.status,
            # FIX: include created_at in response
            "created_at": debate.created_at.isoformat() if debate.created_at else None,
            "created_by": created_by
        })

    return output, 200


def get_single_debate_service(debate_id):

    debate = Debate.query.get(debate_id)

    if not debate:

        return {
            "message": "Debate not found"
        }, 404

    created_by = debate.creator.username if debate.creator else "Unknown"

    return {
        "id": debate.id,
        "topic": debate.topic,
        "description": debate.description,
        "status": debate.status,
        "created_at": debate.created_at.isoformat() if debate.created_at else None,
        "created_by": created_by
    }, 200


def delete_debate_service(debate_id, user_id):

    debate = Debate.query.get(debate_id)

    if not debate:

        return {
            "message": "Debate not found"
        }, 404

    # Check ownership
    if debate.user_id != int(user_id):

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

    # FIX: reject arguments on closed debates
    if debate.status != 'active':

        return {
            "message": "Debate is closed, no more arguments allowed"
        }, 400

    argument = Argument(
        content=content,
        round_type=round_type,
        debate_id=int(debate_id),
        user_id=int(user_id)
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

        # FIX: guard if user was deleted
        username = argument.user.username if argument.user else "Unknown"

        output.append({
            "id": argument.id,
            "content": argument.content,
            "round_type": argument.round_type,
            # FIX: include created_at
            "created_at": argument.created_at.isoformat() if argument.created_at else None,
            "username": username
        })

    return output, 200


def vote_debate_service(data, user_id):

    debate_id = data.get('debate_id')

    vote_type = data.get('vote_type')

    # FIX: read argument_id from request and actually store it
    argument_id = data.get('argument_id')

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

    # FIX: validate argument belongs to this debate if provided
    if argument_id:

        argument = Argument.query.get(argument_id)

        if not argument or argument.debate_id != int(debate_id):

            return {
                "message": "Argument not found in this debate"
            }, 404

    # FIX: duplicate-vote check now includes argument_id
    existing_vote = Vote.query.filter_by(
        debate_id=int(debate_id),
        user_id=int(user_id),
        argument_id=int(argument_id) if argument_id else None
    ).first()

    if existing_vote:

        return {
            "message": "You already voted on this"
        }, 400

    vote = Vote(
        debate_id=int(debate_id),
        user_id=int(user_id),
        vote_type=vote_type,
        # FIX: actually store argument_id so vote is linked to the argument
        argument_id=int(argument_id) if argument_id else None
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

    # FIX: include winner in results
    if total_for > total_against:
        winner = 'for'
    elif total_against > total_for:
        winner = 'against'
    else:
        winner = 'tie'

    return {
        "debate_topic": debate.topic,
        "votes_for": total_for,
        "votes_against": total_against,
        "winner": winner
    }, 200