"""
To-Do List Application - GUI Module
Reference Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3

Production-grade Graphical User Interface built with Python's standard tkinter
and ttk libraries. Features modern layout, responsive filtering, live stats,
dialog editing, and keyboard shortcuts.
"""

from __future__ import annotations

import ctypes
import os
import sys
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from .manager import TaskManager, ValidationError
from .models import Category, Priority, Task

ASSET_REFERENCE = "cf772cd9-6178-4b38-b3a8-ee99efa59dc3"


def enable_high_dpi_awareness() -> None:
    """Enable high-DPI scaling on Windows systems for crisp fonts."""
    if sys.platform.startswith("win"):
        try:
            # Per-monitor DPI awareness (Windows 8.1+)
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                # System DPI awareness (Windows Vista+)
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


class EditTaskDialog(tk.Toplevel):
    """Modal dialog for editing an existing task's properties."""

    def __init__(self, parent: tk.Widget, task: Task, manager: TaskManager) -> None:
        super().__init__(parent)
        self.parent = parent
        self.task = task
        self.manager = manager
        self.saved = False

        self.title("Edit Task")
        self.geometry("480x360")
        self.minsize(420, 320)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_window()

    def _center_window(self) -> None:
        """Center the dialog over the parent window."""
        self.update_idletasks()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()

        w = self.winfo_width()
        h = self.winfo_height()
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding="16 16 16 16")
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(container, text="Task Title *:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 4)
        )
        self.title_var = tk.StringVar(value=self.task.title)
        self.title_entry = ttk.Entry(container, textvariable=self.title_var, font=("Segoe UI", 10))
        self.title_entry.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))

        # Description
        ttk.Label(container, text="Description / Notes:", font=("Segoe UI", 9)).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 4)
        )
        self.desc_text = tk.Text(container, height=4, font=("Segoe UI", 9), wrap=tk.WORD)
        self.desc_text.insert("1.0", self.task.description or "")
        self.desc_text.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))

        # Priority & Category
        row_frame = ttk.Frame(container)
        row_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))

        ttk.Label(row_frame, text="Priority:").pack(side=tk.LEFT, padx=(0, 6))
        self.priority_var = tk.StringVar(value=self.task.priority.value)
        pri_combo = ttk.Combobox(
            row_frame,
            textvariable=self.priority_var,
            values=[p.value for p in Priority],
            state="readonly",
            width=10,
        )
        pri_combo.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(row_frame, text="Category:").pack(side=tk.LEFT, padx=(0, 6))
        self.category_var = tk.StringVar(value=self.task.category)
        cat_combo = ttk.Combobox(
            row_frame,
            textvariable=self.category_var,
            values=self.manager.get_categories(),
            width=12,
        )
        cat_combo.pack(side=tk.LEFT)

        # Due Date
        date_frame = ttk.Frame(container)
        date_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 16))

        ttk.Label(date_frame, text="Due Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=(0, 6))
        self.date_var = tk.StringVar(value=self.task.due_date or "")
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=14)
        date_entry.pack(side=tk.LEFT, padx=(0, 8))

        clear_date_btn = ttk.Button(date_frame, text="Clear Date", command=lambda: self.date_var.set(""))
        clear_date_btn.pack(side=tk.LEFT)

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=6, column=0, columnspan=2, sticky=tk.E)

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))

        save_btn = ttk.Button(btn_frame, text="Save Changes", command=self._save)
        save_btn.pack(side=tk.RIGHT)

        container.columnconfigure(0, weight=1)
        self.title_entry.focus_set()

    def _save(self) -> None:
        new_title = self.title_var.get().strip()
        if not new_title:
            messagebox.showwarning("Validation Error", "Task title cannot be empty.", parent=self)
            self.title_entry.focus_set()
            return

        new_desc = self.desc_text.get("1.0", tk.END).strip()
        new_pri = self.priority_var.get()
        new_cat = self.category_var.get().strip() or Category.OTHER.value
        due_val = self.date_var.get().strip() or None

        try:
            self.manager.update_task(
                self.task.id,
                title=new_title,
                description=new_desc,
                priority=new_pri,
                category=new_cat,
                due_date=due_val,
                clear_due_date=(due_val is None),
            )
            self.saved = True
            self.destroy()
        except ValidationError as err:
            messagebox.showerror("Error", str(err), parent=self)


