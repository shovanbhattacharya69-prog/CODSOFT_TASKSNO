"""
To-Do List Application - Storage Module
Reference Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3

Handles file-based persistence for tasks using JSON with atomic writes,
directory creation, and safe corruption recovery.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import Task

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Custom exception raised when task storage operations fail."""
    pass


class TaskStorage:
    """Manages persistent disk storage of Task objects in JSON format.

    Uses atomic file replacement to prevent data loss or corruption in case of
    system crashes, process interruptions, or power failures.
    """

    DEFAULT_FILENAME = "tasks.json"

    def __init__(self, file_path: Optional[str | Path] = None) -> None:
        """Initialize storage manager with specified or default file path.

        Args:
            file_path: Optional path to JSON storage file. If omitted,
                       saves to 'tasks.json' in current working directory.
        """
        if file_path is None:
            self.file_path = Path.cwd() / self.DEFAULT_FILENAME
        else:
            self.file_path = Path(file_path).resolve()

        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_tasks(self) -> List[Task]:
        """Load tasks from the persistent JSON file.

        Returns:
            List of Task instances loaded from disk, or empty list if file
            does not yet exist.

        Raises:
            StorageError: If the file is unreadable and could not be recovered.
        """
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                raw_data = json.loads(content)

            tasks: List[Task] = []
            for item in raw_data:
                try:
                    tasks.append(Task.from_dict(item))
                except Exception as parse_err:
                    logger.warning("Skipping malformed task entry: %s (%s)", item, parse_err)
            return tasks

        except json.JSONDecodeError as jde:
            # Backup corrupted file and return empty list to protect user
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.file_path.with_suffix(f".corrupt_{timestamp}.bak")
            try:
                shutil.copy2(self.file_path, backup_path)
                logger.error(
                    "Corrupted tasks file backed up to %s. Reason: %s", backup_path, jde
                )
            except OSError as copy_err:
                logger.error("Failed to back up corrupted file: %s", copy_err)
            raise StorageError(
                f"Tasks file was corrupted and backed up to '{backup_path.name}'. "
                "Starting with a fresh task list."
            ) from jde

        except OSError as oe:
            raise StorageError(f"Operating system error reading '{self.file_path}': {oe}") from oe

    def save_tasks(self, tasks: List[Task]) -> None:
        """Atomically save list of tasks to the JSON file.

        Writes first to a temporary file in the same directory, flushes to disk,
        and then atomically renames it to target file name.

        Args:
            tasks: List of Task instances to serialize.

        Raises:
            StorageError: If writing or renaming fails.
        """
        raw_list = [task.to_dict() for task in tasks]
        parent_dir = self.file_path.parent

        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=parent_dir,
                delete=False,
                prefix="tasks_tmp_",
                suffix=".json",
            ) as tf:
                temp_file = tf.name
                json.dump(raw_list, tf, indent=2, ensure_ascii=False)
                tf.flush()
                os.fsync(tf.fileno())

            # Atomic replace
            os.replace(temp_file, self.file_path)

        except Exception as e:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            raise StorageError(f"Failed to save tasks to '{self.file_path}': {e}") from e

    def export_csv(self, tasks: List[Task], export_path: str | Path) -> None:
        """Export tasks into a standard CSV file format.

        Args:
            tasks: Tasks to export.
            export_path: Destination file path.
        """
        import csv

        dest = Path(export_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Title", "Description", "Priority", "Category",
                "Due Date", "Status", "Created At", "Completed At"
            ])
            for t in tasks:
                writer.writerow([
                    t.id,
                    t.title,
                    t.description,
                    t.priority.value,
                    t.category,
                    t.due_date or "",
                    "Completed" if t.completed else "Pending",
                    t.created_at,
                    t.completed_at or ""
                ])
