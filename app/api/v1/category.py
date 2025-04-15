"""Category API endpoints."""
from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import (
    create_category,
    delete_category,
    get_category_by_id,
    get_category_stats,
    list_categories,
    update_category,
)

from .auth_decorators import login_required

category_bp = Blueprint("categories", __name__, url_prefix="/")


@category_bp.route("", methods=["POST"])
@login_required
def create_new_category():
    """Create a new category."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON body"}), 400

    try:
        category_data = CategoryCreate(**data)
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400

    try:
        category = create_category(
            user_id=g.current_user_id,
            name=category_data.name,
            description=category_data.description,
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Category created successfully",
                    "data": category.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@category_bp.route("", methods=["GET"])
@login_required
def get_categories():
    """List all categories for the current user."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    sort_by = request.args.get("sort_by", "name")
    sort_order = request.args.get("sort_order", "asc")

    try:
        categories, total = list_categories(
            user_id=g.current_user_id,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page,
        )

        return jsonify(
            {
                "status": "success",
                "data": [category.to_dict() for category in categories],
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@category_bp.route("/stats", methods=["GET"])
@login_required
def get_categories_stats():
    """Get statistics for all categories."""
    try:
        stats = get_category_stats(g.current_user_id)
        return jsonify({"status": "success", "data": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@category_bp.route("/<uuid:category_id>", methods=["GET"])
@login_required
def get_category(category_id):
    """Get a specific category by ID."""
    category = get_category_by_id(category_id, g.current_user_id)
    if not category:
        return jsonify({"status": "error", "message": "Category not found"}), 404

    return jsonify({"status": "success", "data": category.to_dict()})


@category_bp.route("/<uuid:category_id>", methods=["PUT"])
@login_required
def update_category_by_id(category_id):
    """Update a specific category by ID."""
    category = get_category_by_id(category_id, g.current_user_id)
    if not category:
        return jsonify({"status": "error", "message": "Category not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON body"}), 400

    try:
        category_data = CategoryUpdate(**data)
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400

    try:
        updated_category = update_category(
            category, category_data.dict(exclude_unset=True)
        )
        return jsonify(
            {
                "status": "success",
                "message": "Category updated successfully",
                "data": updated_category.to_dict(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@category_bp.route("/<uuid:category_id>", methods=["DELETE"])
@login_required
def delete_category_by_id(category_id):
    """Delete a specific category by ID."""
    category = get_category_by_id(category_id, g.current_user_id)
    if not category:
        return jsonify({"status": "error", "message": "Category not found"}), 404

    try:
        delete_category(category)
        return jsonify(
            {"status": "success", "message": "Category deleted successfully"}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
