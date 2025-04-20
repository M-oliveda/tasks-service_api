"""User service functions."""
from typing import Any, Dict, List, Optional

from flask import abort, current_app
from sqlalchemy import or_

from app.core.extensions import db
from app.models.user import User


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        user_id: User ID

    Returns:
        User object if found, None otherwise
    """
    return User.query.get(user_id)


def get_user_by_username(username: str) -> Optional[User]:
    """
    Get a user by username.

    Args:
        username: Username

    Returns:
        User object if found, None otherwise
    """
    return User.query.filter_by(username=username).first()


def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        email: Email address

    Returns:
        User object if found, None otherwise
    """
    return User.query.filter_by(email=email).first()


def get_user_by_username_or_email(username: str, email: str) -> Optional[User]:
    """
    Get a user by username or email.

    Args:
        username: Username
        email: Email address

    Returns:
        User object if found, None otherwise
    """
    return User.query.filter(
        or_(User.username == username, User.email == email)
    ).first()


def update_user(user: User, data: Dict[str, Any]) -> User:
    """
    Update a user's information.

    Args:
        user: User object to update
        data: Dictionary of user attributes to update

    Returns:
        Updated user object
    """
    try:
        # Handle special case for password
        if "password" in data and data["password"]:
            user.set_password(data["password"])
            del data["password"]

        # Update other fields
        for key, value in data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        current_app.logger.info(f"User {user.username} updated successfully")

        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update user {user.username}: {e}")
        raise abort(500, "Failed to update user")


def delete_user(user: User) -> bool:
    """
    Delete a user.

    Args:
        user: User object to delete

    Returns:
        True if deletion was successful
    """
    try:
        db.session.delete(user)
        db.session.commit()
        current_app.logger.info(f"User {user.username} deleted successfully")
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete user {user.username}: {e}")
        raise abort(500, "Failed to delete user")


def list_users(page: int = 1, per_page: int = 20) -> tuple[List[User], int]:
    """
    List users with pagination.

    Args:
        page: Page number
        per_page: Number of items per page

    Returns:
        Tuple of (list of users, total count)
    """
    query = User.query.order_by(User.created_at.desc())
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return users, total
