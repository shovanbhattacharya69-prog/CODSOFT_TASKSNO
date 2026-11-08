"""
Unit Test Suite for To-Do List Application
Reference Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3

Validates models, storage layer, business manager logic, validation rules,
and CLI interactions.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from datetime import date, timedelta

from todo_app.cli import run_cli
from todo_app.manager import TaskManager, TaskNotFoundError, ValidationError
from todo_app.models import Category, Priority, Task
from todo_app.storage import StorageError, TaskStorage


class TestTaskModel(unittest.TestCase):
    """Test Task dataclass behavior and validation."""

    def test_task_creation_valid(self) -> None:
        task = Task(title="Buy Groceries", description="Milk, Eggs", priority=Priority.HIGH)
        self.assertEqual(task.title, "Buy Groceries")
        self.assertEqual(task.description, "Milk, Eggs")
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.id)
        self.assertIsNotNone(task.created_at)

    def test_task_empty_title_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            Task(title="")

        with self.assertRaises(ValueError):
            Task(title="    ")

    def test_task_priority_from_str(self) -> None:
        t1 = Task(title="Task 1", priority="high")
        self.assertEqual(t1.priority, Priority.HIGH)

        t2 = Task(title="Task 2", priority="LOW")
        self.assertEqual(t2.priority, Priority.LOW)

        t3 = Task(title="Task 3", priority="unknown")
        self.assertEqual(t3.priority, Priority.MEDIUM)

    def test_task_toggle_completion(self) -> None:
        task = Task(title="Exercise")
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)

        task.toggle_completed()
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)

        task.toggle_completed()
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)

    def test_task_overdue_check(self) -> None:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        overdue_task = Task(title="Past Task", due_date=yesterday)
        self.assertTrue(overdue_task.is_overdue())

        future_task = Task(title="Future Task", due_date=tomorrow)
        self.assertFalse(future_task.is_overdue())

        # If completed, should not be considered overdue
        overdue_task.mark_completed()
        self.assertFalse(overdue_task.is_overdue())

    def test_task_serialization_roundtrip(self) -> None:
        original = Task(
            title="Serialize Me",
            description="Details",
            priority=Priority.HIGH,
            category=Category.WORK.value,
            due_date="2026-12-31",
        )
        d = original.to_dict()
        restored = Task.from_dict(d)

        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.title, restored.title)
        self.assertEqual(original.description, restored.description)
        self.assertEqual(original.priority, restored.priority)
        self.assertEqual(original.category, restored.category)
        self.assertEqual(original.due_date, restored.due_date)


class TestTaskStorage(unittest.TestCase):
    """Test persistence layer, serialization, and error recovery."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.storage_file = os.path.join(self.temp_dir, "test_tasks.json")
        self.storage = TaskStorage(self.storage_file)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_empty_non_existent_file(self) -> None:
        tasks = self.storage.load_tasks()
        self.assertEqual(tasks, [])

    def test_save_and_load(self) -> None:
        t1 = Task(title="Task A")
        t2 = Task(title="Task B", priority=Priority.HIGH)
        self.storage.save_tasks([t1, t2])

        loaded = self.storage.load_tasks()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].title, "Task A")
        self.assertEqual(loaded[1].title, "Task B")

    def test_corrupted_json_handling(self) -> None:
        with open(self.storage_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json corrupted content")

        with self.assertRaises(StorageError):
            self.storage.load_tasks()

        # Check backup created
        backups = [f for f in os.listdir(self.temp_dir) if ".corrupt_" in f]
        self.assertGreater(len(backups), 0)

    def test_export_csv(self) -> None:
        tasks = [Task(title="CSV Task", priority=Priority.LOW)]
        csv_file = os.path.join(self.temp_dir, "export.csv")
        self.storage.export_csv(tasks, csv_file)
        self.assertTrue(os.path.exists(csv_file))
        with open(csv_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("CSV Task", content)
            self.assertIn("Low", content)


class TestTaskManager(unittest.TestCase):
    """Test business logic, CRUD, filtering, and metrics."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.storage = TaskStorage(os.path.join(self.temp_dir, "tasks.json"))
        self.manager = TaskManager(self.storage)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_task_validation(self) -> None:
        # Empty title should raise ValidationError
        with self.assertRaises(ValidationError):
            self.manager.add_task(title="")

        with self.assertRaises(ValidationError):
            self.manager.add_task(title="   ")

        # Invalid date should raise ValidationError
        with self.assertRaises(ValidationError):
            self.manager.add_task(title="Valid", due_date="not-a-date")

        # Valid task
        task = self.manager.add_task(
            title="Read Docs",
            priority="High",
            category="Study",
            due_date="2026-11-20",
        )
        self.assertEqual(task.title, "Read Docs")
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertEqual(task.category, "Study")
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

    def test_update_task(self) -> None:
        task = self.manager.add_task(title="Initial Title")

        updated = self.manager.update_task(
            task.id,
            title="Updated Title",
            priority=Priority.HIGH,
            due_date="2026-12-15",
        )
        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.priority, Priority.HIGH)
        self.assertEqual(updated.due_date, "2026-12-15")

        # Invalid update
        with self.assertRaises(ValidationError):
            self.manager.update_task(task.id, title="")

    def test_delete_and_not_found(self) -> None:
        task = self.manager.add_task(title="To Delete")
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

        self.manager.delete_task(task.id)
        self.assertEqual(len(self.manager.get_all_tasks()), 0)

        with self.assertRaises(TaskNotFoundError):
            self.manager.delete_task("non-existent-id")

    def test_toggle_and_clear_completed(self) -> None:
        t1 = self.manager.add_task(title="Task 1")
        t2 = self.manager.add_task(title="Task 2")

        self.manager.toggle_task(t1.id)
        self.assertTrue(self.manager.get_task(t1.id).completed)
        self.assertFalse(self.manager.get_task(t2.id).completed)

        cleared = self.manager.clear_completed()
        self.assertEqual(cleared, 1)
        self.assertEqual(len(self.manager.get_all_tasks()), 1)
        self.assertEqual(self.manager.get_all_tasks()[0].id, t2.id)

    def test_filtering_and_stats(self) -> None:
        self.manager.add_task(title="Work 1", category="Work", priority="High")
        t2 = self.manager.add_task(title="Work 2", category="Work", priority="Low")
        self.manager.add_task(title="Personal 1", category="Personal", priority="Medium")

        self.manager.toggle_task(t2.id)

        # Filter by status
        pending = self.manager.filter_tasks(status="pending")
        self.assertEqual(len(pending), 2)

        completed = self.manager.filter_tasks(status="completed")
        self.assertEqual(len(completed), 1)

        # Filter by category
        work_tasks = self.manager.filter_tasks(category="Work")
        self.assertEqual(len(work_tasks), 2)

        # Search query
        search_res = self.manager.filter_tasks(search_query="Personal")
        self.assertEqual(len(search_res), 1)

        # Stats
        stats = self.manager.get_stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 2)
        self.assertAlmostEqual(stats["completion_rate"], 33.3, places=1)


class TestCLI(unittest.TestCase):
    """Test CLI commands execution."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.storage = TaskStorage(os.path.join(self.temp_dir, "tasks.json"))
        self.manager = TaskManager(self.storage)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_add_and_list(self) -> None:
        exit_code = run_cli(["add", "CLI Test Task", "-p", "High"], manager=self.manager)
        self.assertEqual(exit_code, 0)
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

        exit_code = run_cli(["list"], manager=self.manager)
        self.assertEqual(exit_code, 0)

    def test_cli_done_and_delete(self) -> None:
        task = self.manager.add_task(title="CLI Action")
        exit_code = run_cli(["done", task.id[:8]], manager=self.manager)
        self.assertEqual(exit_code, 0)
        self.assertTrue(self.manager.get_task(task.id).completed)

        exit_code = run_cli(["delete", task.id[:8]], manager=self.manager)
        self.assertEqual(exit_code, 0)
        self.assertEqual(len(self.manager.get_all_tasks()), 0)


if __name__ == "__main__":
    unittest.main()
