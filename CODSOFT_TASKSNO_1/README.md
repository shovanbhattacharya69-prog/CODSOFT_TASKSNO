# Python GUI To-Do List Application

> **Project Asset Reference:** `cf772cd9-6178-4b38-b3a8-ee99efa59dc3`  
> **Role & Architecture:** Senior Python Developer | Production-Ready Modular Design  
> **Interface:** Tkinter Desktop GUI + Full-Featured Headless CLI (`argparse`)

---

## 📌 Overview

The **Python GUI To-Do List Application** is a production-grade task management system designed to help users organize, track, and complete daily tasks efficiently. Built using Python 3 and Tkinter with a contemporary design layout, it adheres strictly to **PEP-8** standards, includes comprehensive docstrings across all modules, and provides zero-dependency portability.

In addition to the rich GUI experience, the application includes a headless Command Line Interface (CLI) powered by `argparse` for terminal power users, automation pipelines, and CI/CD testing environments.

---

## ✨ Features

- **Intuitive GUI**:
  - Crisp typography with automatic Windows High-DPI scaling.
  - Live statistics dashboard (Total, Pending, Completed, Overdue, % Progress).
  - Clean card-based form input with quick due date helpers (*Today*, *Tomorrow*).
- **Core Task Operations (CRUD)**:
  - **Create**: Add tasks with title, description/notes, priority level (*High*, *Medium*, *Low*), category, and due date.
  - **Read / Track**: View tasks in a structured tabular treeview with status indicators.
  - **Update**: In-place toggle completion with spacebar/double-click, or edit all fields via the modal dialog.
  - **Delete**: Remove individual tasks with confirmation dialogs or bulk-clear all completed tasks.
- **Search, Filter & Sort**:
  - Filter tasks instantly by status (*All*, *Pending*, *Completed*, *Overdue*).
  - Filter by category (*Work*, *Personal*, *Study*, *Health*, *Finance*, etc.).
  - Instant as-you-type search across task titles and descriptions.
  - Multi-criteria sorting (Newest first, Due Date, Priority rank, Alphabetical).
- **Enterprise-Grade Persistence**:
  - Atomic JSON file writing (`tempfile` + `os.replace`) to prevent corrupted files on sudden shutdown.
  - Automatic backup generation if corrupted data is encountered (`tasks.corrupt_<timestamp>.bak`).
  - Export task lists to standard CSV format.
- **Robust Error Handling**:
  - Validation prevents empty task submissions, blank whitespace, and malformed date strings.
  - Friendly graphical alerts (`messagebox.showwarning` / `messagebox.showerror`).

---

## 🏗️ Architecture & Project Structure

The project follows clean MVC (Model-View-Controller) principles and modular separation of concerns:

```
CODSOFT_TASKSNO_1/
├── todo_app/
│   ├── __init__.py      # Package definitions & asset reference metadata
│   ├── models.py        # Domain entities (Task, Priority, Category dataclasses)
│   ├── storage.py       # Persistence layer with atomic write & backup handling
│   ├── manager.py       # Business logic layer (CRUD, filtering, sorting, metrics)
│   ├── gui.py           # Tkinter GUI implementation (views, dialogs, styles)
│   └── cli.py           # Headless CLI implementation using argparse
├── tests/
│   ├── __init__.py
│   └── test_todo.py     # 17 automated unit tests covering all components
├── main.py              # Application entrypoint (auto-routes to GUI or CLI)
├── requirements.txt     # Standard dependencies and dev tooling
└── README.md            # Comprehensive system documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (Python 3.10+ recommended).
- Tkinter (included by default in standard Python distributions).

### Launching the GUI Application

To launch the graphical desktop interface:

```bash
python main.py
```

---

## ⌨️ GUI Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Enter` (in input field) | Add new task |
| `Space` (on task list) | Toggle task completion (*Active* / *Done*) |
| `Double-Click` | Toggle task completion |
| `Delete` | Delete selected task(s) |
| `Ctrl + N` | Focus the *New Task* input box |
| `Ctrl + F` | Focus the *Search* input box |
| `Ctrl + E` | Open the *Edit Task* dialog |
| `Right-Click` | Open task context menu (*Edit*, *Toggle*, *Delete*) |

---

## 💻 Command Line Interface (CLI) Usage

The application seamlessly supports CLI subcommands using the same business engine and storage file:

### 1. Add a Task
```bash
python main.py add "Review quarterly sprint goals" --priority High --category Work --due 2026-11-20
```

### 2. List Tasks
```bash
# List all tasks
python main.py list

# Filter by status
python main.py list --status pending
python main.py list --status overdue

# Filter by category or search term
python main.py list --category Work --search "sprint"
```

### 3. Complete or Toggle a Task
```bash
# Accepts either full task UUID or the first 8 characters
python main.py done <task_id>
```

### 4. Delete a Task
```bash
python main.py delete <task_id>
```

### 5. Clear Completed Tasks
```bash
python main.py clear-completed
```

### 6. View Analytics & Statistics
```bash
python main.py stats
```

---

## 🧪 Running Automated Unit Tests

A comprehensive unit test suite with 17 test cases verifies model validation, persistence recovery, sorting, filtering, and CLI interactions:

```bash
python -m unittest discover -s tests -v
```

Expected output:
```
test_add_task_validation (test_todo.TestTaskManager.test_add_task_validation) ... ok
test_delete_and_not_found (test_todo.TestTaskManager.test_delete_and_not_found) ... ok
test_filtering_and_stats (test_todo.TestTaskManager.test_filtering_and_stats) ... ok
test_toggle_and_clear_completed (test_todo.TestTaskManager.test_toggle_and_clear_completed) ... ok
test_update_task (test_todo.TestTaskManager.test_update_task) ... ok
...
Ran 17 tests in 0.214s

OK
```

---

## 🔒 Error Handling & Quality Guarantees

1. **Input Validation**: Prevents blank or whitespace-only task entries. Displays direct feedback to the user without crashing.
2. **Date Format Verification**: Enforces `YYYY-MM-DD` formatting, rejecting invalid calendar dates gracefully.
3. **Atomic File Storage**: Writes JSON payloads to a temporary file before committing the file rename (`os.replace`), guarding against data corruption during unexpected shutdowns.
4. **Data Recovery**: If the persistence file is externally corrupted, it is automatically backed up to `tasks.corrupt_<timestamp>.bak` and a clean workspace is initialized.
5. **Code Style**: Strictly compliant with PEP-8 formatting, type annotations, and explicit docstrings across all modules.

---

## 📄 License & Asset Details

- **Asset Reference**: `cf772cd9-6178-4b38-b3a8-ee99efa59dc3`
- **Author**: Senior Python Developer
- **Status**: Production-Ready
