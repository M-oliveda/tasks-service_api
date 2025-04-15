"""Category service functions."""
from typing import Any, Dict, List, Optional, Tuple

from flask import abort, current_app
from sqlalchemy import asc, desc

from app.core.extensions import db
from app.models import Category, Task
from app.schemas.task import StatusEnum


def create_category(
    user_id: int, name: str, description: Optional[str] = None
) -> Category:
    """
    Create a new category.

    Args:
        user_id: ID of the user creating the category
        name: Category name
        description: Category description

    Returns:
        Created category object
    """
    category = Category(user_id=user_id, name=name, description=description)

    try:
        db.session.add(category)
        db.session.commit()
        current_app.logger.info(f"Category {name} created successfully")
        return category
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to create category {name}: {e}")
        raise abort(500, "Failed to create category")


def get_category_by_id(category_id: int, user_id: int) -> Optional[Category]:
    """
    Get a category by ID for a specific user.

    Args:
        category_id: Category ID
        user_id: User ID

    Returns:
        Category object if found, None otherwise
    """
    return Category.query.filter_by(id=category_id, user_id=user_id).first()


def update_category(category: Category, data: Dict[str, Any]) -> Category:
    """
    Update a category.

    Args:
        category: Category object to update
        data: Dictionary of category attributes to update

    Returns:
        Updated category object
    """
    for key, value in data.items():
        if hasattr(category, key) and value is not None:
            setattr(category, key, value)

    try:
        db.session.commit()
        current_app.logger.info(f"Category {category.name} updated successfully")
        return category
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update category: {e}")
        raise abort(500, "Failed to update category")


def delete_category(category: Category) -> bool:
    """
    Delete a category. This will remove the category from all tasks.

    Args:
        category: Category object to delete

    Returns:
        True if deletion was successful
    """
    # Delete the category
    try:
        db.session.delete(category)
        db.session.commit()
        current_app.logger.info(f"Category {category.name} deleted successfully")
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete category: {e}")
        raise abort(500, "Failed to delete category")


def list_categories(
    user_id: int,
    sort_by: str = "name",
    sort_order: str = "asc",
    page: int = 1,
    per_page: int = 20,
) -> Tuple[List[Category], int]:
    """
    List categories for a user with pagination.

    Args:
        user_id: User ID
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        page: Page number
        per_page: Number of items per page

    Returns:
        Tuple of (list of categories, total count)
    """
    query = Category.query.filter_by(user_id=user_id)

    # Apply sorting
    if hasattr(Category, sort_by):
        sort_attr = getattr(Category, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_attr))
        else:
            query = query.order_by(asc(sort_attr))

    # Apply pagination
    total = query.count()
    categories = query.offset((page - 1) * per_page).limit(per_page).all()

    return categories, total


def get_category_stats(user_id: int) -> List[Dict[str, Any]]:
    """
    Get statistics for each category for a user.

    Args:
        user_id: User ID

    Returns:
        List of category statistics
    """
    from datetime import datetime

    today = datetime.now().date()

    categories = Category.query.filter_by(user_id=user_id).all()
    result = []

    for category in categories:
        # Get tasks in this category
        tasks = Task.query.filter_by(user_id=user_id, category_id=category.id).all()

        # Count total, completed, and overdue tasks
        task_count = len(tasks)
        completed_count = sum(1 for task in tasks if task.status == StatusEnum.READY)
        overdue_count = sum(
            1
            for task in tasks
            if task.due_date
            and task.due_date < today
            and task.status != StatusEnum.READY
        )

        # Create stats dictionary
        stats = category.to_dict()
        stats.update(
            {
                "task_count": task_count,
                "completed_count": completed_count,
                "overdue_count": overdue_count,
                "completion_rate": round((completed_count / task_count * 100), 2)
                if task_count > 0
                else 100.0,
            }
        )

        result.append(stats)

    return result
