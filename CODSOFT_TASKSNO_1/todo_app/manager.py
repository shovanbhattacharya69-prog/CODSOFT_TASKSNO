"""
To-Do List Application - Manager Module
Reference Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3

Implements the business logic and state management for tasks, including
CRUD operations, search, filtering, sorting, and aggregate analytics.
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Dict, List, Optional

from .models import Category, Priority, Task
from .storage import TaskStorage


class TaskNotFoundError(Exception):
    """Raised when an operation references a task ID that does not exist."""
    pass


class ValidationError(Exception):
    """Raised when task input validation fails."""
    pass


class TaskManager:
    """Coordinates task operations, validation, queries, and persistence.

    Acts as the primary application service consumed by both GUI and CLI frontends.
    """

    def __init__(self, storage: Optional[TaskStorage] = None) -> None:
        """Initialize task manager with optional custom storage.

        Args:
            storage: Optional TaskStorage instance. Defaults to TaskStorage()
                     using local tasks.json.
        """
        self.storage = storage or TaskStorage()
        self._tasks: List[Task] = []
        self.load()

    def load(self) -> None:
        """Reload tasks from persistent storage."""
        self._tasks = self.storage.load_tasks()

    def save(self) -> None:
        """Persist current task state to disk."""
        self.storage.save_tasks(self._tasks)

    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: Priority | str = Priority.MEDIUM,
        category: str = Category.OTHER.value,
        due_date: Optional[str] = None,
    ) -> Task:
        """Create, validate, append and persist a new Task.

        Args:
            title: Title text for the task (cannot be empty).
            description: Optional descriptive notes.
            priority: Priority enum or string representation.
            category: Organizational category tag.
            due_date: Optional date string in YYYY-MM-DD format.

        Returns:
            The created Task instance.

        Raises:
            ValidationError: If title is empty or due date is invalid.
        """
        clean_title = (title or "").strip()
        if not clean_title:
            raise ValidationError("Task title cannot be empty or blank.")

        clean_due_date: Optional[str] = None
        if due_date:
            due_str = due_date.strip()
            if due_str:
                try:
                    # Validate format
                    datetime.strptime(due_str, "%Y-%m-%d")
                    clean_due_date = due_str
                except ValueError:
                    raise ValidationError(
                        f"Invalid due date '{due_date}'. Expected YYYY-MM-DD format."
                    )

        if isinstance(priority, str):
            priority = Priority.from_str(priority)

        task = Task(
            title=clean_title,
            description=(description or "").strip(),
            priority=priority,
            category=category,
            due_date=clean_due_date,
        )

        self._tasks.append(task)
        self.save()
        return task

    def get_task(self, task_id: str) -> Task:
        """Locate a task by its ID.

        Args:
            task_id: Unique task identifier.

        Returns:
            The matching Task object.

        Raises:
            TaskNotFoundError: If task ID is not found.
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"Task with ID '{task_id}' not found.")

    def update_task(
        self,
        task_id: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority | str] = None,
        category: Optional[str] = None,
        due_date: Optional[str] = None,
        clear_due_date: bool = False,
    ) -> Task:
        """Update fields on an existing task.

        Args:
            task_id: Task identifier.
            title: New title if specified (cannot be empty if given).
            description: New description if specified.
            priority: New priority if specified.
            category: New category if specified.
            due_date: New due date string (YYYY-MM-DD).
            clear_due_date: If True, resets due date to None.

        Returns:
            The updated Task.
        """
        task = self.get_task(task_id)

        if title is not None:
            clean_title = title.strip()
            if not clean_title:
                raise ValidationError("Task title cannot be empty or blank.")
            task.title = clean_title

        if description is not None:
            task.description = description.strip()

        if priority is not None:
            if isinstance(priority, str):
                task.priority = Priority.from_str(priority)
            else:
                task.priority = priority

        if category is not None:
            task.category = Category.from_str(category)

        if clear_due_date:
            task.due_date = None
        elif due_date is not None:
            due_str = due_date.strip()
            if due_str:
                try:
                    datetime.strptime(due_str, "%Y-%m-%d")
                    task.due_date = due_str
                except ValueError:
                    raise ValidationError(
                        f"Invalid due date '{due_date}'. Expected YYYY-MM-DD format."
                    )
            else:
                task.due_date = None

        self.save()
        return task

    def toggle_task(self, task_id: str) -> Task:
        """Toggle the completion status of a task.

        Args:
            task_id: Task identifier.

        Returns:
            The updated Task.
        """
        task = self.get_task(task_id)
        task.toggle_completed()
        self.save()
        return task

    def set_task_status(self, task_id: str, completed: bool) -> Task:
        """Explicitly set task completion status."""
        task = self.get_task(task_id)
        if completed:
            task.mark_completed()
        else:
            task.mark_pending()
        self.save()
        return task

    def delete_task(self, task_id: str) -> Task:
        """Remove a task from the list and persist changes.

        Args:
            task_id: Task identifier.

        Returns:
            The removed Task object.
        """
        task = self.get_task(task_id)
        self._tasks.remove(task)
        self.save()
        return task

    def clear_completed(self) -> int:
        """Delete all completed tasks.

        Returns:
            Number of tasks removed.
        """
        initial_len = len(self._tasks)
        self._tasks = [t for t in self._tasks if not t.completed]
        removed_count = initial_len - len(self._tasks)
        if removed_count > 0:
            self.save()
        return removed_count

    # -------------------------------------------------------------------------
    # Search, Query & Filters
    # -------------------------------------------------------------------------

    def get_all_tasks(self) -> List[Task]:
        """Return shallow copy of all tasks."""
        return list(self._tasks)

    def filter_tasks(
        self,
        *,
        status: Optional[str] = None,  # "all", "pending", "completed", "overdue"
        category: Optional[str] = None,
        priority: Optional[str | Priority] = None,
        search_query: Optional[str] = None,
        sort_by: str = "created_desc",  # "created_desc", "due_date", "priority", "title"
    ) -> List[Task]:
        """Filter and sort tasks based on provided criteria.

        Args:
            status: 'all', 'pending', 'completed', or 'overdue'.
            category: Filter to specific category name or 'all'.
            priority: Filter to specific Priority or 'all'.
            search_query: Search string in title and description.
            sort_by: Sort ordering key.

        Returns:
            List of matching Task instances.
        """
        results = list(self._tasks)

        # Status filter
        if status:
            st = status.lower().strip()
            if st == "pending":
                results = [t for t in results if not t.completed]
            elif st == "completed":
                results = [t for t in results if t.completed]
            elif st == "overdue":
                results = [t for t in results if t.is_overdue()]

        # Category filter
        if category and category.lower() != "all":
            results = [t for t in results if t.category.lower() == category.lower()]

        # Priority filter
        if priority and str(priority).lower() != "all":
            pri_enum = (
                priority if isinstance(priority, Priority) else Priority.from_str(priority)
            )
            results = [t for t in results if t.priority == pri_enum]

        # Search query (case-insensitive search in title or description)
        if search_query:
            query = search_query.strip().lower()
            if query:
                results = [
                    t for t in results
                    if query in t.title.lower() or query in t.description.lower()
                ]

        # Sorting
        if sort_by == "priority":
            # High -> Medium -> Low, then by due date
            results.sort(
                key=lambda t: (not t.completed, t.priority.rank, t.due_date or "9999-12-31"),
                reverse=True,
            )
        elif sort_by == "due_date":
            # Soonest due date first, tasks without due date at end
            results.sort(
                key=lambda t: (
                    t.completed,
                    t.due_date is None,
                    t.due_date or "9999-12-31",
                )
            )
        elif sort_by == "title":
            results.sort(key=lambda t: t.title.lower())
        elif sort_by == "created_asc":
            results.sort(key=lambda t: t.created_at)
        else:  # "created_desc" default
            results.sort(key=lambda t: t.created_at, reverse=True)

        return results

    def get_categories(self) -> List[str]:
        """Return sorted list of unique categories currently in use plus standard defaults."""
        standard = [c.value for c in Category]
        used = {t.category for t in self._tasks if t.category}
        all_cats = sorted(set(standard).union(used))
        return all_cats

    def get_stats(self) -> Dict[str, Any]:
        """Compute summary statistics for dashboard and progress indicators.

        Returns:
            Dictionary containing metrics: total, completed, pending,
            overdue, and completion_percentage.
        """
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks if t.completed)
        pending = total - completed
        overdue = sum(1 for t in self._tasks if t.is_overdue())
        rate = round((completed / total * 100), 1) if total > 0 else 0.0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": rate,
        }
