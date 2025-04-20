"""Tests for Category model."""
from datetime import datetime

from app.models.category import Category


def test_category_creation(db_session, user):
    """Test the creation of a Category instance.

    This test verifies that a Category can be created with the correct attributes,
    including name, description, user association, and timestamps. It also ensures
    that the `id` is generated after committing the object to the database.
    """
    category = Category(
        name="Test Category", description="Test category description", user_id=user.id
    )
    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert category.name == "Test Category"
    assert category.description == "Test category description"
    assert category.user_id == user.id
    assert isinstance(category.created_at, datetime)
    assert isinstance(category.updated_at, datetime)


def test_category_relationship_with_user(category, user):
    """Test the relationship between a Category and a User.

    This test checks that a Category instance is correctly linked to a User instance
    via the `user` relationship and that the User's `id` and `username` match the
    expected values.
    """
    assert category.user is not None
    assert category.user.id == user.id
    assert category.user.username == user.username


def test_category_relationship_with_tasks(category, task):
    """Test the relationship between a Category and Tasks.

    This test ensures that a Category instance has a correct relationship with Task
    instances and that the tasks related to the category are correctly associated.
    """
    assert len(category.tasks) == 1
    assert category.tasks[0].id == task.id
    assert category.tasks[0].title == task.title


def test_category_to_dict(category):
    """Test converting a Category instance to a dictionary.

    This test verifies that the `to_dict` method correctly converts
    A Category instance into a dictionary representation,
    including checking for the expected keys and values.
    """
    category_dict = category.to_dict()

    assert "id" in category_dict
    assert "name" in category_dict
    assert "description" in category_dict
    assert "user_id" in category_dict
    assert "created_at" in category_dict
    assert "updated_at" in category_dict

    # Check values
    assert category_dict["name"] == "Test Category"
    assert category_dict["description"] == "Test category description"


def test_category_repr(category):
    """Test the string representation of a Category instance.

    This test checks that the string representation of a Category instance returns
    the expected format with the category's name.
    """
    assert repr(category) == "<Category Test Category>"


def test_category_crud_methods(db_session, user):
    """Test CRUD methods inherited from the base model in Category.

    This test ensures that the Category model's CRUD methods (`create`, `update`,
    `save`, `delete`) work as expected, including creating a new category, updating it,
    saving changes, and deleting the category from the database.
    """
    # Create using class method
    category = Category.create(
        name="New Category", description="New description", user_id=user.id
    )

    assert category.id is not None
    assert category.name == "New Category"

    # Update the category
    category.update(name="Updated Category")
    db_session.refresh(category)

    assert category.name == "Updated Category"
    assert category.description == "New description"  # Unchanged

    # Save the category with changes
    category.description = "Updated description"
    category.save()
    db_session.refresh(category)

    assert category.description == "Updated description"

    # Delete the category
    category_id = category.id
    category.delete()

    # Check that it's deleted
    assert db_session.get(Category, category_id) is None
