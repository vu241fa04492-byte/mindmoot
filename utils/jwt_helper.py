# FIX: file was completely empty — added get_current_user_id helper
from flask_jwt_extended import get_jwt_identity


def get_current_user_id() -> int:
    """Return the current authenticated user's ID as an integer."""
    return int(get_jwt_identity())
