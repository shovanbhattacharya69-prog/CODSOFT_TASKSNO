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

- **Modern & Attractive UI**:
  - **Card-Based Task Display**: Elegant cards with hover effects replacing legacy table rows.
  - **Dark / Light Mode**: Dynamic palette switcher with deep obsidian dark theme (`#0F172A`) and crisp clean light theme (`#F1F5F9`).
  - **Live Stat Chips**: Real-time counters for *Total Tasks*, *Active*, *Completed*, *Overdue*, and a progress percentage widget.
  - **Priority Pills**: Distinct color-coded badges for High (crimson), Medium (amber), and Low (emerald) priority.
  - **Smart Due Date Badges**: Dynamic status badges highlighting *Overdue* (red alert), *Due Today* (warm amber), or future scheduled dates.
  - **Friendly Empty State**: Welcoming illustration and message when all tasks are complete (`🎉 All caught up!`).
  - **Windows High-DPI Scaling**: Automatic per-monitor crisp typography using Segoe UI.

- **Core Task Operations (CRUD)**:
  - **Create**: Floating input card with auto-clearing placeholder, priority selector pills, category dropdown, and quick date helpers (*Today*, *Tomorrow*, *+7 Days*).
  - **Read / Track**: Scrollable task cards with instant interactive completion checkboxes.
  - **Update**: Modal edit dialog to update task title, notes, priority, category, and due date.
  - **Delete**: Individual deletion with confirmation prompts or bulk clearing of completed tasks.
  - **Search & Filter**: Real-time search-as-you-type filter, category filter, and status pills (*All*, *Active*, *Completed*, *Overdue*).

- **Enterprise-Grade Persistence**:
  - Atomic JSON file writing (`tempfile` + `os.replace` + `os.fsync`) preventing database corruption during sudden exits.
  - Automatic backup creation (`tasks.corrupt_<timestamp>.bak`) if an external corruption is encountered.
  - 1-click Export to standard CSV.

---

## 🏗️ Architecture & Project Structure

```
CODSOFT_TASKSNO_1/
├── todo_app/
│   ├── __init__.py          # Package metadata & asset reference
│   ├── models.py            # Task, Priority, and Category domain dataclasses
│   ├── storage.py           # Persistence engine with atomic writes & CSV export
│   ├── manager.py           # Business controller (CRUD, filtering, sorting, stats)
│   ├── gui.py               # Modern Card UI, Dark/Light theme, dialogs, styles
│   └── cli.py               # Headless CLI interface using argparse
├── tests/
│   ├── __init__.py
│   └── test_todo.py         # 17 automated unit tests
├── main.py                  # Universal launcher (GUI by default, CLI with subcommands)
├── TaskMaster.pyw           # Windowless direct double-click launcher
├── run.bat                  # 1-Click Windows batch launcher
├── run.ps1                  # PowerShell launcher script
├── build_standalone.bat     # Automated PyInstaller script to compile single-file .exe
├── requirements.txt         # Dev & build dependencies
├── tasks.json               # Local JSON task database
└── README.md                # System documentation
```

---

## 🚀 How to Run the Application

### Option 1: The 1-Click Launcher (Easiest)
Simply double-click **`run.bat`** or **`TaskMaster.pyw`** in File Explorer.

### Option 2: From the Terminal
```bash
py main.py
```
*(or `python main.py` if python is registered in your PATH)*

---

## 📦 Publishing as a Standalone Windows Executable (.exe)

To distribute this application to users who do not have Python installed:

1. Double-click **`build_standalone.bat`** (or run `py -m PyInstaller --onefile --windowed --name "TaskMaster_Pro" main.py`).
2. Your standalone executable will be packaged into:
   ```text
   dist\TaskMaster_Pro.exe
   ```
3. Share `TaskMaster_Pro.exe` directly with anyone—it runs with zero dependencies!

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
