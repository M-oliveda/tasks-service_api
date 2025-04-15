"""Task service functions."""
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from flask import abort, current_app
from sqlalchemy import and_, asc, desc, or_

from app.core.extensions import db
from app.models import Task, TaskTag
from app.schemas.task import StatusEnum


def create_task(
    user_id: UUID,
    title: str,
    description: Optional[str] = None,
    status: StatusEnum = StatusEnum.TODO,
    priority: Optional[Any] = None,
    due_date: Optional[date] = None,
    category_id: Optional[UUID] = None,
    tag_ids: Optional[List[UUID]] = None,
) -> Task:
    """
    Create a new task.

    Args:
        user_id: ID of the user creating the task
        title: Task title
        description: Task description
        status: Task status
        priority: Task priority
        due_date: Task due date
        category_id: ID of the category for the task
        tag_ids: List of tag IDs to associate with the task

    Returns:
        Created task object
    """
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        category_id=category_id,
    )

    try:
        db.session.add(task)

        # Add task tags if provided
        if tag_ids:
            for tag_id in tag_ids:
                from .tag import get_tag_by_id

                tag = get_tag_by_id(tag_id, user_id)
                if tag:
                    task.add_tag(tag)

        db.session.commit()
        current_app.logger.info(f"Task {title} created successfully")
        return task
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to create task {title}: {e}")
        raise abort(500, "Failed to create task")


def get_task_by_id(task_id: UUID, user_id: int) -> Optional[Task]:
    """
    Get a task by ID for a specific user.

    Args:
        task_id: Task ID
        user_id: User ID

    Returns:
        Task object if found, None otherwise
    """
    return Task.query.filter_by(id=task_id, user_id=user_id).first()


def update_task(task: Task, data: Dict[str, Any]) -> Task:
    """
    Update a task.

    Args:
        task: Task object to update
        data: Dictionary of task attributes to update

    Returns:
        Updated task object
    """
    # Handle tag_ids separately
    tag_ids = data.pop("tag_ids", None)

    try:
        # Update task attributes
        for key, value in data.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        # Update tags if provided
        if tag_ids is not None:
            # Clear existing tags
            for task_tag in task.task_tags:
                db.session.delete(task_tag)

            # Add new tags
            from .tag import get_tag_by_id

            for tag_id in tag_ids:
                tag = get_tag_by_id(tag_id, task.user_id)
                if tag:
                    task.add_tag(tag)

        db.session.commit()
        current_app.logger.info(f"Task {task.title} updated successfully")
        return task
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update task: {e}")
        raise abort(500, "Failed to update task")


def delete_task(task: Task) -> bool:
    """
    Delete a task.

    Args:
        task: Task object to delete

    Returns:
        True if deletion was successful
    """
    try:
        db.session.delete(task)
        db.session.commit()
        current_app.logger.info(f"Task {task.title} deleted successfully")
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete task: {e}")
        raise abort(500, "Failed to delete task")


def list_tasks(
    user_id: int, page: int = 1, per_page: int = 20
) -> Tuple[List[Task], int]:
    """
    List tasks for a user with pagination.

    Args:
        user_id: User ID
        page: Page number
        per_page: Number of items per page

    Returns:
        Tuple of (list of tasks, total count)
    """
    query = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc())
    total = query.count()
    tasks = query.offset((page - 1) * per_page).limit(per_page).all()
    return tasks, total


def search_tasks(
    user_id: int,
    title: Optional[str] = None,
    status: Optional[StatusEnum] = None,
    priority: Optional[Any] = None,
    category_id: Optional[int] = None,
    tag_ids: Optional[List[int]] = None,
    is_overdue: Optional[bool] = None,
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> Tuple[List[Task], int]:
    """
    Search tasks with filters.

    Args:
        user_id: User ID
        title: Filter by title (partial match)
        status: Filter by status
        priority: Filter by priority
        category_id: Filter by category ID
        tag_ids: Filter by tag IDs (tasks with any of these tags)
        is_overdue: Filter by overdue status
        due_date_from: Filter by due date (from)
        due_date_to: Filter by due date (to)
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        page: Page number
        per_page: Number of items per page

    Returns:
        Tuple of (list of tasks, total count)
    """
    query = Task.query.filter_by(user_id=user_id)

    # Apply filters
    if title:
        query = query.filter(Task.title.ilike(f"%{title}%"))

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if category_id:
        query = query.filter(Task.category_id == category_id)

    if tag_ids:
        query = query.join(Task.task_tags).filter(
            Task.task_tags.any(TaskTag.tag_id.in_(tag_ids))
        )

    if is_overdue is not None:
        today = datetime.now().date()
        if is_overdue:
            query = query.filter(and_(Task.due_date.isnot(None), Task.due_date < today))
        else:
            query = query.filter(or_(Task.due_date.is_(None), Task.due_date >= today))

    if due_date_from:
        query = query.filter(Task.due_date >= due_date_from)

    if due_date_to:
        query = query.filter(Task.due_date <= due_date_to)

    # Apply sorting
    if hasattr(Task, sort_by):
        sort_attr = getattr(Task, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_attr))
        else:
            query = query.order_by(asc(sort_attr))

    # Apply pagination
    total = query.count()
    tasks = query.offset((page - 1) * per_page).limit(per_page).all()

    return tasks, total


def add_tag_to_task(task: Task, tag_id: UUID) -> bool:
    """
    Add a tag to a task.

    Args:
        task: Task object
        tag_id: Tag ID

    Returns:
        True if tag was added successfully
    """
    from .tag import get_tag_by_id

    tag = get_tag_by_id(tag_id, task.user_id)
    if not tag:
        return False

    task.add_tag(tag)
    db.session.commit()
    return True


def remove_tag_from_task(task: Task, tag_id: UUID) -> bool:
    """
    Remove a tag from a task.

    Args:
        task: Task object
        tag_id: Tag ID

    Returns:
        True if tag was removed successfully
    """
    from .tag import get_tag_by_id

    tag = get_tag_by_id(tag_id, task.user_id)
    if not tag:
        return False

    task.remove_tag(tag)
    db.session.commit()
    return True


def get_task_stats(user_id: int) -> Dict[str, Any]:
    """
    Get task statistics for a user.

    Args:
        user_id: User ID

    Returns:
        Dictionary of task statistics
    """
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(
        user_id=user_id, status=StatusEnum.READY
    ).count()

    today = datetime.now().date()
    overdue_tasks = Task.query.filter(
        Task.user_id == user_id, Task.due_date < today, Task.status != StatusEnum.READY
    ).count()

    due_today = Task.query.filter(
        Task.user_id == user_id, Task.due_date == today
    ).count()

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "due_today": due_today,
        "completion_rate": round((completed_tasks / total_tasks * 100), 2)
        if total_tasks > 0
        else 100.0,
    }
