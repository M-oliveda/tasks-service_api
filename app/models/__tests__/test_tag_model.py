"""Tests for Tag model."""
from datetime import datetime

from app.models.tag import Tag


def test_tag_creation(db_session, user):
    """Test the creation of a Tag instance.

    This test verifies that a Tag can be created with the correct attributes,
    including name, user association, and timestamps. It also ensures that
    the `id` is generated after committing the object to the database.
    """
    tag = Tag(name="TestTag", user_id=user.id)
    db_session.add(tag)
    db_session.commit()

    assert tag.id is not None
    assert tag.name == "TestTag"
    assert tag.user_id == user.id
    assert isinstance(tag.created_at, datetime)
    assert isinstance(tag.updated_at, datetime)


def test_tag_relationship_with_user(tag, user):
    """Test the relationship between a Tag and a User.

    This test checks that a Tag instance is correctly linked to a User instance
    via the `user` relationship and that the User's `id` and `username` match
    the expected values.
    """
    assert tag.user is not None
    assert tag.user.id == user.id
    assert tag.user.username == user.username


def test_tag_relationship_with_tasks(task_with_tags, tag):
    """Test the relationship between a Tag and Tasks via TaskTag.

    This test ensures that a Tag instance has a correct relationship with Task
    instances through the TaskTag association table and that the tasks related
    to the tag are correctly associated.
    """
    assert len(tag.task_tags) == 1
    assert tag.task_tags[0].task.id == task_with_tags.id
    assert tag.task_tags[0].task.title == task_with_tags.title


def test_tag_to_dict(tag):
    """Test converting a Tag instance to a dictionary.

    This test verifies that the `to_dict` method correctly converts a Tag instance
    into a dictionary representation, including checking for the expected keys
    and values.
    """
    tag_dict = tag.to_dict()

    assert "id" in tag_dict
    assert "name" in tag_dict
    assert "user_id" in tag_dict
    assert "created_at" in tag_dict
    assert "updated_at" in tag_dict

    # Check values
    assert tag_dict["name"] == "TestTag"


def test_tag_repr(tag):
    """Test the string representation of a Tag instance.

    This test checks that the string representation of a Tag instance returns
    the expected format with the tag's name.
    """
    assert repr(tag) == "<Tag TestTag>"


def test_tag_crud_methods(db_session, user):
    """Test CRUD methods inherited from the base model in Tag.

    This test ensures that the Tag model's CRUD methods (`create`, `update`,
    `save`, `delete`) work as expected, including creating a new tag, updating it,
    saving changes, and deleting the tag from the database.
    """
    # Create using class method
    tag = Tag.create(name="NewTag", user_id=user.id)

    assert tag.id is not None
    assert tag.name == "NewTag"

    # Update the tag
    tag.update(name="UpdatedTag")
    db_session.refresh(tag)

    assert tag.name == "UpdatedTag"

    # Save the tag with changes
    tag.name = "SavedTag"
    tag.save()
    db_session.refresh(tag)

    assert tag.name == "SavedTag"

    # Delete the tag
    tag_id = tag.id
    tag.delete()

    # Check that it's deleted
    assert db_session.get(Tag, tag_id) is None
