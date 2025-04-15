"""Task API endpoints."""
from uuid import UUID

from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.schemas.task import TaskCreate, TaskSearchParams, TaskUpdate
from app.services.task import (
    add_tag_to_task,
    create_task,
    delete_task,
    get_task_by_id,
    get_task_stats,
    list_tasks,
    remove_tag_from_task,
    search_tasks,
    update_task,
)

from .auth_decorators import login_required

task_bp = Blueprint("tasks", __name__, url_prefix="/")


@task_bp.route("", methods=["POST"])
@login_required
def create_new_task():
    """Create a new task."""
    data = request.get_json()

    try:
        task_data = TaskCreate.model_validate(data)
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400

    try:
        task = create_task(
            user_id=g.current_user_id,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            due_date=task_data.due_date,
            category_id=task_data.category_id if task_data.category_id else None,
            tag_ids=task_data.tag_ids,
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Task created successfully",
                    "data": task.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@task_bp.route("", methods=["GET"])
@login_required
def get_tasks():
    """List all tasks for the current user."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    try:
        tasks, total = list_tasks(
            user_id=g.current_user_id, page=page, per_page=per_page
        )

        return jsonify(
            {
                "status": "success",
                "data": [task.to_dict() for task in tasks],
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@task_bp.route("/search", methods=["GET"])
@login_required
def search_user_tasks():
    """Search tasks with filters."""
    query_params = request.args.to_dict(flat=False)

    # Convert flat dict to expected format for Pydantic
    single_values = {k: v[0] for k, v in query_params.items() if len(v) == 1}
    multiple_values = {k: v for k, v in query_params.items() if len(v) > 1}

    data = {**single_values, **multiple_values}

    # Handle boolean conversion for is_overdue
    if "is_overdue" in data:
        data["is_overdue"] = data["is_overdue"].lower() == "true"

    try:
        search_params = TaskSearchParams.model_validate(data)

        tasks, total = search_tasks(
            user_id=g.current_user_id, **search_params.model_dump()
        )

        return jsonify(
            {
                "status": "success",
                "data": [task.to_dict() for task in tasks],
                "page": search_params.page,
                "per_page": search_params.per_page,
                "total": total,
                "pages": (total + search_params.per_page - 1) // search_params.per_page,
            }
        )
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@task_bp.route("/stats", methods=["GET"])
@login_required
def get_tasks_stats():
    """Get task statistics for the current user."""
    try:
        stats = get_task_stats(g.current_user_id)
        return jsonify({"status": "success", "data": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@task_bp.route("/<uuid:task_id>", methods=["GET"])
@login_required
def get_task(task_id: UUID):
    """Get a specific task by ID."""
    task = get_task_by_id(task_id, g.current_user_id)
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    return jsonify({"status": "success", "data": task.to_dict()})


@task_bp.route("/<uuid:task_id>", methods=["PUT"])
@login_required
def update_task_by_id(task_id: UUID):
    """Update a specific task by ID."""
    task = get_task_by_id(task_id, g.current_user_id)
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    data = request.get_json()

    try:
        task_data = TaskUpdate.model_validate(data)
    except ValidationError as e:
        return jsonify({"status": "error", "message": e.errors()}), 400

    try:
        updated_task = update_task(task, task_data.model_dump(exclude_unset=True))
        return jsonify(
            {
                "status": "success",
                "message": "Task updated successfully",
                "data": updated_task.to_dict(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@task_bp.route("/<uuid:task_id>", methods=["DELETE"])
@login_required
def delete_task_by_id(task_id: UUID):
    """Delete a specific task by ID."""
    task = get_task_by_id(task_id, g.current_user_id)
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    try:
        delete_task(task)
        return jsonify({"status": "success", "message": "Task deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@task_bp.route("/<uuid:task_id>/tags/<uuid:tag_id>", methods=["POST"])
@login_required
def add_tag(task_id: UUID, tag_id: UUID):
    """Add a tag to a task."""
    task = get_task_by_id(task_id, g.current_user_id)
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    if add_tag_to_task(task, tag_id):
        return jsonify(
            {"status": "success", "message": "Tag added to task successfully"}
        )
    else:
        return jsonify({"status": "error", "message": "Failed to add tag to task"}), 400


@task_bp.route("/<uuid:task_id>/tags/<uuid:tag_id>", methods=["DELETE"])
@login_required
def remove_tag(task_id: UUID, tag_id: UUID):
    """Remove a tag from a task."""
    task = get_task_by_id(task_id, g.current_user_id)
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    if remove_tag_from_task(task, tag_id):
        return jsonify(
            {"status": "success", "message": "Tag removed from task successfully"}
        )
    else:
        return (
            jsonify({"status": "error", "message": "Failed to remove tag from task"}),
            400,
        )
