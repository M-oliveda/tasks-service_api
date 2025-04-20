"""Authentication decorators for route protection."""
from functools import wraps

from flask import abort, g, request

from app.schemas.user import RoleEnum
from app.services.auth import get_current_user_from_token


def get_token_from_header():
    """Extract token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    return auth_header.split(" ")[1]


def login_required(f):
    """Check if the user is logged in."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            abort(401, "Authentication token required")

        try:
            user = get_current_user_from_token(token)
            if not user:
                abort(401, "Invalid authentication token")

            # Set the current user in flask.g for access in route handlers
            g.current_user = user
            g.current_user_id = user.id

            return f(*args, **kwargs)
        except Exception as e:
            abort(401, f"Authentication error: {str(e)}")

    return decorated_function


def admin_required(f):
    """Check if user is an admin."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is logged in
        login_required(lambda: None)()

        # Then check if user is admin
        if g.current_user.role != RoleEnum.ADMIN:
            abort(403, "Admin access required")

        return f(*args, **kwargs)

    return decorated_function
