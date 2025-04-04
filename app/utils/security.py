"""Security utilities for the TasksService API."""
import bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity


def hash_password(password):
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")


def check_password(password, hashed_password):
    """
    Check if the password matches the hash.

    Args:
        password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if the password matches the hash, False otherwise
    """
    if isinstance(password, str):
        password = password.encode("utf-8")
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password, hashed_password)


def generate_token(user_id):
    """
    Generate a JWT token for a user.

    Args:
        user_id: User ID

    Returns:
        JWT token
    """
    return create_access_token(identity=user_id)


def get_current_user_id():
    """
    Get the current user ID from the JWT token.

    Returns:
        User ID
    """
    return get_jwt_identity()
