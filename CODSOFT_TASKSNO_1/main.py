"""
Production-Ready To-Do List Application
Reference Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3

Entry point script for launching the Graphical User Interface (GUI)
or Command Line Interface (CLI) based on runtime arguments.

Usage:
    # Launch standard Tkinter GUI application:
    python main.py

    # Launch CLI commands:
    python main.py add "Review quarterly budget" --priority High --due 2026-11-15
    python main.py list
    python main.py done <task_id>
    python main.py delete <task_id>
    python main.py stats
"""

from __future__ import annotations

import sys

ASSET_REFERENCE = "cf772cd9-6178-4b38-b3a8-ee99efa59dc3"


def main() -> int:
    """Evaluate execution arguments and launch GUI or CLI frontend."""
    cli_commands = {"add", "list", "done", "delete", "clear-completed", "stats", "-h", "--help"}

    # If CLI subcommands or flags were supplied
    if len(sys.argv) > 1 and (sys.argv[1] in cli_commands or sys.argv[1].startswith("-")):
        from todo_app.cli import run_cli
        return run_cli(sys.argv[1:])

    # Default to modern Tkinter GUI
    from todo_app.gui import launch_gui
    launch_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
