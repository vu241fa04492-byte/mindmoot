from flask import jsonify
from models.debate_model import Debate
from database.db import db
from models.argument_model import Argument
from models.vote_model import Vote
from models.user_model import User
from sqlalchemy import func


# --------------------------------------------------
# DEBATE CRUD
# --------------------------------------------------

def create_debate_service(data, user_id):
    topic = data.get('topic')
    description = data.get('description')

    if not topic:
        return {"message": "Topic is required"}, 400

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


def get_all_debates_service(search=None, status=None, topic=None):
    """
    Get all debates with optional search/filter.
    - search: keyword match against topic or description
    - status: 'active' | 'closed'
    - topic: exact or partial topic match
    """
    query = Debate.query

    # ENHANCEMENT 3: Search & Filter
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Debate.topic.ilike(like)) | (Debate.description.ilike(like))
        )

    if status:
        query = query.filter(Debate.status == status)

    if topic:
        query = query.filter(Debate.topic.ilike(f"%{topic}%"))

    debates = query.order_by(Debate.created_at.desc()).all()

    output = []
    for debate in debates:
        created_by = debate.creator.username if debate.creator else "Unknown"

        votes_for = Vote.query.filter_by(debate_id=debate.id, vote_type='for').count()
        votes_against = Vote.query.filter_by(debate_id=debate.id, vote_type='against').count()

        output.append({
            "id": debate.id,
            "topic": debate.topic,
            "description": debate.description,
            "status": debate.status,
            "created_at": debate.created_at.isoformat() if debate.created_at else None,
            "created_by": created_by,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "total_votes": votes_for + votes_against
        })

    return output, 200


def get_single_debate_service(debate_id):
    debate = Debate.query.get(debate_id)
    if not debate:
        return {"message": "Debate not found"}, 404

    created_by = debate.creator.username if debate.creator else "Unknown"

    votes_for = Vote.query.filter_by(debate_id=debate.id, vote_type='for').count()
    votes_against = Vote.query.filter_by(debate_id=debate.id, vote_type='against').count()

    return {
        "id": debate.id,
        "topic": debate.topic,
        "description": debate.description,
        "status": debate.status,
        "created_at": debate.created_at.isoformat() if debate.created_at else None,
        "created_by": created_by,
        "votes_for": votes_for,
        "votes_against": votes_against
    }, 200


def delete_debate_service(debate_id, user_id):
    debate = Debate.query.get(debate_id)
    if not debate:
        return {"message": "Debate not found"}, 404

    if debate.user_id != int(user_id):
        return {"message": "Unauthorized Access"}, 403

    db.session.delete(debate)
    db.session.commit()

    return {"message": "Debate Deleted Successfully"}, 200


# --------------------------------------------------
# ARGUMENTS
# --------------------------------------------------

def submit_argument_service(data, user_id):
    content = data.get('content')
    round_type = data.get('round_type', 'opening')
    debate_id = data.get('debate_id')

    if not content or not debate_id:
        return {"message": "content and debate_id are required"}, 400

    debate = Debate.query.get(debate_id)
    if not debate:
        return {"message": "Debate not found"}, 404

    if debate.status != 'active':
        return {"message": "Debate is closed, no more arguments allowed"}, 400

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
        return {"message": "Debate not found"}, 404

    arguments = Argument.query.filter_by(debate_id=debate_id).all()

    output = []
    for argument in arguments:
        username = argument.user.username if argument.user else "Unknown"
        vote_count = Vote.query.filter_by(argument_id=argument.id).count()
        output.append({
            "id": argument.id,
            "content": argument.content,
            "round_type": argument.round_type,
            "created_at": argument.created_at.isoformat() if argument.created_at else None,
            "username": username,
            "vote_count": vote_count
        })

    return output, 200


# --------------------------------------------------
# VOTING
# --------------------------------------------------

def vote_debate_service(data, user_id, socketio=None):
    debate_id = data.get('debate_id')
    vote_type = data.get('vote_type')
    argument_id = data.get('argument_id')

    if not debate_id or not vote_type:
        return {"message": "debate_id and vote_type are required"}, 400

    if vote_type not in ('for', 'against'):
        return {"message": "vote_type must be 'for' or 'against'"}, 400

    debate = Debate.query.get(debate_id)
    if not debate:
        return {"message": "Debate not found"}, 404

    if argument_id:
        argument = Argument.query.get(argument_id)
        if not argument or argument.debate_id != int(debate_id):
            return {"message": "Argument not found in this debate"}, 404

    existing_vote = Vote.query.filter_by(
        debate_id=int(debate_id),
        user_id=int(user_id),
        argument_id=int(argument_id) if argument_id else None
    ).first()

    if existing_vote:
        return {"message": "You already voted on this"}, 400

    vote = Vote(
        debate_id=int(debate_id),
        user_id=int(user_id),
        vote_type=vote_type,
        argument_id=int(argument_id) if argument_id else None
    )
    db.session.add(vote)
    db.session.commit()

    # ENHANCEMENT 1: Live vote count broadcast via SocketIO
    votes_for = Vote.query.filter_by(debate_id=int(debate_id), vote_type='for').count()
    votes_against = Vote.query.filter_by(debate_id=int(debate_id), vote_type='against').count()

    if socketio:
        socketio.emit('vote_update', {
            'debate_id': int(debate_id),
            'votes_for': votes_for,
            'votes_against': votes_against,
            'total_votes': votes_for + votes_against,
            'last_vote_type': vote_type,
            'argument_id': argument_id
        }, room=f"debate_{debate_id}")

    return {
        "message": "Vote Submitted Successfully",
        "vote_id": vote.id,
        "votes_for": votes_for,
        "votes_against": votes_against
    }, 201


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

def debate_results_service(debate_id):
    debate = Debate.query.get(debate_id)
    if not debate:
        return {"message": "Debate not found"}, 404

    total_for = Vote.query.filter_by(debate_id=debate_id, vote_type='for').count()
    total_against = Vote.query.filter_by(debate_id=debate_id, vote_type='against').count()

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


# --------------------------------------------------
# ENHANCEMENT 2: LEADERBOARD
# --------------------------------------------------

def get_leaderboard_service(limit=10):
    """
    Rank users by total votes received on their arguments.
    Returns top `limit` users.
    """
    results = (
        db.session.query(
            User.id,
            User.username,
            func.count(Vote.id).label('total_votes_received'),
            func.count(func.distinct(Argument.debate_id)).label('debates_participated')
        )
        .join(Argument, Argument.user_id == User.id)
        .join(Vote, Vote.argument_id == Argument.id)
        .group_by(User.id, User.username)
        .order_by(func.count(Vote.id).desc())
        .limit(limit)
        .all()
    )

    leaderboard = []
    for rank, row in enumerate(results, start=1):
        leaderboard.append({
            "rank": rank,
            "user_id": row.id,
            "username": row.username,
            "total_votes_received": row.total_votes_received,
            "debates_participated": row.debates_participated
        })

    return {"leaderboard": leaderboard, "total_ranked": len(leaderboard)}, 200
