"""Tests for base models."""
import pytest
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CRUDMixin, Model


def test_crud_mixin_methods():
    """Test that the CRUDMixin class has the expected CRUD methods.

    This test ensures that the CRUDMixin class includes the correct methods.
    Also, it checks that they are callable.
    """
    # Check that the methods exist
    assert hasattr(CRUDMixin, "create")
    assert hasattr(CRUDMixin, "update")
    assert hasattr(CRUDMixin, "save")
    assert hasattr(CRUDMixin, "delete")

    # Check that they are callable
    assert callable(CRUDMixin.create)
    assert callable(CRUDMixin.update)
    assert callable(CRUDMixin.save)
    assert callable(CRUDMixin.delete)


def test_model_init_valid_kwargs():
    """Test that the Model class __init__ method accepts valid keyword arguments."""

    class UniqueTestModel(Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        attribute1 = "test"
        attribute2 = 123
        __table_args__ = {"extend_existing": True}

    # Initialize with valid kwargs
    model = UniqueTestModel(attribute1="new value", attribute2=456)
    assert model.attribute1 == "new value"
    assert model.attribute2 == 456


def test_model_init_invalid_kwargs():
    """Test Model class __init__ method raises TypeError for invalid arguments."""

    class UniqueTestModel(Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        attribute = "test"
        __table_args__ = {"extend_existing": True}

    # Initialize with invalid kwargs should raise TypeError
    with pytest.raises(TypeError) as exc_info:
        UniqueTestModel(invalid_attribute="value")

    assert "Invalid keyword argument: invalid_attribute" in str(exc_info.value)
