"""Tag API endpoints."""
from uuid import UUID

from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.schemas.tag import TagCreate, TagUpdate
from app.services.tag import (
    create_tag,
    delete_tag,
    get_tag_by_id,
    get_tag_by_name,
    get_tag_stats,
    list_tags,
    update_tag,
)

from .auth_decorators import login_required

tag_bp = Blueprint("tags", __name__, url_prefix="/tags")


@tag_bp.route("", methods=["POST"])
@login_required
def create_new_tag():
    """Create a new tag."""
    data = request.get_json(silent=True) or {}

    try:
        tag_data = TagCreate(**data)
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400

    # Check if tag with same name already exists
    if get_tag_by_name(tag_data.name, g.current_user_id):
        return jsonify({"status": "error", "message": "Tag already exists"}), 409

    try:
        tag = create_tag(user_id=g.current_user_id, name=tag_data.name)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Tag created successfully",
                    "data": tag.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@tag_bp.route("", methods=["GET"])
@login_required
def get_tags():
    """List all tags for the current user."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    sort_by = request.args.get("sort_by", "name")
    sort_order = request.args.get("sort_order", "asc")

    try:
        tags, total = list_tags(
            user_id=g.current_user_id,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page,
        )

        return jsonify(
            {
                "status": "success",
                "data": [tag.to_dict() for tag in tags],
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@tag_bp.route("/stats", methods=["GET"])
@login_required
def get_tags_stats():
    """Get statistics for all tags."""
    try:
        stats = get_tag_stats(g.current_user_id)
        return jsonify({"status": "success", "data": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@tag_bp.route("/<uuid:tag_id>", methods=["GET"])
@login_required
def get_tag(tag_id: UUID):
    """Get a specific tag by ID."""
    tag = get_tag_by_id(tag_id, g.current_user_id)
    if not tag:
        return jsonify({"status": "error", "message": "Tag not found"}), 404

    return jsonify({"status": "success", "data": tag.to_dict()})


@tag_bp.route("/<uuid:tag_id>", methods=["PUT"])
@login_required
def update_tag_by_id(tag_id: UUID):
    """Update a specific tag by ID."""
    tag = get_tag_by_id(tag_id, g.current_user_id)
    if not tag:
        return jsonify({"status": "error", "message": "Tag not found"}), 404

    data = request.get_json(silent=True) or {}

    try:
        tag_data = TagUpdate(**data)
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400

    # Check if new tag name already exists (if name is being changed)
    if tag_data.name and tag_data.name != tag.name:
        existing_tag = get_tag_by_name(tag_data.name, g.current_user_id)
        if existing_tag:
            return (
                jsonify({"status": "error", "message": "Tag name already exists"}),
                409,
            )

    try:
        updated_tag = update_tag(tag, tag_data.model_dump(exclude_unset=True))
        return jsonify(
            {
                "status": "success",
                "message": "Tag updated successfully",
                "data": updated_tag.to_dict(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@tag_bp.route("/<uuid:tag_id>", methods=["DELETE"])
@login_required
def delete_tag_by_id(tag_id: UUID):
    """Delete a specific tag by ID."""
    tag = get_tag_by_id(tag_id, g.current_user_id)
    if not tag:
        return jsonify({"status": "error", "message": "Tag not found"}), 404

    try:
        delete_tag(tag)
        return jsonify({"status": "success", "message": "Tag deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
