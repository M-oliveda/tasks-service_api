"""Tests for Task model and TaskTag association."""
from datetime import datetime, timedelta

from app.models.tag import Tag
from app.models.task import Task, TaskTag
from app.schemas.task import PriorityEnum, StatusEnum


def test_task_creation(db_session, user, category):
    """Test the creation of a Task.

    This test verifies that a Task can be created with the correct attributes,
    including title, description, status, priority, due date, user and category
    associations, and timestamps. It also ensures that the `id` is generated
    after committing the task to the database.
    """
    task = Task(
        title="Test Task",
        description="Test task description",
        status=StatusEnum.TODO,
        priority=PriorityEnum.MEDIUM,
        due_date=datetime.now().date() + timedelta(days=1),
        user_id=user.id,
        category_id=category.id,
    )
    db_session.add(task)
    db_session.commit()

    assert task.id is not None
    assert task.title == "Test Task"
    assert task.description == "Test task description"
    assert task.status == StatusEnum.TODO
    assert task.priority == PriorityEnum.MEDIUM
    assert task.due_date is not None
    assert task.user_id == user.id
    assert task.category_id == category.id
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_relationship_with_user(task, user):
    """Test the relationship between Task and User.

    This test ensures that a Task instance is correctly linked to a User instance
    via the `user` relationship and that the User's `id` and `username` match
    the expected values.
    """
    assert task.user is not None
    assert task.user.id == user.id
    assert task.user.username == user.username


def test_task_relationship_with_category(task, category):
    """Test the relationship between Task and Category.

    This test ensures that a Task instance is correctly linked to a Category instance
    via the `category` relationship and that the Category's `id` and `name` match
    the expected values.
    """
    assert task.category is not None
    assert task.category.id == category.id
    assert task.category.name == category.name


def test_task_tags_property(task_with_tags, tag):
    """Test the tags property.

    This test checks that the `tags` property of a Task instance correctly returns
    the tags associated with the task. It ensures that the task has the expected
    number of tags and verifies the correct values of the tags.
    """
    tags = task_with_tags.tags
    assert len(tags) == 1
    assert tags[0].id == tag.id
    assert tags[0].name == tag.name


def test_add_tag_to_task(db_session, task, user):
    """Test adding a tag to a task.

    This test ensures that a tag can be successfully added to a Task instance.
    It checks that the tag is correctly linked to the task and that the task's
    tags relationship is updated accordingly.
    """
    # Create a new tag
    new_tag = Tag(name="NewTag", user_id=user.id)
    db_session.add(new_tag)
    db_session.commit()

    # Add tag to task
    task.add_tag(new_tag)
    db_session.commit()

    # Check that the tag was added
    assert len(task.tags) == 1
    assert task.tags[0].id == new_tag.id
    assert task.tags[0].name == "NewTag"


def test_remove_tag_from_task(db_session, task_with_tags, tag):
    """Test removing a tag from a task.

    This test checks that a tag can be successfully removed from a Task instance.
    It verifies that the tag is removed from the task's tags relationship and that
    the tag is no longer associated with the task.
    """
    # Check that the tag exists initially
    assert len(task_with_tags.tags) == 1

    # Remove the tag
    task_with_tags.remove_tag(tag)
    db_session.commit()

    # Check that the tag was removed
    assert len(task_with_tags.tags) == 0


def test_is_overdue_method(task, overdue_task):
    """Test the is_overdue method.

    This test verifies the behavior of the `is_overdue` method. It ensures that
    a task with a due date in the past is considered overdue and that tasks without
    a due date or due in the future are not considered overdue.
    """
    # Regular task should not be overdue
    assert task.is_overdue() is False

    # Overdue task should be overdue
    assert overdue_task.is_overdue() is True

    # Task without due date should not be overdue
    task.due_date = None
    assert task.is_overdue() is False


def test_task_to_dict(task_with_tags, tag):
    """Test converting a task to a dictionary.

    This test ensures that the `to_dict` method correctly converts a Task instance
    into a dictionary representation, including checking for the expected keys
    and values.
    It also verifies the correct handling of the task's tags and overdue status.
    """
    task_dict = task_with_tags.to_dict()

    assert "id" in task_dict
    assert "title" in task_dict
    assert "description" in task_dict
    assert "status" in task_dict
    assert "priority" in task_dict
    assert "due_date" in task_dict
    assert "user_id" in task_dict
    assert "category_id" in task_dict
    assert "category" in task_dict
    assert "tags" in task_dict
    assert "created_at" in task_dict
    assert "updated_at" in task_dict
    assert "is_overdue" in task_dict

    # Check values
    assert task_dict["title"] == "Test Task"
    assert task_dict["description"] == "Test task description"
    assert task_dict["status"] == StatusEnum.TODO.value
    assert task_dict["priority"] == PriorityEnum.MEDIUM.value
    assert task_dict["category"] == "Test Category"
    assert len(task_dict["tags"]) == 1
    assert task_dict["tags"][0] == "TestTag"
    assert task_dict["is_overdue"] is False


def test_task_repr(task):
    """Test the string representation of a task.

    This test ensures that the string representation of a Task instance returns
    the expected format with the task's title.
    """
    assert repr(task) == "<Task Test Task>"


def test_task_crud_methods(db_session, user, category):
    """Test CRUD methods inherited from the base model in Task.

    This test ensures that the Task model's CRUD methods (`create`, `update`,
    `save`, `delete`) work as expected, including creating a new task, updating it,
    saving changes, and deleting the task from the database.
    """
    # Create using class method
    task = Task.create(
        title="New Task",
        description="New description",
        status=StatusEnum.TODO,
        priority=PriorityEnum.LOW,
        user_id=user.id,
        category_id=category.id,
    )

    assert task.id is not None
    assert task.title == "New Task"

    # Update the task
    task.update(title="Updated Task", status=StatusEnum.IN_PROGRESS)
    db_session.refresh(task)

    assert task.title == "Updated Task"
    assert task.status == StatusEnum.IN_PROGRESS
    assert task.description == "New description"  # Unchanged

    # Save the task with changes
    task.description = "Updated description"
    task.save()
    db_session.refresh(task)

    assert task.description == "Updated description"

    # Delete the task
    task_id = task.id
    task.delete()

    # Check that it's deleted
    assert db_session.get(Task, task_id) is None


def test_task_tag_association(db_session, task, tag):
    """Test the TaskTag association model.

    This test verifies the creation of an association between a Task and a Tag
    through the TaskTag model. It ensures that the relationship is correctly
    established and that both the Task and Tag instances reflect the association.
    """
    # Create association
    task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
    db_session.add(task_tag)
    db_session.commit()

    # Check relationships
    assert task_tag.task_id == task.id
    assert task_tag.tag_id == tag.id
    assert task_tag.task == task
    assert task_tag.tag == tag

    # Check that task_tags are added to task and tag
    assert len(task.task_tags) == 1
    assert task.task_tags[0].tag_id == tag.id
    assert len(tag.task_tags) == 1
    assert tag.task_tags[0].task_id == task.id
