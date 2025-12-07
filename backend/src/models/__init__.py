"""
Data model base classes for the GitHub Spec Kit Demo Application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class BaseModel:
    """Base class for all data models with common functionality."""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary.

        Returns:
            Dictionary representation of the model.
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat() + "Z"
            elif isinstance(value, BaseModel):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, BaseModel) else item for item in value
                ]
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        Create a model instance from a dictionary.

        Args:
            data: Dictionary with model data.

        Returns:
            New instance of the model.
        """
        return cls(**data)
