"""User API endpoints."""
from os import getenv

from flask import Blueprint, g, jsonify, request

from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserUpdate
from app.services.auth import authenticate_user, create_access_token, register_user
from app.services.user import (
    delete_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    list_users,
    update_user,
)

from .auth_decorators import admin_required, login_required

user_bp = Blueprint("users", __name__, url_prefix="/")

TOKEN_TYPE = getenv("TOKEN_TYPE", "bearer")


@user_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON payload"}), 400

    try:
        user_data = UserCreate(**data)
    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400

    if get_user_by_username(user_data.username) or get_user_by_email(user_data.email):
        return (
            jsonify({"status": "error", "message": "Username or email already exists"}),
            409,
        )

    try:
        user, _ = register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )
        token = create_access_token(user.id)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "User registered successfully",
                    "data": TokenResponse(
                        access_token=token, token_type=TOKEN_TYPE, expires_in=3600
                    ).model_dump(),
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user and return a token."""
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON payload"}), 400

    try:
        user_data = UserLogin(**data)
    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400

    user = authenticate_user(user_data.username, user_data.password)
    if not user:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    token = create_access_token(user.id)

    return jsonify(
        {
            "status": "success",
            "message": "Login successful",
            "data": TokenResponse(
                access_token=token, token_type=TOKEN_TYPE, expires_in=3600
            ).dict(),
        }
    )


@user_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Get the current authenticated user."""
    return jsonify({"status": "success", "data": g.current_user.to_dict()})


@user_bp.route("/me", methods=["PUT"])
@login_required
def update_current_user():
    """Update the current authenticated user."""
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON payload"}), 400

    try:
        user_data = UserUpdate(**data)
    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400

    try:
        updated_user = update_user(g.current_user, user_data.dict(exclude_unset=True))
        return jsonify(
            {
                "status": "success",
                "message": "User updated successfully",
                "data": updated_user.to_dict(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route("/me", methods=["DELETE"])
@login_required
def delete_current_user():
    """Delete the current authenticated user."""
    try:
        delete_user(g.current_user)
        return jsonify({"status": "success", "message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route("", methods=["GET"])
@admin_required
def get_users():
    """List all users (admin only)."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    try:
        users, total = list_users(page=page, per_page=per_page)
        return jsonify(
            {
                "status": "success",
                "data": [user.to_dict() for user in users],
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route("/<uuid:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    """Get a specific user by ID (admin only)."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    return jsonify({"status": "success", "data": user.to_dict()})


@user_bp.route("/<uuid:user_id>", methods=["PUT"])
@admin_required
def update_user_by_id(user_id):
    """Update a specific user by ID (admin only)."""
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON payload"}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    try:
        user_data = UserUpdate(**data)
    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400

    try:
        updated_user = update_user(user, user_data.dict(exclude_unset=True))
        return jsonify(
            {
                "status": "success",
                "message": "User updated successfully",
                "data": updated_user.to_dict(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route("/<uuid:user_id>", methods=["DELETE"])
@admin_required
def delete_user_by_id(user_id):
    """Delete a specific user by ID (admin only)."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    try:
        delete_user(user)
        return jsonify({"status": "success", "message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
