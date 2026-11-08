"""
To-Do List Application - Models Module
Reference Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3

Defines core data structures and domain models for tasks, priorities,
and task status management with full serialization support.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class Priority(str, Enum):
    """Enumeration of task priority levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    @classmethod
    def from_str(cls, value: str) -> "Priority":
        """Parse priority from string case-insensitively with safe fallback."""
        val = (value or "").strip().lower()
        if val in ("high", "h", "3"):
            return cls.HIGH
        if val in ("low", "l", "1"):
            return cls.LOW
        return cls.MEDIUM

    @property
    def rank(self) -> int:
        """Numeric rank for sorting: High (3), Medium (2), Low (1)."""
        mapping = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        return mapping.get(self, 2)


class Category(str, Enum):
    """Common categories for organizing tasks."""

    WORK = "Work"
    PERSONAL = "Personal"
    STUDY = "Study"
    HEALTH = "Health"
    FINANCE = "Finance"
    OTHER = "Other"

    @classmethod
    def from_str(cls, value: str) -> str:
        """Clean and normalize category string, retaining custom strings."""
        val = (value or "").strip()
        if not val:
            return cls.OTHER.value
        # If matches an enum member title-cased, standardize it
        for member in cls:
            if member.value.lower() == val.lower():
                return member.value
        return val


@dataclass
class Task:
    """Represents an individual to-do task.

    Attributes:
        id: Unique identifier for the task (UUID string).
        title: Short title/summary of the task (must not be empty).
        description: Detailed notes or context for the task.
        priority: Priority enum (Low, Medium, High).
        category: Category string tag (e.g., Work, Personal).
        due_date: Optional due date string in YYYY-MM-DD format.
        completed: Boolean flag indicating if the task is finished.
        created_at: ISO 8601 timestamp string when task was created.
        completed_at: ISO 8601 timestamp string when task was completed.
    """

    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    category: str = Category.OTHER.value
    due_date: Optional[str] = None
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    completed_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate fields upon initialization."""
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Task title cannot be empty or whitespace only.")

        if isinstance(self.priority, str):
            self.priority = Priority.from_str(self.priority)

        if not self.category:
            self.category = Category.OTHER.value
        else:
            self.category = Category.from_str(self.category)

        if self.due_date:
            self.due_date = self.due_date.strip() or None

    def mark_completed(self) -> None:
        """Mark task as completed and record completion timestamp."""
        self.completed = True
        self.completed_at = datetime.now().isoformat(timespec="seconds")

    def mark_pending(self) -> None:
        """Reopen task as pending/active."""
        self.completed = False
        self.completed_at = None

    def toggle_completed(self) -> bool:
        """Toggle completion state and return new state."""
        if self.completed:
            self.mark_pending()
        else:
            self.mark_completed()
        return self.completed

    def is_overdue(self) -> bool:
        """Check if task has a passed due date and is not completed."""
        if self.completed or not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            return due < datetime.now().date()
        except ValueError:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert task instance to JSON-serializable dictionary."""
        data = asdict(self)
        data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Reconstruct Task instance from dictionary."""
        clean_data = dict(data)
        if "priority" in clean_data and isinstance(clean_data["priority"], str):
            clean_data["priority"] = Priority.from_str(clean_data["priority"])
        return cls(**clean_data)
