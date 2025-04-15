"""Tag service functions."""
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from flask import abort, current_app
from sqlalchemy import asc, desc

from app.core.extensions import db
from app.models import Tag, TaskTag


def create_tag(user_id: UUID, name: str) -> Tag:
    """
    Create a new tag.

    Args:
        user_id: ID of the user creating the tag
        name: Tag name

    Returns:
        Created tag object
    """
    tag = Tag(user_id=user_id, name=name)

    try:
        db.session.add(tag)
        db.session.commit()

        current_app.logger.info(f"Tag {name} created successfully")
        return tag
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to create tag {name}: {e}")
        raise abort(500, "Failed to create tag")


def get_tag_by_id(tag_id: UUID, user_id: UUID) -> Optional[Tag]:
    """
    Get a tag by ID for a specific user.

    Args:
        tag_id: Tag ID
        user_id: User ID

    Returns:
        Tag object if found, None otherwise
    """
    return Tag.query.filter_by(id=tag_id, user_id=user_id).first()


def get_tag_by_name(name: str, user_id: int) -> Optional[Tag]:
    """
    Get a tag by name for a specific user.

    Args:
        name: Tag name
        user_id: User ID

    Returns:
        Tag object if found, None otherwise
    """
    return Tag.query.filter_by(name=name, user_id=user_id).first()


def update_tag(tag: Tag, data: Dict[str, Any]) -> Tag:
    """
    Update a tag.

    Args:
        tag: Tag object to update
        data: Dictionary of tag attributes to update

    Returns:
        Updated tag object
    """
    for key, value in data.items():
        if hasattr(tag, key) and value is not None:
            setattr(tag, key, value)

    try:
        db.session.commit()
        current_app.logger.info(f"Tag {tag.name} updated successfully")
        return tag
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update tag: {e}")
        raise abort(500, "Failed to update tag")


def delete_tag(tag: Tag) -> bool:
    """
    Delete a tag. This will remove the tag from all tasks.

    Args:
        tag: Tag object to delete

    Returns:
        True if deletion was successful
    """
    # The cascade should handle removing the tag from all tasks
    try:
        db.session.delete(tag)
        db.session.commit()
        current_app.logger.info(f"Tag {tag.name} deleted successfully")
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete tag: {e}")
        raise abort(500, "Failed to delete tag")


def list_tags(
    user_id: int,
    sort_by: str = "name",
    sort_order: str = "asc",
    page: int = 1,
    per_page: int = 20,
) -> Tuple[List[Tag], int]:
    """
    List tags for a user with pagination.

    Args:
        user_id: User ID
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        page: Page number
        per_page: Number of items per page

    Returns:
        Tuple of (list of tags, total count)
    """
    query = Tag.query.filter_by(user_id=user_id)

    # Apply sorting
    if hasattr(Tag, sort_by):
        sort_attr = getattr(Tag, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_attr))
        else:
            query = query.order_by(asc(sort_attr))

    # Apply pagination
    total = query.count()
    tags = query.offset((page - 1) * per_page).limit(per_page).all()

    return tags, total


def get_tag_stats(user_id: int) -> List[Dict[str, Any]]:
    """
    Get statistics for each tag for a user.

    Args:
        user_id: User ID

    Returns:
        List of tag statistics with usage counts
    """
    # First get all tags for this user
    tags = Tag.query.filter_by(user_id=user_id).all()
    result = []

    for tag in tags:
        # Count tasks that use this tag
        task_count = TaskTag.query.filter_by(tag_id=tag.id).count()

        # Create stats dictionary
        stats = tag.to_dict()
        stats.update({"task_count": task_count})

        result.append(stats)

    # Sort by task_count (most used first)
    result.sort(key=lambda x: x["task_count"], reverse=True)

    return result
