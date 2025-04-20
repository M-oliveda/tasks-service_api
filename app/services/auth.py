"""Authentication service functions."""
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from uuid import UUID

import jwt
from flask import abort, current_app
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.extensions import db
from app.models.user import RoleEnum, User


def register_user(username: str, email: str, password: str) -> Tuple[User, bool]:
    """
    Register a new user.

    Args:
        username: Username for the new user
        email: Email address for the new user
        password: Password for the new user

    Returns:
        Tuple of (user, created).
        created is a boolean indicating if a new user was created
    """
    existing_user = (
        db.session.query(User)
        .filter((User.username == username) | (User.email == email))
        .first()
    )

    if existing_user:
        abort(400, "User already exists")

    try:
        user = User(username=username, email=email, role=RoleEnum.USER)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        current_app.logger.info(f"User {username} registered successfully")

        return user, True
    except IntegrityError:
        db.session.rollback()
        current_app.logger.error(f"Failed to create user {username}")
        raise abort(500, "Failed to create user")


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.

    Args:
        username: Username or email of the user
        password: Password to check

    Returns:
        User object if authentication is successful, None otherwise
    """
    user = (
        db.Query(User)
        .filter((User.username == username) | (User.email == username))
        .first()
    )

    if not user:
        return None

    if not user.check_password(password):
        return None

    # Update last login timestamp
    user.update_last_login()

    current_app.logger.info(
        f"User {username} authenticated successfully at {user.last_login}"
    )

    return user


def create_access_token(
    user_id: UUID, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token for the user.

    Args:
        user_id: ID of the user
        expires_delta: Optional timedelta for token expiration

    Returns:
        JWT token string
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRES)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
    )


def decode_token(token: str) -> Dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        jwt.PyJWTError: If token is invalid
    """
    settings = get_settings()
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
    )


def get_current_user_id_from_token(token: str) -> Optional[int]:
    """
    Get the user ID from a token.

    Args:
        token: JWT token string

    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            return None
        return sub
    except (jwt.PyJWTError, ValueError):
        return None


def get_current_user_from_token(token: str) -> Optional[User]:
    """
    Get the user from a token.

    Args:
        token: JWT token string

    Returns:
        User object if token is valid, None otherwise
    """
    user_id = get_current_user_id_from_token(token)
    if user_id:
        user = db.Query(User).filter(User.id == user_id).first()
        if user:
            return user
    return None
