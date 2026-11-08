"""
To-Do List Application - CLI Module
Reference Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3

Provides a robust, command-line interface for the To-Do application using argparse.
Allows headless execution, batch script automation, and terminal task tracking.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .manager import TaskManager, ValidationError
from .models import Priority


def run_cli(args: Optional[List[str]] = None, manager: Optional[TaskManager] = None) -> int:
    """Parse command line arguments and execute the corresponding task operation.

    Args:
        args: Optional list of command-line argument strings (defaults to sys.argv[1:]).
        manager: Optional TaskManager instance.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    mgr = manager or TaskManager()

    parser = argparse.ArgumentParser(
        prog="todo",
        description="Production To-Do List Application [Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3]",
        epilog="Run without arguments or with --gui to start the Tkinter GUI interface.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available sub-commands")

    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new task")
    parser_add.add_argument("title", type=str, help="Task title / description")
    parser_add.add_argument("-d", "--desc", default="", help="Detailed notes/description")
    parser_add.add_argument(
        "-p",
        "--priority",
        choices=["Low", "Medium", "High"],
        default="Medium",
        help="Priority level (default: Medium)",
    )
    parser_add.add_argument("-c", "--category", default="Other", help="Task category")
    parser_add.add_argument("--due", help="Due date (YYYY-MM-DD)")

    # List command
    parser_list = subparsers.add_parser("list", help="List and track tasks")
    parser_list.add_argument(
        "-s",
        "--status",
        choices=["all", "pending", "completed", "overdue"],
        default="all",
        help="Filter by status (default: all)",
    )
    parser_list.add_argument("-c", "--category", default="all", help="Filter by category")
    parser_list.add_argument("-p", "--priority", help="Filter by priority (Low/Medium/High)")
    parser_list.add_argument("-q", "--search", help="Search string in title/notes")

    # Done / Toggle command
    parser_done = subparsers.add_parser("done", help="Toggle or mark a task as completed")
    parser_done.add_argument("id", help="Task ID (full or starting 8 chars)")

    # Delete command
    parser_del = subparsers.add_parser("delete", help="Delete a task")
    parser_del.add_argument("id", help="Task ID (full or starting 8 chars)")

    # Clear completed
    subparsers.add_parser("clear-completed", help="Remove all completed tasks")

    # Stats command
    subparsers.add_parser("stats", help="Show summary statistics")

    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 0

    try:
        if parsed.command == "add":
            task = mgr.add_task(
                title=parsed.title,
                description=parsed.desc,
                priority=parsed.priority,
                category=parsed.category,
                due_date=parsed.due,
            )
            print(f"[OK] Task added successfully: [{task.id[:8]}] {task.title} (Priority: {task.priority.value})")
            return 0

        elif parsed.command == "list":
            tasks = mgr.filter_tasks(
                status=parsed.status,
                category=parsed.category,
                priority=parsed.priority,
                search_query=parsed.search,
            )
            if not tasks:
                print("No tasks found matching criteria.")
                return 0

            print(f"\n{'ID':<10} {'Status':<10} {'Priority':<10} {'Due Date':<12} {'Category':<12} {'Title'}")
            print("-" * 80)
            for t in tasks:
                status = "[DONE]" if t.completed else "[TODO]"
                due = t.due_date or "-"
                print(f"{t.id[:8]:<10} {status:<10} {t.priority.value:<10} {due:<12} {t.category:<12} {t.title}")
            print(f"\nTotal listed: {len(tasks)}")
            return 0

        elif parsed.command == "done":
            target_id = _resolve_task_id(mgr, parsed.id)
            task = mgr.toggle_task(target_id)
            state = "Completed" if task.completed else "Reopened"
            print(f"[OK] Task '{task.title}' [{task.id[:8]}] is now {state}.")
            return 0

        elif parsed.command == "delete":
            target_id = _resolve_task_id(mgr, parsed.id)
            task = mgr.delete_task(target_id)
            print(f"[OK] Task '{task.title}' [{task.id[:8]}] has been deleted.")
            return 0

        elif parsed.command == "clear-completed":
            count = mgr.clear_completed()
            print(f"[OK] Cleared {count} completed task(s).")
            return 0

        elif parsed.command == "stats":
            stats = mgr.get_stats()
            print("\n--- Task Management Statistics ---")
            print(f"Total Tasks:     {stats['total']}")
            print(f"Pending Tasks:   {stats['pending']}")
            print(f"Completed Tasks: {stats['completed']}")
            print(f"Overdue Tasks:   {stats['overdue']}")
            print(f"Completion Rate: {stats['completion_rate']}%")
            print("----------------------------------\n")
            return 0

    except ValidationError as ve:
        print(f"Error: {ve}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    return 0


def _resolve_task_id(mgr: TaskManager, prefix_or_id: str) -> str:
    """Find matching task ID by full UUID or prefix."""
    prefix = prefix_or_id.strip().lower()
    matches = [t.id for t in mgr.get_all_tasks() if t.id.lower().startswith(prefix)]
    if not matches:
        raise ValueError(f"No task found matching prefix '{prefix_or_id}'.")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous ID prefix '{prefix_or_id}'. Matches multiple tasks: {matches}")
    return matches[0]
