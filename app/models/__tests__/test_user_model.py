"""Tests for User model."""
from datetime import datetime

from app.models.user import User
from app.schemas.user import RoleEnum


def test_user_creation(db_session):
    """Test creation of a User."""
    user = User(username="testuser", email="test@example.com", password="password123")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    assert user.role == RoleEnum.USER
    assert user.last_login is None
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_user_password(user):
    """Test password setting and checking."""
    # Password hash should be different from the original password
    assert user.password_hash != "password123"

    # Check password should return True for correct password
    assert user.check_password("password123") is True

    # Check password should return False for incorrect password
    assert user.check_password("wrongpassword") is False

    # Change password
    user.set_password("newpassword")
    assert user.check_password("password123") is False
    assert user.check_password("newpassword") is True


def test_user_update_last_login(user, db_session):
    """Test updating the last login timestamp."""
    assert user.last_login is None

    user.update_last_login()
    db_session.refresh(user)

    assert user.last_login is not None
    assert isinstance(user.last_login, datetime)


def test_user_to_dict(user):
    """Test converting user to dictionary."""
    user_dict = user.to_dict()

    assert "id" in user_dict
    assert "username" in user_dict
    assert "email" in user_dict
    assert "role" in user_dict
    assert "created_at" in user_dict
    assert "updated_at" in user_dict
    assert "last_login" in user_dict

    # Password hash should not be in the dictionary
    assert "password_hash" not in user_dict

    # Check values
    assert user_dict["username"] == "testuser"
    assert user_dict["email"] == "test@example.com"
    assert user_dict["role"] == RoleEnum.USER.value
    assert user_dict["last_login"] is None


def test_user_repr(user):
    """Test the string representation of a user."""
    assert repr(user) == "<User testuser>"


def test_user_relationships(user, task, category, tag):
    """Test user relationships with tasks, categories, and tags."""
    assert len(user.tasks) == 1
    assert user.tasks[0].id == task.id
    assert len(user.categories) == 1
    assert user.categories[0].id == category.id
    assert len(user.tags) == 1
    assert user.tags[0].id == tag.id
