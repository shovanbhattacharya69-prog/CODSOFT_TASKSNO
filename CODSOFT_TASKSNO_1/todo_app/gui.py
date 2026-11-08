"""
To-Do List Application - Modern GUI Module
Reference Asset: cf772cd9-6178-4b38-b3a8-ee99efa59dc3

Production-grade Graphical User Interface built with Python's standard tkinter
and ttk libraries. Features modern card-based task rendering, Dark/Light mode,
live stat widgets, priority pills, date badges, search, and keyboard shortcuts.
"""

from __future__ import annotations

import ctypes
import os
import sys
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from .manager import TaskManager, ValidationError
from .models import Category, Priority, Task

ASSET_REFERENCE = "cf772cd9-6178-4b38-b3a8-ee99efa59dc3"


def enable_high_dpi_awareness() -> None:
    """Enable high-DPI scaling on Windows systems for crisp fonts."""
    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Theme Palettes
# ---------------------------------------------------------------------------

THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "bg_app": "#F1F5F9",          # Soft slate light background
        "bg_header": "#0F172A",       # Deep navy hero header
        "fg_header_title": "#FFFFFF",
        "fg_header_sub": "#94A3B8",
        "bg_card": "#FFFFFF",         # Pure white cards
        "bg_card_hover": "#F8FAFC",   # Hover subtle tint
        "bg_card_done": "#F8FAFC",    # Completed task background
        "border": "#E2E8F0",          # Crisp border
        "border_focus": "#3B82F6",    # Blue focus outline
        "fg_primary": "#0F172A",      # High contrast dark text
        "fg_secondary": "#475569",    # Medium contrast secondary text
        "fg_muted": "#94A3B8",        # Subtle text
        "accent": "#2563EB",          # Royal blue primary accent
        "accent_hover": "#1D4ED8",
        "accent_text": "#FFFFFF",
        # Stat cards
        "stat_card_bg": "#1E293B",
        "stat_label": "#94A3B8",
        "stat_num": "#FFFFFF",
        # Priority pill badges
        "pri_high_bg": "#FEE2E2",
        "pri_high_fg": "#DC2626",
        "pri_med_bg": "#FEF3C7",
        "pri_med_fg": "#D97706",
        "pri_low_bg": "#DCFCE7",
        "pri_low_fg": "#16A34A",
        # Category badge
        "cat_bg": "#E2E8F0",
        "cat_fg": "#334155",
        # Due date badge
        "due_normal_bg": "#F1F5F9",
        "due_normal_fg": "#475569",
        "due_overdue_bg": "#FEE2E2",
        "due_overdue_fg": "#B91C1C",
        "due_today_bg": "#FEF3C7",
        "due_today_fg": "#B45309",
        # Checkbox
        "check_border": "#94A3B8",
        "check_active_bg": "#10B981",
        "check_active_fg": "#FFFFFF",
    },
    "dark": {
        "bg_app": "#0F172A",          # Deep midnight background
        "bg_header": "#020617",       # Pure obsidian hero header
        "fg_header_title": "#F8FAFC",
        "fg_header_sub": "#64748B",
        "bg_card": "#1E293B",         # Rich slate card
        "bg_card_hover": "#273549",   # Slightly lighter slate hover
        "bg_card_done": "#182234",    # Muted slate for completed
        "border": "#334155",          # Subtle dark border
        "border_focus": "#60A5FA",
        "fg_primary": "#F8FAFC",      # Bright text
        "fg_secondary": "#CBD5E1",    # Soft gray text
        "fg_muted": "#64748B",        # Dim text
        "accent": "#3B82F6",          # Vibrant blue
        "accent_hover": "#60A5FA",
        "accent_text": "#FFFFFF",
        # Stat cards
        "stat_card_bg": "#0B132B",
        "stat_label": "#64748B",
        "stat_num": "#F8FAFC",
        # Priority pill badges
        "pri_high_bg": "#450A0A",
        "pri_high_fg": "#F87171",
        "pri_med_bg": "#451A03",
        "pri_med_fg": "#FBBF24",
        "pri_low_bg": "#064E3B",
        "pri_low_fg": "#34D399",
        # Category badge
        "cat_bg": "#334155",
        "cat_fg": "#E2E8F0",
        # Due date badge
        "due_normal_bg": "#334155",
        "due_normal_fg": "#CBD5E1",
        "due_overdue_bg": "#450A0A",
        "due_overdue_fg": "#FCA5A5",
        "due_today_bg": "#451A03",
        "due_today_fg": "#FDE68A",
        # Checkbox
        "check_border": "#64748B",
        "check_active_bg": "#059669",
        "check_active_fg": "#FFFFFF",
    },
}