class TodoAppGUI(tk.Tk):
    """Main Application Window for the Python GUI To-Do List."""

    def __init__(self, manager: Optional[TaskManager] = None) -> None:
        enable_high_dpi_awareness()
        super().__init__()

        self.manager = manager or TaskManager()

        # Window configuration
        self.title(f"Task Master - To-Do List Application [{ASSET_REFERENCE[:8]}]")
        self.geometry("980x680")
        self.minsize(820, 540)

        # Active filter states
        self.status_filter = tk.StringVar(value="all")
        self.category_filter = tk.StringVar(value="all")
        self.sort_by = tk.StringVar(value="created_desc")
        self.search_query = tk.StringVar()

        self._configure_styles()
        self._build_ui()
        self._bind_shortcuts()
        self.refresh_task_list()

    def _configure_styles(self) -> None:
        """Configure ttk styles with a clean, modern palette."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Color constants
        self.c_primary = "#2563EB"       # Modern blue
        self.c_bg = "#F8FAFC"            # Light slate background
        self.c_card = "#FFFFFF"          # Pure white cards
        self.c_text = "#1E293B"          # Dark slate
        self.c_muted = "#64748B"         # Cool gray
        self.c_success = "#16A34A"       # Green
        self.c_danger = "#DC2626"        # Red
        self.c_warning = "#D97706"       # Amber
        self.c_border = "#E2E8F0"        # Light border

        self.configure(bg=self.c_bg)

        # General font definitions
        style.configure(".", font=("Segoe UI", 9), background=self.c_bg, foreground=self.c_text)
        style.configure("TFrame", background=self.c_bg)
        style.configure("Card.TFrame", background=self.c_card, relief="flat")

        # Headings
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.c_text, background=self.c_bg)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 8), foreground=self.c_muted, background=self.c_bg)
        style.configure("Asset.TLabel", font=("Segoe UI", 8, "italic"), foreground=self.c_muted, background=self.c_bg)

        # Stat cards
        style.configure("StatTitle.TLabel", font=("Segoe UI", 8), foreground=self.c_muted, background=self.c_card)
        style.configure("StatValue.TLabel", font=("Segoe UI", 14, "bold"), foreground=self.c_text, background=self.c_card)

        # Buttons
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), padding=6)
        style.configure("Action.TButton", padding=5)
        style.configure("Danger.TButton", foreground=self.c_danger, padding=5)

        # Treeview styling
        style.configure(
            "Tasks.Treeview",
            font=("Segoe UI", 9),
            rowheight=28,
            bordercolor=self.c_border,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Tasks.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#E2E8F0",
            foreground="#334155",
            padding=5,
        )
        style.map(
            "Tasks.Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#1E3A8A")],
        )

    def _build_ui(self) -> None:
        """Construct the main user interface hierarchy."""
        main_container = ttk.Frame(self, padding="16 16 16 12")
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Header & Live Dashboard
        self._build_header(main_container)

        # 2. Add New Task Input Card
        self._build_input_card(main_container)

        # 3. Filters & Search Toolbar
        self._build_toolbar(main_container)

        # 4. Tasks Treeview Table
        self._build_treeview(main_container)

        # 5. Bottom Action Controls & Status Bar
        self._build_footer(main_container)

    def _build_header(self, parent: ttk.Frame) -> None:
        """Build top header bar with title, asset ID, and live statistics."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 12))

        # Title block
        title_block = ttk.Frame(header_frame)
        title_block.pack(side=tk.LEFT)

        ttk.Label(title_block, text="Task Master", style="Header.TLabel").pack(anchor=tk.W)
        sub_text = f"Production To-Do List Application • Asset ID: {ASSET_REFERENCE}"
        ttk.Label(title_block, text=sub_text, style="Asset.TLabel").pack(anchor=tk.W)

        # Stat cards block
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side=tk.RIGHT)

        self.stat_widgets = {}
        for title, key in [
            ("Total Tasks", "total"),
            ("Pending", "pending"),
            ("Completed", "completed"),
            ("Overdue", "overdue"),
        ]:
            card = ttk.Frame(stats_frame, style="Card.TFrame", padding="8 4 8 4")
            card.pack(side=tk.LEFT, padx=4)
            ttk.Label(card, text=title, style="StatTitle.TLabel").pack()
            val_lbl = ttk.Label(card, text="0", style="StatValue.TLabel")
            val_lbl.pack()
            self.stat_widgets[key] = val_lbl

        # Progress bar
        progress_card = ttk.Frame(stats_frame, style="Card.TFrame", padding="8 4 8 4")
        progress_card.pack(side=tk.LEFT, padx=4)
        ttk.Label(progress_card, text="Progress", style="StatTitle.TLabel").pack()
        self.progress_val_lbl = ttk.Label(progress_card, text="0%", font=("Segoe UI", 9, "bold"), background=self.c_card)
        self.progress_val_lbl.pack()
        self.progress_bar = ttk.Progressbar(progress_card, length=70, mode="determinate")
        self.progress_bar.pack(pady=2)

    def _build_input_card(self, parent: ttk.Frame) -> None:
        """Build input form card for creating new tasks."""
        card = ttk.Frame(parent, style="Card.TFrame", padding="12 10 12 10")
        card.pack(fill=tk.X, pady=(0, 10))

        # Top row: Title input & Add button
        row1 = ttk.Frame(card, style="Card.TFrame")
        row1.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(row1, text="New Task:", font=("Segoe UI", 9, "bold"), background=self.c_card).pack(side=tk.LEFT, padx=(0, 6))
        self.entry_title = ttk.Entry(row1, font=("Segoe UI", 10))
        self.entry_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry_title.bind("<Return>", lambda e: self.on_add_task())

        add_btn = ttk.Button(row1, text="+ Add Task", style="Primary.TButton", command=self.on_add_task)
        add_btn.pack(side=tk.RIGHT)

        # Bottom row: Priority, Category, Due Date, Quick Dates
        row2 = ttk.Frame(card, style="Card.TFrame")
        row2.pack(fill=tk.X)

        ttk.Label(row2, text="Priority:", background=self.c_card).pack(side=tk.LEFT, padx=(0, 4))
        self.combo_priority = ttk.Combobox(
            row2,
            values=[p.value for p in Priority],
            state="readonly",
            width=9,
        )
        self.combo_priority.set(Priority.MEDIUM.value)
        self.combo_priority.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(row2, text="Category:", background=self.c_card).pack(side=tk.LEFT, padx=(0, 4))
        self.combo_category = ttk.Combobox(
            row2,
            values=self.manager.get_categories(),
            width=12,
        )
        self.combo_category.set(Category.WORK.value)
        self.combo_category.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(row2, text="Due Date:", background=self.c_card).pack(side=tk.LEFT, padx=(0, 4))
        self.entry_due_date = ttk.Entry(row2, width=12)
        self.entry_due_date.pack(side=tk.LEFT, padx=(0, 4))

        # Quick due date helper buttons
        ttk.Button(row2, text="Today", width=6, command=self._set_due_today).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="Tomorrow", width=8, command=self._set_due_tomorrow).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="Clear", width=5, command=lambda: self.entry_due_date.delete(0, tk.END)).pack(side=tk.LEFT, padx=2)

    def _set_due_today(self) -> None:
        self.entry_due_date.delete(0, tk.END)
        self.entry_due_date.insert(0, date.today().isoformat())

    def _set_due_tomorrow(self) -> None:
        self.entry_due_date.delete(0, tk.END)
        self.entry_due_date.insert(0, (date.today() + timedelta(days=1)).isoformat())

    def _build_toolbar(self, parent: ttk.Frame) -> None:
        """Build search, filter tabs, category filter, and sort options toolbar."""
        bar = ttk.Frame(parent)
        bar.pack(fill=tk.X, pady=(0, 8))

        # Status filter tabs (All / Pending / Completed / Overdue)
        tabs_frame = ttk.Frame(bar)
        tabs_frame.pack(side=tk.LEFT)

        for label, val in [("All", "all"), ("Pending", "pending"), ("Completed", "completed"), ("Overdue", "overdue")]:
            rb = ttk.Radiobutton(
                tabs_frame,
                text=label,
                value=val,
                variable=self.status_filter,
                command=self.refresh_task_list,
            )
            rb.pack(side=tk.LEFT, padx=(0, 8))

        # Separator
        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        # Category filter dropdown
        ttk.Label(bar, text="Category:").pack(side=tk.LEFT, padx=(0, 4))
        self.filter_cat_combo = ttk.Combobox(
            bar,
            textvariable=self.category_filter,
            values=["All"] + self.manager.get_categories(),
            state="readonly",
            width=12,
        )
        self.filter_cat_combo.set("All")
        self.filter_cat_combo.pack(side=tk.LEFT, padx=(0, 12))
        self.filter_cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_task_list())

        # Sort selector
        ttk.Label(bar, text="Sort By:").pack(side=tk.LEFT, padx=(0, 4))
        sort_combo = ttk.Combobox(
            bar,
            textvariable=self.sort_by,
            values=["Newest First", "Due Date", "Priority", "Title"],
            state="readonly",
            width=12,
        )
        sort_combo.set("Newest First")
        sort_combo.pack(side=tk.LEFT, padx=(0, 12))
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_task_list())

        # Search box (instant filter as user types)
        search_frame = ttk.Frame(bar)
        search_frame.pack(side=tk.RIGHT)

        ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_search = ttk.Entry(search_frame, textvariable=self.search_query, width=16)
        self.entry_search.pack(side=tk.LEFT)
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_task_list())

    def _build_treeview(self, parent: ttk.Frame) -> None:
        """Build tasks table with columns, scrollbar, and tag color mappings."""
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        columns = ("status", "title", "priority", "category", "due_date", "created_at")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="Tasks.Treeview",
            selectmode="extended",
        )

        # Configure columns
        self.tree.heading("status", text="Status", anchor=tk.CENTER)
        self.tree.heading("title", text="Task Title", anchor=tk.W)
        self.tree.heading("priority", text="Priority", anchor=tk.CENTER)
        self.tree.heading("category", text="Category", anchor=tk.CENTER)
        self.tree.heading("due_date", text="Due Date", anchor=tk.CENTER)
        self.tree.heading("created_at", text="Created", anchor=tk.CENTER)

        self.tree.column("status", width=95, minwidth=80, anchor=tk.CENTER, stretch=False)
        self.tree.column("title", width=360, minwidth=180, anchor=tk.W)
        self.tree.column("priority", width=90, minwidth=70, anchor=tk.CENTER, stretch=False)
        self.tree.column("category", width=110, minwidth=80, anchor=tk.CENTER, stretch=False)
        self.tree.column("due_date", width=110, minwidth=90, anchor=tk.CENTER, stretch=False)
        self.tree.column("created_at", width=130, minwidth=100, anchor=tk.CENTER, stretch=False)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Row styling tags
        self.tree.tag_configure("completed", foreground="#94A3B8")
        self.tree.tag_configure("priority_high", foreground="#DC2626")
        self.tree.tag_configure("priority_medium", foreground="#D97706")
        self.tree.tag_configure("priority_low", foreground="#16A34A")
        self.tree.tag_configure("overdue", background="#FEE2E2", foreground="#991B1B")

        # Double click to toggle or edit
        self.tree.bind("<Double-1>", lambda e: self.on_toggle_selected())
        self.tree.bind("<Return>", lambda e: self.on_toggle_selected())
        self.tree.bind("<Delete>", lambda e: self.on_delete_task())

        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Toggle Status (Complete/Pending)", command=self.on_toggle_selected)
        self.context_menu.add_command(label="Edit Task...", command=self.on_edit_task)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Task", command=self.on_delete_task)
        self.tree.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event: tk.Event) -> None:
        """Display right-click context menu on selected item."""
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _build_footer(self, parent: ttk.Frame) -> None:
        """Build action buttons bar and application status bar."""
        actions_bar = ttk.Frame(parent)
        actions_bar.pack(fill=tk.X, pady=(0, 6))

        # Left action buttons
        ttk.Button(actions_bar, text="✓ Toggle Complete", style="Action.TButton", command=self.on_toggle_selected).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions_bar, text="✎ Edit Task", style="Action.TButton", command=self.on_edit_task).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions_bar, text="🗑 Delete", style="Danger.TButton", command=self.on_delete_task).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions_bar, text="Clear Completed", style="Action.TButton", command=self.on_clear_completed).pack(side=tk.LEFT, padx=(0, 6))

        # Right action buttons
        ttk.Button(actions_bar, text="Export CSV", style="Action.TButton", command=self.on_export_csv).pack(side=tk.RIGHT)
        ttk.Button(actions_bar, text="Reload", style="Action.TButton", command=self.on_reload).pack(side=tk.RIGHT, padx=(0, 6))

        # Status Bar
        status_bar = ttk.Frame(parent)
        status_bar.pack(fill=tk.X)

        self.status_var = tk.StringVar(value="Ready. Double-click any task to toggle completion.")
        ttk.Label(status_bar, textvariable=self.status_var, style="SubHeader.TLabel").pack(side=tk.LEFT)

        file_note = f"File: {self.manager.storage.file_path.name}"
        ttk.Label(status_bar, text=file_note, style="SubHeader.TLabel").pack(side=tk.RIGHT)

    def _bind_shortcuts(self) -> None:
        """Bind productivity keyboard shortcuts."""
        self.bind("<Control-n>", lambda e: self.entry_title.focus_set())
        self.bind("<Control-f>", lambda e: self.entry_search.focus_set())
        self.bind("<Control-e>", lambda e: self.on_edit_task())
        self.bind("<space>", self._on_space_pressed)

    def _on_space_pressed(self, event: tk.Event) -> Optional[str]:
        """Toggle task on Spacebar if focused on the treeview."""
        if self.focus_get() == self.tree:
            self.on_toggle_selected()
            return "break"
        return None

    # -------------------------------------------------------------------------
    # UI Actions & Event Handlers
    # -------------------------------------------------------------------------

    def on_add_task(self) -> None:
        """Handle submission of a new task."""
        title = self.entry_title.get().strip()

        # Input validation: preventing empty task submissions
        if not title:
            messagebox.showwarning(
                "Input Required",
                "Task title cannot be empty! Please provide a description for the task.",
                parent=self,
            )
            self.entry_title.focus_set()
            return

        priority = self.combo_priority.get()
        category = self.combo_category.get().strip() or Category.OTHER.value
        due_date = self.entry_due_date.get().strip() or None

        try:
            task = self.manager.add_task(
                title=title,
                priority=priority,
                category=category,
                due_date=due_date,
            )
            # Clear input fields
            self.entry_title.delete(0, tk.END)
            self.entry_due_date.delete(0, tk.END)
            self.status_var.set(f"Added task: '{task.title}'")
            self.refresh_task_list()
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e), parent=self)

    def on_toggle_selected(self) -> None:
        """Toggle completion status for selected task(s)."""
        selected_ids = self.tree.selection()
        if not selected_ids:
            self.status_var.set("Please select a task to toggle.")
            return

        for task_id in selected_ids:
            try:
                task = self.manager.toggle_task(task_id)
                status = "completed" if task.completed else "reopened"
                self.status_var.set(f"Task '{task.title}' marked as {status}.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to toggle task: {e}", parent=self)

        self.refresh_task_list()

    def on_edit_task(self) -> None:
        """Open the modal edit dialog for the currently selected task."""
        selected_ids = self.tree.selection()
        if not selected_ids:
            messagebox.showinfo("Select Task", "Please select a task from the list to edit.", parent=self)
            return

        task_id = selected_ids[0]
        try:
            task = self.manager.get_task(task_id)
            dialog = EditTaskDialog(self, task, self.manager)
            self.wait_window(dialog)
            if dialog.saved:
                self.status_var.set(f"Task '{task.title}' updated successfully.")
                self.refresh_task_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load task: {e}", parent=self)

    def on_delete_task(self) -> None:
        """Delete selected task(s) after user confirmation."""
        selected_ids = self.tree.selection()
        if not selected_ids:
            messagebox.showinfo("Select Task", "Please select a task from the list to delete.", parent=self)
            return

        count = len(selected_ids)
        msg = f"Are you sure you want to delete {count} selected task(s)?" if count > 1 else "Are you sure you want to delete this task?"
        if not messagebox.askyesno("Confirm Delete", msg, parent=self):
            return

        for task_id in selected_ids:
            try:
                self.manager.delete_task(task_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete task: {e}", parent=self)

        self.status_var.set(f"Deleted {count} task(s).")
        self.refresh_task_list()

    def on_clear_completed(self) -> None:
        """Remove all completed tasks after confirmation."""
        stats = self.manager.get_stats()
        if stats["completed"] == 0:
            messagebox.showinfo("Info", "There are no completed tasks to clear.", parent=self)
            return

        if messagebox.askyesno("Clear Completed", f"Delete all {stats['completed']} completed task(s)?", parent=self):
            removed = self.manager.clear_completed()
            self.status_var.set(f"Cleared {removed} completed task(s).")
            self.refresh_task_list()

    def on_reload(self) -> None:
        """Reload tasks from disk."""
        self.manager.load()
        self.status_var.set("Tasks reloaded from file.")
        self.refresh_task_list()

    def on_export_csv(self) -> None:
        """Export current tasks to a user-chosen CSV file."""
        tasks = self.manager.get_all_tasks()
        if not tasks:
            messagebox.showinfo("Export", "No tasks available to export.", parent=self)
            return

        dest = filedialog.asksaveasfilename(
            parent=self,
            title="Export Tasks to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile="tasks_export.csv",
        )
        if not dest:
            return

        try:
            self.manager.storage.export_csv(tasks, dest)
            messagebox.showinfo("Export Successful", f"Successfully exported {len(tasks)} tasks to:\n{dest}", parent=self)
            self.status_var.set(f"Exported to {os.path.basename(dest)}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export file: {e}", parent=self)

    # -------------------------------------------------------------------------
    # Render & Refresh Logic
    # -------------------------------------------------------------------------

    def refresh_task_list(self) -> None:
        """Query manager with current filters and update the treeview & dashboard stats."""
        # Map sort label to manager parameter
        sort_map = {
            "Newest First": "created_desc",
            "Due Date": "due_date",
            "Priority": "priority",
            "Title": "title",
        }
        sort_key = sort_map.get(self.sort_by.get(), "created_desc")

        tasks = self.manager.filter_tasks(
            status=self.status_filter.get(),
            category=self.category_filter.get(),
            search_query=self.search_query.get(),
            sort_by=sort_key,
        )

        # Preserve selection if still visible
        selected = set(self.tree.selection())

        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in tasks:
            status_symbol = "✔ Done" if task.completed else "⭕ Active"
            tags = []

            if task.completed:
                tags.append("completed")
            elif task.is_overdue():
                tags.append("overdue")
            elif task.priority == Priority.HIGH:
                tags.append("priority_high")
            elif task.priority == Priority.MEDIUM:
                tags.append("priority_medium")
            elif task.priority == Priority.LOW:
                tags.append("priority_low")

            created_display = task.created_at[:16].replace("T", " ")
            due_display = task.due_date if task.due_date else "—"

            self.tree.insert(
                "",
                tk.END,
                iid=task.id,
                values=(
                    status_symbol,
                    task.title,
                    task.priority.value,
                    task.category,
                    due_display,
                    created_display,
                ),
                tags=tuple(tags),
            )

        # Restore selection
        for task_id in selected:
            if self.tree.exists(task_id):
                self.tree.selection_add(task_id)

        # Update category dropdown lists
        all_cats = ["All"] + self.manager.get_categories()
        self.filter_cat_combo["values"] = all_cats
        self.combo_category["values"] = self.manager.get_categories()

        # Update stat dashboard
        self._update_stats_dashboard()

    def _update_stats_dashboard(self) -> None:
        """Update stat numbers and progress bar based on current data."""
        stats = self.manager.get_stats()
        self.stat_widgets["total"].config(text=str(stats["total"]))
        self.stat_widgets["pending"].config(text=str(stats["pending"]))
        self.stat_widgets["completed"].config(text=str(stats["completed"]))
        self.stat_widgets["overdue"].config(text=str(stats["overdue"]))

        rate = stats["completion_rate"]
        self.progress_val_lbl.config(text=f"{int(rate)}%")
        self.progress_bar["value"] = rate


def launch_gui() -> None:
    """Entry point function to instantiate and run the Tkinter GUI."""
    app = TodoAppGUI()
    app.mainloop()
