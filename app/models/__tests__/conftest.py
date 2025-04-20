"""Test configuration for pytest."""
import warnings
from datetime import datetime, timedelta
from os import environ

import pytest

from app.core.extensions import db
from app.models.category import Category
from app.models.tag import Tag
from app.models.task import Task, TaskTag
from app.models.user import User
from app.schemas.task import PriorityEnum, StatusEnum
from app.schemas.user import RoleEnum


def pytest_configure(config):
    """Configure warnings to ignore DeprecationWarnings for specific modules."""
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="sqlalchemy.*"
    )
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="werkzeug.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="ast")
    warnings.filterwarnings(
        "ignore", message=".*PydanticDeprecatedSince20.*", module="pydantic.*"
    )
    warnings.filterwarnings(
        "ignore", category=Warning, message=".*declarative base already contains.*"
    )


@pytest.fixture(scope="function")
def app():
    """Configure the app to use SQLite in-memory database."""
    from app import create_app

    environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    environ["TESTING"] = "True"

    app = create_app("testing")

    # Configure the app to use SQLite in-memory database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from app.core.extensions import db

    with app.app_context():
        # Create tables
        db.create_all()
        yield app
        # Drop tables
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def db_session(app):
    """Create and manage a database session for testing.

    This fixture provides a fresh database session for each test
    and rolls back transactions to ensure isolation.
    """
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        session = db.session

        yield session

        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def user(db_session):
    """Create a test user in the database.

    This fixture creates a test user with default values and adds it to the database.
    The user is returned for use in test functions.
    """
    user = User(username="testuser", email="test@example.com", password="password123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """Create a test admin user in the database.

    This fixture creates a test user with admin role and adds it to the database.
    The admin user is returned for use in test functions.
    """
    admin = User(
        username="adminuser",
        email="admin@example.com",
        password="admin123",
        role=RoleEnum.ADMIN,
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def category(db_session, user):
    """Create a test category in the database.

    This fixture creates a test category, associates it with the provided user,
    and adds it to the database. The category is returned for use in test functions.
    """
    category = Category(
        name="Test Category", description="Test category description", user_id=user.id
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def tag(db_session, user):
    """Create a test tag in the database.

    This fixture creates a test tag, associates it with the provided user,
    and adds it to the database. The tag is returned for use in test functions.
    """
    tag = Tag(name="TestTag", user_id=user.id)
    db_session.add(tag)
    db_session.commit()
    return tag


@pytest.fixture
def task(db_session, user, category):
    """Create a test task in the database."""
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
    return task


@pytest.fixture
def overdue_task(db_session, user, category):
    """Create an overdue test task in the database."""
    task = Task(
        title="Overdue Task",
        description="This task is overdue",
        status=StatusEnum.TODO,
        priority=PriorityEnum.HIGH,
        due_date=datetime.now().date() - timedelta(days=1),
        user_id=user.id,
        category_id=category.id,
    )
    db_session.add(task)
    db_session.commit()
    return task


@pytest.fixture
def task_with_tags(db_session, task, tag):
    """Create a task and associate it with a tag."""
    task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
    db_session.add(task_tag)
    db_session.commit()
    return task