class ModernButton(tk.Canvas):
    """Custom anti-aliased styled rounded button for polished UX."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Any = None,
        bg: str = "#2563EB",
        fg: str = "#FFFFFF",
        hover_bg: str = "#1D4ED8",
        font: tuple = ("Segoe UI", 9, "bold"),
        width: int = 100,
        height: int = 32,
        radius: int = 8,
        cursor: str = "hand2",
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent["bg"] if "bg" in parent.keys() else "#FFFFFF",
            highlightthickness=0,
            cursor=cursor,
        )
        self.text = text
        self.command = command
        self.btn_bg = bg
        self.btn_fg = fg
        self.hover_bg = hover_bg
        self.btn_font = font
        self.btn_width = width
        self.btn_height = height
        self.radius = radius

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        self._draw(self.btn_bg)

    def _draw(self, fill_color: str) -> None:
        self.delete("all")
        w, h, r = self.btn_width, self.btn_height, self.radius
        # Draw rounded rectangle
        self.create_arc((0, 0, 2 * r, 2 * r), start=90, extent=90, fill=fill_color, outline=fill_color)
        self.create_arc((w - 2 * r, 0, w, 2 * r), start=0, extent=90, fill=fill_color, outline=fill_color)
        self.create_arc((0, h - 2 * r, 2 * r, h), start=180, extent=90, fill=fill_color, outline=fill_color)
        self.create_arc((w - 2 * r, h - 2 * r, w, h), start=270, extent=90, fill=fill_color, outline=fill_color)
        self.create_rectangle((r, 0, w - r, h), fill=fill_color, outline=fill_color)
        self.create_rectangle((0, r, w, h - r), fill=fill_color, outline=fill_color)
        # Draw text
        self.create_text(w / 2, h / 2, text=self.text, fill=self.btn_fg, font=self.btn_font)

    def _on_enter(self, _event: tk.Event) -> None:
        self._draw(self.hover_bg)

    def _on_leave(self, _event: tk.Event) -> None:
        self._draw(self.btn_bg)

    def _on_click(self, _event: tk.Event) -> None:
        if self.command:
            self.command()

    def update_colors(self, bg: str, fg: str, hover_bg: str, parent_bg: str) -> None:
        """Update colors dynamically when theme toggles."""
        self.configure(bg=parent_bg)
        self.btn_bg = bg
        self.btn_fg = fg
        self.hover_bg = hover_bg
        self._draw(self.btn_bg)


class EditTaskDialog(tk.Toplevel):
    """Modal dialog with styled fields for editing an existing task."""

    def __init__(self, parent: tk.Widget, task: Task, manager: TaskManager, theme_mode: str = "light") -> None:
        super().__init__(parent)
        self.parent = parent
        self.task = task
        self.manager = manager
        self.theme = THEMES[theme_mode]
        self.saved = False

        self.title("Edit Task Details")
        self.geometry("520x420")
        self.minsize(460, 380)
        self.configure(bg=self.theme["bg_card"])
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_window()

    def _center_window(self) -> None:
        self.update_idletasks()
        pw, ph = self.parent.winfo_width(), self.parent.winfo_height()
        px, py = self.parent.winfo_rootx(), self.parent.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self) -> None:
        t = self.theme
        container = tk.Frame(self, bg=t["bg_card"], padx=24, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Header Title
        tk.Label(
            container,
            text="Edit Task",
            font=("Segoe UI", 14, "bold"),
            bg=t["bg_card"],
            fg=t["fg_primary"],
        ).pack(anchor=tk.W, pady=(0, 14))

        # Title Field
        tk.Label(
            container,
            text="Task Title *",
            font=("Segoe UI", 9, "bold"),
            bg=t["bg_card"],
            fg=t["fg_secondary"],
        ).pack(anchor=tk.W, pady=(0, 4))
        self.title_var = tk.StringVar(value=self.task.title)
        self.title_entry = tk.Entry(
            container,
            textvariable=self.title_var,
            font=("Segoe UI", 10),
            bg=t["bg_app"],
            fg=t["fg_primary"],
            insertbackground=t["fg_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["accent"],
        )
        self.title_entry.pack(fill=tk.X, ipady=6, pady=(0, 12))

        # Description / Notes
        tk.Label(
            container,
            text="Notes / Description",
            font=("Segoe UI", 9, "bold"),
            bg=t["bg_card"],
            fg=t["fg_secondary"],
        ).pack(anchor=tk.W, pady=(0, 4))
        self.desc_text = tk.Text(
            container,
            height=3,
            font=("Segoe UI", 9),
            bg=t["bg_app"],
            fg=t["fg_primary"],
            insertbackground=t["fg_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["accent"],
            wrap=tk.WORD,
        )
        self.desc_text.insert("1.0", self.task.description or "")
        self.desc_text.pack(fill=tk.X, pady=(0, 12))

        # Priority & Category row
        row = tk.Frame(container, bg=t["bg_card"])
        row.pack(fill=tk.X, pady=(0, 12))

        # Priority
        col1 = tk.Frame(row, bg=t["bg_card"])
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(col1, text="Priority", font=("Segoe UI", 9, "bold"), bg=t["bg_card"], fg=t["fg_secondary"]).pack(anchor=tk.W, pady=(0, 4))
        self.priority_var = tk.StringVar(value=self.task.priority.value)
        pri_combo = ttk.Combobox(
            col1,
            textvariable=self.priority_var,
            values=[p.value for p in Priority],
            state="readonly",
        )
        pri_combo.pack(fill=tk.X)

        # Category
        col2 = tk.Frame(row, bg=t["bg_card"])
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(col2, text="Category", font=("Segoe UI", 9, "bold"), bg=t["bg_card"], fg=t["fg_secondary"]).pack(anchor=tk.W, pady=(0, 4))
        self.category_var = tk.StringVar(value=self.task.category)
        cat_combo = ttk.Combobox(
            col2,
            textvariable=self.category_var,
            values=self.manager.get_categories(),
        )
        cat_combo.pack(fill=tk.X)

        # Due Date
        tk.Label(
            container,
            text="Due Date (YYYY-MM-DD)",
            font=("Segoe UI", 9, "bold"),
            bg=t["bg_card"],
            fg=t["fg_secondary"],
        ).pack(anchor=tk.W, pady=(0, 4))

        date_row = tk.Frame(container, bg=t["bg_card"])
        date_row.pack(fill=tk.X, pady=(0, 18))

        self.date_var = tk.StringVar(value=self.task.due_date or "")
        self.date_entry = tk.Entry(
            date_row,
            textvariable=self.date_var,
            font=("Segoe UI", 10),
            bg=t["bg_app"],
            fg=t["fg_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["accent"],
            width=18,
        )
        self.date_entry.pack(side=tk.LEFT, ipady=4, padx=(0, 8))

        tk.Button(
            date_row,
            text="Clear Date",
            command=lambda: self.date_var.set(""),
            font=("Segoe UI", 8),
            bg=t["bg_app"],
            fg=t["fg_secondary"],
            relief="flat",
            padx=8,
            pady=3,
        ).pack(side=tk.LEFT)

        # Action Buttons
        btn_row = tk.Frame(container, bg=t["bg_card"])
        btn_row.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            btn_row,
            text="Cancel",
            command=self.destroy,
            font=("Segoe UI", 9),
            bg=t["bg_app"],
            fg=t["fg_secondary"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(
            btn_row,
            text="Save Changes",
            command=self._save,
            font=("Segoe UI", 9, "bold"),
            bg=t["accent"],
            fg=t["accent_text"],
            activebackground=t["accent_hover"],
            activeforeground=t["accent_text"],
            relief="flat",
            padx=18,
            pady=6,
            cursor="hand2",
        ).pack(side=tk.RIGHT)

        self.title_entry.focus_set()

    def _save(self) -> None:
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Validation Error", "Task title cannot be empty.", parent=self)
            self.title_entry.focus_set()
            return

        desc = self.desc_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        category = self.category_var.get().strip() or Category.OTHER.value
        due_val = self.date_var.get().strip() or None

        try:
            self.manager.update_task(
                self.task.id,
                title=title,
                description=desc,
                priority=priority,
                category=category,
                due_date=due_val,
                clear_due_date=(due_val is None),
            )
            self.saved = True
            self.destroy()
        except ValidationError as err:
            messagebox.showerror("Error", str(err), parent=self)


class TodoAppGUI(tk.Tk):
    """Modern Production-Ready To-Do List Application GUI."""

    def __init__(self, manager: Optional[TaskManager] = None) -> None:
        enable_high_dpi_awareness()
        super().__init__()

        self.manager = manager or TaskManager()
        self.theme_mode = "light"  # Default light, toggleable to "dark"
        self.theme = THEMES[self.theme_mode]

        # Window Setup
        self.title("TaskMaster Pro — Productivity & Task Management")
        self.geometry("1060x740")
        self.minsize(880, 580)
        self.configure(bg=self.theme["bg_app"])

        # Filter and Search State
        self.current_status_filter = "all"
        self.current_category_filter = "All"
        self.current_sort_by = "Newest First"
        self.search_text = tk.StringVar()
        self.selected_priority_input = "Medium"

        # UI Element references for dynamic theme updates
        self.theme_elements: List[Any] = []
        self.filter_buttons: Dict[str, tk.Button] = {}

        self._configure_ttk_styles()
        self._build_ui()
        self._bind_shortcuts()
        self.refresh_task_cards()

    def _configure_ttk_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", font=("Segoe UI", 9))

    def _build_ui(self) -> None:
        """Construct the full modern application layout."""
        # Main root layout container
        self.main_container = tk.Frame(self, bg=self.theme["bg_app"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Hero Header Bar & Dashboard Stats
        self._build_header(self.main_container)

        # 2. Modern Quick-Create Card
        self._build_input_card(self.main_container)

        # 3. Interactive Filter Pills & Search Bar
        self._build_filter_bar(self.main_container)

        # 4. Scrollable Task Cards View
        self._build_task_scroll_area(self.main_container)

        # 5. Bottom Action Bar & Status Toast
        self._build_bottom_bar(self.main_container)

    # -------------------------------------------------------------------------
    # UI Component Builders
    # -------------------------------------------------------------------------

    def _build_header(self, parent: tk.Frame) -> None:
        """Render hero top bar with title, asset ID, theme switch, and stat cards."""
        t = self.theme
        self.header_frame = tk.Frame(parent, bg=t["bg_header"], padx=24, pady=16)
        self.header_frame.pack(fill=tk.X)

        # Left branding
        brand_frame = tk.Frame(self.header_frame, bg=t["bg_header"])
        brand_frame.pack(side=tk.LEFT)

        title_row = tk.Frame(brand_frame, bg=t["bg_header"])
        title_row.pack(anchor=tk.W)

        self.lbl_logo = tk.Label(
            title_row,
            text="✓",
            font=("Segoe UI", 16, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            padx=8,
            pady=0,
        )
        self.lbl_logo.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_title = tk.Label(
            title_row,
            text="TaskMaster Pro",
            font=("Segoe UI", 16, "bold"),
            bg=t["bg_header"],
            fg=t["fg_header_title"],
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_asset = tk.Label(
            brand_frame,
            text=f"Production Task Engine • Asset: {ASSET_REFERENCE[:18]}...",
            font=("Segoe UI", 8),
            bg=t["bg_header"],
            fg=t["fg_header_sub"],
        )
        self.lbl_asset.pack(anchor=tk.W, pady=(4, 0))

        # Right side: Theme Toggle & Stat Widgets
        right_header = tk.Frame(self.header_frame, bg=t["bg_header"])
        right_header.pack(side=tk.RIGHT)

        # Dark/Light Mode Switch
        self.btn_theme_toggle = tk.Button(
            right_header,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            font=("Segoe UI", 8, "bold"),
            bg=t["stat_card_bg"],
            fg=t["fg_header_title"],
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
        )
        self.btn_theme_toggle.pack(side=tk.LEFT, padx=(0, 16))

        # Live Stat Cards
        self.stat_labels: Dict[str, tk.Label] = {}
        for key, label in [("total", "Total"), ("pending", "Pending"), ("completed", "Done"), ("overdue", "Overdue")]:
            card = tk.Frame(right_header, bg=t["stat_card_bg"], padx=12, pady=6)
            card.pack(side=tk.LEFT, padx=4)

            tk.Label(card, text=label, font=("Segoe UI", 7, "bold"), bg=t["stat_card_bg"], fg=t["stat_label"]).pack()
            val_lbl = tk.Label(card, text="0", font=("Segoe UI", 13, "bold"), bg=t["stat_card_bg"], fg=t["stat_num"])
            val_lbl.pack()
            self.stat_labels[key] = val_lbl

        # Progress Chip
        prog_card = tk.Frame(right_header, bg=t["stat_card_bg"], padx=12, pady=6)
        prog_card.pack(side=tk.LEFT, padx=4)
        tk.Label(prog_card, text="Progress", font=("Segoe UI", 7, "bold"), bg=t["stat_card_bg"], fg=t["stat_label"]).pack()
        self.lbl_progress = tk.Label(prog_card, text="0%", font=("Segoe UI", 13, "bold"), bg=t["stat_card_bg"], fg="#38BDF8")
        self.lbl_progress.pack()

    def _build_input_card(self, parent: tk.Frame) -> None:
        """Card layout for quickly adding tasks with priority and due date."""
        t = self.theme
        self.input_card = tk.Frame(parent, bg=t["bg_card"], padx=18, pady=12, relief="flat", highlightthickness=1, highlightbackground=t["border"])
        self.input_card.pack(fill=tk.X, padx=20, pady=(14, 10))

        # Row 1: Task Title & Add Button
        r1 = tk.Frame(self.input_card, bg=t["bg_card"])
        r1.pack(fill=tk.X, pady=(0, 8))

        self.entry_task_title = tk.Entry(
            r1,
            font=("Segoe UI", 11),
            bg=t["bg_app"],
            fg=t["fg_primary"],
            insertbackground=t["fg_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["accent"],
        )
        self.entry_task_title.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
        self.entry_task_title.bind("<Return>", lambda e: self.on_add_task())
        self._add_placeholder(self.entry_task_title, "What needs to be done? Press Enter to save...")

        self.btn_add_task = tk.Button(
            r1,
            text="+ Add Task",
            command=self.on_add_task,
            font=("Segoe UI", 10, "bold"),
            bg=t["accent"],
            fg=t["accent_text"],
            activebackground=t["accent_hover"],
            activeforeground=t["accent_text"],
            relief="flat",
            padx=18,
            pady=6,
            cursor="hand2",
        )
        self.btn_add_task.pack(side=tk.RIGHT)

        # Row 2: Priority Pills, Category Dropdown, Due Date & Helpers
        r2 = tk.Frame(self.input_card, bg=t["bg_card"])
        r2.pack(fill=tk.X)

        # Priority Selector Pills
        tk.Label(r2, text="Priority:", font=("Segoe UI", 8, "bold"), bg=t["bg_card"], fg=t["fg_secondary"]).pack(side=tk.LEFT, padx=(0, 6))
        self.priority_buttons: Dict[str, tk.Button] = {}
        for p_name in ["Low", "Medium", "High"]:
            btn = tk.Button(
                r2,
                text=p_name,
                command=lambda p=p_name: self._set_priority_input(p),
                font=("Segoe UI", 8),
                relief="flat",
                padx=8,
                pady=2,
                cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.priority_buttons[p_name] = btn
        self._update_priority_button_styles()

        # Category Dropdown
        tk.Label(r2, text="Category:", font=("Segoe UI", 8, "bold"), bg=t["bg_card"], fg=t["fg_secondary"]).pack(side=tk.LEFT, padx=(14, 6))
        self.combo_category = ttk.Combobox(
            r2,
            values=self.manager.get_categories(),
            width=11,
            state="readonly",
        )
        self.combo_category.set(Category.WORK.value)
        self.combo_category.pack(side=tk.LEFT, padx=(0, 14))

        # Due Date Entry
        tk.Label(r2, text="Due Date:", font=("Segoe UI", 8, "bold"), bg=t["bg_card"], fg=t["fg_secondary"]).pack(side=tk.LEFT, padx=(0, 6))
        self.entry_due_date = tk.Entry(
            r2,
            font=("Segoe UI", 9),
            bg=t["bg_app"],
            fg=t["fg_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["accent"],
            width=12,
        )
        self.entry_due_date.pack(side=tk.LEFT, ipady=3, padx=(0, 6))

        # Quick Date buttons
        for label, delta_days in [("Today", 0), ("Tomorrow", 1), ("+7 Days", 7)]:
            tk.Button(
                r2,
                text=label,
                command=lambda d=delta_days: self._set_quick_date(d),
                font=("Segoe UI", 7),
                bg=t["bg_app"],
                fg=t["fg_secondary"],
                relief="flat",
                padx=5,
                pady=2,
                cursor="hand2",
            ).pack(side=tk.LEFT, padx=1)

        tk.Button(
            r2,
            text="✕",
            command=lambda: self.entry_due_date.delete(0, tk.END),
            font=("Segoe UI", 7),
            bg=t["bg_app"],
            fg=t["fg_muted"],
            relief="flat",
            padx=4,
            pady=2,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(2, 0))

    def _set_priority_input(self, priority: str) -> None:
        self.selected_priority_input = priority
        self._update_priority_button_styles()

    def _update_priority_button_styles(self) -> None:
        t = self.theme
        for name, btn in self.priority_buttons.items():
            if name == self.selected_priority_input:
                if name == "High":
                    btn.configure(bg=t["pri_high_bg"], fg=t["pri_high_fg"], font=("Segoe UI", 8, "bold"))
                elif name == "Medium":
                    btn.configure(bg=t["pri_med_bg"], fg=t["pri_med_fg"], font=("Segoe UI", 8, "bold"))
                else:
                    btn.configure(bg=t["pri_low_bg"], fg=t["pri_low_fg"], font=("Segoe UI", 8, "bold"))
            else:
                btn.configure(bg=t["bg_app"], fg=t["fg_muted"], font=("Segoe UI", 8))

    def _set_quick_date(self, days_ahead: int) -> None:
        target_date = (date.today() + timedelta(days=days_ahead)).isoformat()
        self.entry_due_date.delete(0, tk.END)
        self.entry_due_date.insert(0, target_date)

    def _add_placeholder(self, entry: tk.Entry, placeholder: str) -> None:
        """Add modern auto-clearing placeholder to an entry field."""
        def on_focus_in(event: tk.Event) -> None:
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.configure(fg=self.theme["fg_primary"])

        def on_focus_out(event: tk.Event) -> None:
            if not entry.get().strip():
                entry.delete(0, tk.END)
                entry.insert(0, placeholder)
                entry.configure(fg=self.theme["fg_muted"])

        entry.insert(0, placeholder)
        entry.configure(fg=self.theme["fg_muted"])
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _build_filter_bar(self, parent: tk.Frame) -> None:
        """Construct segmented status filter pills and search bar."""
        t = self.theme
        self.filter_bar = tk.Frame(parent, bg=t["bg_app"], padx=20)
        self.filter_bar.pack(fill=tk.X, pady=(4, 8))

        # Filter Pills container
        pills_frame = tk.Frame(self.filter_bar, bg=t["bg_app"])
        pills_frame.pack(side=tk.LEFT)

        filters = [("all", "All Tasks"), ("pending", "Active"), ("completed", "Completed"), ("overdue", "Overdue")]
        for key, label in filters:
            btn = tk.Button(
                pills_frame,
                text=label,
                command=lambda k=key: self._set_status_filter(k),
                font=("Segoe UI", 8, "bold" if key == "all" else "normal"),
                relief="flat",
                padx=10,
                pady=4,
                cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self.filter_buttons[key] = btn
        self._update_filter_button_styles()

        # Category Filter Dropdown
        tk.Label(self.filter_bar, text="Category:", font=("Segoe UI", 8, "bold"), bg=t["bg_app"], fg=t["fg_secondary"]).pack(side=tk.LEFT, padx=(12, 4))
        self.filter_cat_combo = ttk.Combobox(
            self.filter_bar,
            values=["All"] + self.manager.get_categories(),
            state="readonly",
            width=11,
        )
        self.filter_cat_combo.set("All")
        self.filter_cat_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_task_cards())

        # Sort Dropdown
        tk.Label(self.filter_bar, text="Sort:", font=("Segoe UI", 8, "bold"), bg=t["bg_app"], fg=t["fg_secondary"]).pack(side=tk.LEFT, padx=(0, 4))
        self.combo_sort = ttk.Combobox(
            self.filter_bar,
            values=["Newest First", "Due Date", "Priority", "Title"],
            state="readonly",
            width=12,
        )
        self.combo_sort.set("Newest First")
        self.combo_sort.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_sort.bind("<<ComboboxSelected>>", lambda e: self.refresh_task_cards())

        # Search Bar
        search_frame = tk.Frame(self.filter_bar, bg=t["bg_app"])
        search_frame.pack(side=tk.RIGHT)

        tk.Label(search_frame, text="🔍", font=("Segoe UI", 9), bg=t["bg_app"], fg=t["fg_muted"]).pack(side=tk.LEFT, padx=(0, 4))
        self.entry_search = tk.Entry(
            search_frame,
            textvariable=self.search_text,
            font=("Segoe UI", 9),
            bg=t["bg_card"],
            fg=t["fg_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["accent"],
            width=18,
        )
        self.entry_search.pack(side=tk.LEFT, ipady=3)
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_task_cards())

        # Clear search button
        tk.Button(
            search_frame,
            text="✕",
            command=self._clear_search,
            font=("Segoe UI", 7),
            bg=t["bg_app"],
            fg=t["fg_muted"],
            relief="flat",
            padx=4,
            pady=2,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(2, 0))

    def _clear_search(self) -> None:
        self.search_text.set("")
        self.refresh_task_cards()

    def _set_status_filter(self, status: str) -> None:
        self.current_status_filter = status
        self._update_filter_button_styles()
        self.refresh_task_cards()

    def _update_filter_button_styles(self) -> None:
        t = self.theme
        for key, btn in self.filter_buttons.items():
            if key == self.current_status_filter:
                btn.configure(bg=t["accent"], fg=t["accent_text"], font=("Segoe UI", 8, "bold"))
            else:
                btn.configure(bg=t["bg_card"], fg=t["fg_secondary"], font=("Segoe UI", 8))

    def _build_task_scroll_area(self, parent: tk.Frame) -> None:
        """Build smooth scrollable cards container."""
        t = self.theme
        self.cards_outer = tk.Frame(parent, bg=t["bg_app"], padx=20)
        self.cards_outer.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Canvas with mousewheel scrolling
        self.canvas = tk.Canvas(self.cards_outer, bg=t["bg_app"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.cards_outer, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=t["bg_app"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Make scrollable frame expand width with canvas
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )

        # Mousewheel binding
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_bottom_bar(self, parent: tk.Frame) -> None:
        """Footer with bulk actions and status toast."""
        t = self.theme
        self.bottom_bar = tk.Frame(parent, bg=t["bg_header"], padx=20, pady=8)
        self.bottom_bar.pack(fill=tk.X)

        # Status Toast Message
        self.lbl_status = tk.Label(
            self.bottom_bar,
            text="Ready. Click any checkbox or card to complete a task.",
            font=("Segoe UI", 8),
            bg=t["bg_header"],
            fg=t["fg_header_sub"],
        )
        self.lbl_status.pack(side=tk.LEFT)

        # Right Action Buttons
        btn_box = tk.Frame(self.bottom_bar, bg=t["bg_header"])
        btn_box.pack(side=tk.RIGHT)

        tk.Button(
            btn_box,
            text="Clear Completed",
            command=self.on_clear_completed,
            font=("Segoe UI", 8),
            bg=t["stat_card_bg"],
            fg=t["fg_header_title"],
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_box,
            text="Export CSV",
            command=self.on_export_csv,
            font=("Segoe UI", 8),
            bg=t["stat_card_bg"],
            fg=t["fg_header_title"],
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=4)

    # -------------------------------------------------------------------------
    # Task Rendering: Modern Cards View
    # -------------------------------------------------------------------------

    def refresh_task_cards(self) -> None:
        """Fetch filtered tasks and generate modern visual cards in scrollable frame."""
        t = self.theme
        # Destroy existing cards
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        sort_map = {
            "Newest First": "created_desc",
            "Due Date": "due_date",
            "Priority": "priority",
            "Title": "title",
        }
        sort_key = sort_map.get(self.combo_sort.get(), "created_desc")

        tasks = self.manager.filter_tasks(
            status=self.current_status_filter,
            category=self.filter_cat_combo.get(),
            search_query=self.search_text.get(),
            sort_by=sort_key,
        )

        # Empty State
        if not tasks:
            self._render_empty_state()
            self._update_stats_dashboard()
            return

        # Render each task as an interactive Card
        for task in tasks:
            self._create_task_card(task)

        # Update stats
        self._update_stats_dashboard()

    def _render_empty_state(self) -> None:
        """Render a friendly, clean empty-state graphic when no tasks match."""
        t = self.theme
        empty_box = tk.Frame(self.scrollable_frame, bg=t["bg_app"], pady=60)
        empty_box.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            empty_box,
            text="🎉",
            font=("Segoe UI", 36),
            bg=t["bg_app"],
        ).pack(pady=(0, 6))

        tk.Label(
            empty_box,
            text="All caught up!",
            font=("Segoe UI", 14, "bold"),
            bg=t["bg_app"],
            fg=t["fg_primary"],
        ).pack()

        tk.Label(
            empty_box,
            text="No tasks match your current filter. Enjoy your day or add a new task above.",
            font=("Segoe UI", 9),
            bg=t["bg_app"],
            fg=t["fg_muted"],
        ).pack(pady=(4, 0))

    def _create_task_card(self, task: Task) -> None:
        """Render an individual interactive task card."""
        t = self.theme
        card_bg = t["bg_card_done"] if task.completed else t["bg_card"]
        card = tk.Frame(
            self.scrollable_frame,
            bg=card_bg,
            padx=14,
            pady=10,
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
        )
        card.pack(fill=tk.X, pady=4)

        # 1. Custom Checkbox button
        check_symbol = "✔" if task.completed else ""
        chk_bg = t["check_active_bg"] if task.completed else card_bg
        chk_fg = t["check_active_fg"] if task.completed else t["fg_primary"]

        chk_btn = tk.Button(
            card,
            text=check_symbol,
            command=lambda tid=task.id: self.on_toggle_task(tid),
            font=("Segoe UI", 10, "bold"),
            bg=chk_bg,
            fg=chk_fg,
            activebackground=t["check_active_bg"],
            activeforeground="#FFFFFF",
            relief="solid",
            bd=1,
            width=2,
            height=1,
            cursor="hand2",
        )
        chk_btn.pack(side=tk.LEFT, padx=(0, 12))

        # 2. Main Task Details Block
        details = tk.Frame(card, bg=card_bg)
        details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Title row
        title_font = ("Segoe UI", 10, "overstrike" if task.completed else "bold")
        title_fg = t["fg_muted"] if task.completed else t["fg_primary"]

        title_lbl = tk.Label(
            details,
            text=task.title,
            font=title_font,
            bg=card_bg,
            fg=title_fg,
            anchor=tk.W,
        )
        title_lbl.pack(anchor=tk.W)

        # Badges row: Priority Pill, Category, Due Date, Timestamp
        badges = tk.Frame(details, bg=card_bg)
        badges.pack(anchor=tk.W, pady=(4, 0))

        # Priority Pill
        if task.priority == Priority.HIGH:
            pri_bg, pri_fg = t["pri_high_bg"], t["pri_high_fg"]
        elif task.priority == Priority.LOW:
            pri_bg, pri_fg = t["pri_low_bg"], t["pri_low_fg"]
        else:
            pri_bg, pri_fg = t["pri_med_bg"], t["pri_med_fg"]

        tk.Label(
            badges,
            text=f"● {task.priority.value.upper()}",
            font=("Segoe UI", 7, "bold"),
            bg=pri_bg,
            fg=pri_fg,
            padx=6,
            pady=1,
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Category Pill
        tk.Label(
            badges,
            text=task.category,
            font=("Segoe UI", 7),
            bg=t["cat_bg"],
            fg=t["cat_fg"],
            padx=6,
            pady=1,
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Due Date Pill
        if task.due_date:
            if task.completed:
                due_bg, due_fg = t["cat_bg"], t["fg_muted"]
                due_prefix = "📅"
            elif task.is_overdue():
                due_bg, due_fg = t["due_overdue_bg"], t["due_overdue_fg"]
                due_prefix = "⚠️ Overdue:"
            elif task.due_date == date.today().isoformat():
                due_bg, due_fg = t["due_today_bg"], t["due_today_fg"]
                due_prefix = "⏰ Due Today:"
            else:
                due_bg, due_fg = t["due_normal_bg"], t["due_normal_fg"]
                due_prefix = "📅"

            tk.Label(
                badges,
                text=f"{due_prefix} {task.due_date}",
                font=("Segoe UI", 7, "bold" if task.is_overdue() else "normal"),
                bg=due_bg,
                fg=due_fg,
                padx=6,
                pady=1,
            ).pack(side=tk.LEFT, padx=(0, 6))

        # Optional Description snippet
        if task.description:
            tk.Label(
                details,
                text=task.description[:80] + ("..." if len(task.description) > 80 else ""),
                font=("Segoe UI", 8),
                bg=card_bg,
                fg=t["fg_muted"],
                anchor=tk.W,
            ).pack(anchor=tk.W, pady=(2, 0))

        # 3. Action Buttons on Right (Edit, Delete)
        actions = tk.Frame(card, bg=card_bg)
        actions.pack(side=tk.RIGHT)

        tk.Button(
            actions,
            text="✎ Edit",
            command=lambda tid=task.id: self.on_edit_task(tid),
            font=("Segoe UI", 8),
            bg=card_bg,
            fg=t["fg_secondary"],
            relief="flat",
            padx=8,
            pady=4,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            actions,
            text="🗑 Delete",
            command=lambda tid=task.id: self.on_delete_task(tid),
            font=("Segoe UI", 8),
            bg=card_bg,
            fg="#EF4444",
            relief="flat",
            padx=8,
            pady=4,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=2)

        # Hover Effect
        def on_enter(e: tk.Event) -> None:
            if not task.completed:
                card.configure(bg=t["bg_card_hover"])
                details.configure(bg=t["bg_card_hover"])
                title_lbl.configure(bg=t["bg_card_hover"])
                badges.configure(bg=t["bg_card_hover"])
                actions.configure(bg=t["bg_card_hover"])

        def on_leave(e: tk.Event) -> None:
            if not task.completed:
                card.configure(bg=card_bg)
                details.configure(bg=card_bg)
                title_lbl.configure(bg=card_bg)
                badges.configure(bg=card_bg)
                actions.configure(bg=card_bg)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    def _update_stats_dashboard(self) -> None:
        """Update numbers and progress bar based on manager calculations."""
        stats = self.manager.get_stats()
        self.stat_labels["total"].config(text=str(stats["total"]))
        self.stat_labels["pending"].config(text=str(stats["pending"]))
        self.stat_labels["completed"].config(text=str(stats["completed"]))
        self.stat_labels["overdue"].config(text=str(stats["overdue"]))

        rate = stats["completion_rate"]
        self.lbl_progress.config(text=f"{int(rate)}%")

    # -------------------------------------------------------------------------
    # Theme Toggle Logic
    # -------------------------------------------------------------------------

    def toggle_theme(self) -> None:
        """Switch smoothly between Dark and Light mode."""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.theme = THEMES[self.theme_mode]
        t = self.theme

        self.configure(bg=t["bg_app"])
        self.main_container.configure(bg=t["bg_app"])
        self.header_frame.configure(bg=t["bg_header"])
        self.lbl_title.configure(bg=t["bg_header"], fg=t["fg_header_title"])
        self.lbl_asset.configure(bg=t["bg_header"], fg=t["fg_header_sub"])
        self.btn_theme_toggle.configure(
            text="☀️ Light Mode" if self.theme_mode == "dark" else "🌙 Dark Mode",
            bg=t["stat_card_bg"],
            fg=t["fg_header_title"],
        )

        for card in self.stat_labels.values():
            parent_card = card.master
            parent_card.configure(bg=t["stat_card_bg"])
            card.configure(bg=t["stat_card_bg"], fg=t["stat_num"])
            # Update label in same card
            for child in parent_card.winfo_children():
                if child != card:
                    child.configure(bg=t["stat_card_bg"], fg=t["stat_label"])

        self.lbl_progress.master.configure(bg=t["stat_card_bg"])
        self.lbl_progress.configure(bg=t["stat_card_bg"])
        for child in self.lbl_progress.master.winfo_children():
            if child != self.lbl_progress:
                child.configure(bg=t["stat_card_bg"], fg=t["stat_label"])

        # Input card
        self.input_card.configure(bg=t["bg_card"], highlightbackground=t["border"])
        self.input_card.master.configure(bg=t["bg_app"])
        self.entry_task_title.configure(bg=t["bg_app"], fg=t["fg_primary"], insertbackground=t["fg_primary"], highlightbackground=t["border"])
        self.entry_due_date.configure(bg=t["bg_app"], fg=t["fg_primary"], insertbackground=t["fg_primary"], highlightbackground=t["border"])
        self.btn_add_task.configure(bg=t["accent"], fg=t["accent_text"], activebackground=t["accent_hover"])
        self._update_priority_button_styles()

        # Filter bar
        self.filter_bar.configure(bg=t["bg_app"])
        self.entry_search.configure(bg=t["bg_card"], fg=t["fg_primary"], insertbackground=t["fg_primary"], highlightbackground=t["border"])
        self._update_filter_button_styles()

        # Cards area
        self.cards_outer.configure(bg=t["bg_app"])
        self.canvas.configure(bg=t["bg_app"])
        self.scrollable_frame.configure(bg=t["bg_app"])

        # Bottom bar
        self.bottom_bar.configure(bg=t["bg_header"])
        self.lbl_status.configure(bg=t["bg_header"], fg=t["fg_header_sub"])

        self.refresh_task_cards()

    # -------------------------------------------------------------------------
    # Core Operations (CRUD)
    # -------------------------------------------------------------------------

    def on_add_task(self) -> None:
        """Add new task with validation."""
        title = self.entry_task_title.get().strip()
        placeholder = "What needs to be done? Press Enter to save..."

        if not title or title == placeholder:
            messagebox.showwarning(
                "Input Required",
                "Task title cannot be empty! Please provide a name for your task.",
                parent=self,
            )
            self.entry_task_title.focus_set()
            return

        priority = self.selected_priority_input
        category = self.combo_category.get().strip() or Category.WORK.value
        due_date = self.entry_due_date.get().strip() or None

        try:
            task = self.manager.add_task(
                title=title,
                priority=priority,
                category=category,
                due_date=due_date,
            )
            self.entry_task_title.delete(0, tk.END)
            self.entry_due_date.delete(0, tk.END)
            self.lbl_status.config(text=f"Task added: '{task.title}'")
            self.refresh_task_cards()
        except ValidationError as err:
            messagebox.showerror("Validation Error", str(err), parent=self)

    def on_toggle_task(self, task_id: str) -> None:
        """Toggle completion status for task."""
        try:
            task = self.manager.toggle_task(task_id)
            state = "completed 🎉" if task.completed else "active"
            self.lbl_status.config(text=f"Task '{task.title}' marked as {state}.")
            self.refresh_task_cards()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle task: {e}", parent=self)

    def on_edit_task(self, task_id: str) -> None:
        """Open modern edit dialog."""
        try:
            task = self.manager.get_task(task_id)
            dialog = EditTaskDialog(self, task, self.manager, theme_mode=self.theme_mode)
            self.wait_window(dialog)
            if dialog.saved:
                self.lbl_status.config(text=f"Task '{task.title}' updated successfully.")
                self.refresh_task_cards()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open edit dialog: {e}", parent=self)

    def on_delete_task(self, task_id: str) -> None:
        """Delete task after prompt confirmation."""
        try:
            task = self.manager.get_task(task_id)
            if messagebox.askyesno("Confirm Delete", f"Delete task '{task.title}'?", parent=self):
                self.manager.delete_task(task_id)
                self.lbl_status.config(text=f"Deleted task '{task.title}'.")
                self.refresh_task_cards()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete task: {e}", parent=self)

    def on_clear_completed(self) -> None:
        """Remove all completed tasks."""
        stats = self.manager.get_stats()
        if stats["completed"] == 0:
            messagebox.showinfo("Clear Completed", "No completed tasks to clear.", parent=self)
            return

        if messagebox.askyesno("Clear Completed", f"Delete all {stats['completed']} completed task(s)?", parent=self):
            removed = self.manager.clear_completed()
            self.lbl_status.config(text=f"Cleared {removed} completed task(s).")
            self.refresh_task_cards()

    def on_export_csv(self) -> None:
        """Export tasks into a CSV file."""
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
            messagebox.showinfo("Export Successful", f"Exported {len(tasks)} tasks to:\n{dest}", parent=self)
            self.lbl_status.config(text=f"Exported to {os.path.basename(dest)}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export CSV: {e}", parent=self)

    def _bind_shortcuts(self) -> None:
        """Keyboard productivity shortcuts."""
        self.bind("<Control-n>", lambda e: self.entry_task_title.focus_set())
        self.bind("<Control-f>", lambda e: self.entry_search.focus_set())
        self.bind("<Control-d>", lambda e: self.toggle_theme())


def launch_gui() -> None:
    """Entry point for running the GUI."""
    app = TodoAppGUI()
    app.mainloop()
