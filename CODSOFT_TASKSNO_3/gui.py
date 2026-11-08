"""
Rock-Paper-Scissors Game - Modern Tkinter Graphical User Interface.

Production-ready GUI with responsive design, dynamic duel animations,
live scoreboard, match history modal, keyboard shortcuts, and soundless visual feedback.
Adheres strictly to PEP-8 and clean separation of concerns.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from game_logic import Choice, GameEngine, GameMode, GameResult, RoundRecord

# Asset file reference for documentation and UI attribution
ASSET_ID: str = "3e548554-5bb7-4004-a613-8069b078f30e"

# UI Color Palette (Modern Slate & Neon Accents)
BG_DARK = "#0f172a"        # Deep slate background
BG_CARD = "#1e293b"        # Card background
BG_CARD_ALT = "#334155"    # Card border / secondary
TEXT_PRIMARY = "#f8fafc"   # Clean bright white
TEXT_MUTED = "#94a3b8"     # Subdued gray/blue
ACCENT_BLUE = "#3b82f6"    # Primary action blue
ACCENT_GREEN = "#10b981"   # Victory green
ACCENT_RED = "#ef4444"     # Defeat red
ACCENT_AMBER = "#f59e0b"   # Tie / warning amber
ACCENT_PURPLE = "#8b5cf6"  # Special badge


class HistoryDialog(tk.Toplevel):
    """Modal dialog displaying the full round-by-round match history."""

    def __init__(self, parent: tk.Widget, engine: GameEngine) -> None:
        super().__init__(parent)
        self.title("Match History & Analytics")
        self.geometry("640x450")
        self.minsize(550, 350)
        self.configure(bg=BG_DARK)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        # Header
        header_frame = tk.Frame(self, bg=BG_DARK, pady=12)
        header_frame.pack(fill=tk.X, padx=16)

        title = tk.Label(
            header_frame,
            text="📜 Round-by-Round History",
            font=("Segoe UI", 16, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_DARK,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header_frame,
            text=f"Total Rounds: {engine.total_rounds} | Win Rate: {engine.user_win_rate}% | Best Streak: {engine.best_streak}",
            font=("Segoe UI", 10),
            fg=TEXT_MUTED,
            bg=BG_DARK,
        )
        subtitle.pack(anchor="w")

        # Table Container
        table_frame = tk.Frame(self, bg=BG_CARD)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        columns = ("round", "user", "comp", "result", "explanation", "time")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.tree.heading("round", text="Round")
        self.tree.heading("user", text="You")
        self.tree.heading("comp", text="Computer")
        self.tree.heading("result", text="Result")
        self.tree.heading("explanation", text="Detail")
        self.tree.heading("time", text="Time")

        self.tree.column("round", width=60, anchor="center")
        self.tree.column("user", width=90, anchor="center")
        self.tree.column("comp", width=90, anchor="center")
        self.tree.column("result", width=80, anchor="center")
        self.tree.column("explanation", width=220, anchor="w")
        self.tree.column("time", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Style Treeview
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=BG_CARD,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_CARD,
            font=("Segoe UI", 10),
            rowheight=26,
        )
        style.configure(
            "Treeview.Heading",
            background=BG_CARD_ALT,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", ACCENT_BLUE)])

        # Populate rows (newest first)
        for record in reversed(engine.history):
            tag = record.result.name.lower()
            self.tree.insert(
                "",
                tk.END,
                values=(
                    f"#{record.round_number}",
                    f"{record.user_choice.emoji} {record.user_choice.value}",
                    f"{record.computer_choice.emoji} {record.computer_choice.value}",
                    record.result.value,
                    record.explanation,
                    record.timestamp.strftime("%H:%M:%S"),
                ),
                tags=(tag,),
            )

        self.tree.tag_configure("win", foreground=ACCENT_GREEN)
        self.tree.tag_configure("loss", foreground=ACCENT_RED)
        self.tree.tag_configure("tie", foreground=ACCENT_AMBER)

        # Close Button
        btn_close = tk.Button(
            self,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=BG_CARD_ALT,
            fg=TEXT_PRIMARY,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.destroy,
        )
        btn_close.pack(pady=12)


class RulesDialog(tk.Toplevel):
    """Informational dialog showing official game rules and shortcuts."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.title("Game Rules & Hotkeys")
        self.geometry("520x420")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        content = tk.Frame(self, bg=BG_DARK, padx=24, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            content,
            text="📖 How to Play Rock-Paper-Scissors",
            font=("Segoe UI", 14, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_DARK,
        ).pack(anchor="w", pady=(0, 10))

        rules_text = (
            "• Rock beats Scissors (Crushes)\n"
            "• Scissors beats Paper (Cuts)\n"
            "• Paper beats Rock (Covers)\n"
            "• Identical selections result in a Tie!\n\n"
            "🎯 Match Modes:\n"
            "• Endless Casual: Play continuously with rolling stats.\n"
            "• Best of 3: First to 2 points wins the series.\n"
            "• Best of 5: First to 3 points wins the series.\n\n"
            "⌨️ Keyboard Shortcuts:\n"
            "• [R] : Select Rock\n"
            "• [P] : Select Paper\n"
            "• [S] : Select Scissors\n"
            "• [Space] : Ready Next Round\n"
            "• [H] : Open Match History\n"
            "• [Ctrl+R] : Reset Scores"
        )

        lbl_rules = tk.Label(
            content,
            text=rules_text,
            font=("Segoe UI", 10),
            justify=tk.LEFT,
            fg=TEXT_MUTED,
            bg=BG_DARK,
            anchor="w",
        )
        lbl_rules.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            content,
            text=f"Asset ID: {ASSET_ID}",
            font=("Segoe UI", 8),
            fg=BG_CARD_ALT,
            bg=BG_DARK,
        ).pack(anchor="w")

        btn_ok = tk.Button(
            content,
            text="Got It!",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_BLUE,
            fg=TEXT_PRIMARY,
            activebackground="#2563eb",
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.destroy,
        )
        btn_ok.pack(side=tk.BOTTOM, pady=(10, 0))


class RockPaperScissorsGUI:
    """
    Main Application Window and Controller for Rock-Paper-Scissors.
    Coordinates between user actions, GameEngine domain logic, and graphical presentation.
    """

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the GUI application window and widgets."""
        self.root = root
        self.engine = GameEngine(mode=GameMode.CASUAL)
        self._is_animating: bool = False

        self._configure_root_window()
        self._create_widgets()
        self._bind_shortcuts()
        self._refresh_scoreboard()

    def _configure_root_window(self) -> None:
        """Configure main window title, geometry, minimum size, and icon style."""
        self.root.title("Rock-Paper-Scissors • Production Edition")
        self.root.geometry("780x760")
        self.root.minsize(720, 700)
        self.root.configure(bg=BG_DARK)

    def _create_widgets(self) -> None:
        """Instantiate and lay out all UI components."""
        # Main Scrollable / Padded Container
        self.main_container = tk.Frame(self.root, bg=BG_DARK, padx=24, pady=16)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self._build_header()
        self._build_scoreboard()
        self._build_duel_arena()
        self._build_result_banner()
        self._build_controls()
        self._build_footer()

    def _build_header(self) -> None:
        """Build top header with title, mode selector, and quick actions."""
        header_frame = tk.Frame(self.main_container, bg=BG_DARK)
        header_frame.pack(fill=tk.X, pady=(0, 14))

        title_box = tk.Frame(header_frame, bg=BG_DARK)
        title_box.pack(side=tk.LEFT)

        app_title = tk.Label(
            title_box,
            text="ROCK  •  PAPER  •  SCISSORS",
            font=("Segoe UI", 18, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_DARK,
        )
        app_title.pack(anchor="w")

        app_subtitle = tk.Label(
            title_box,
            text="Human vs. Machine Duel Arena",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_DARK,
        )
        app_subtitle.pack(anchor="w")

        # Right side: Game Mode selector and Info button
        mode_box = tk.Frame(header_frame, bg=BG_DARK)
        mode_box.pack(side=tk.RIGHT)

        tk.Label(
            mode_box,
            text="Mode:",
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_MUTED,
            bg=BG_DARK,
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.mode_var = tk.StringVar(value=GameMode.CASUAL.value)
        mode_menu = ttk.Combobox(
            mode_box,
            textvariable=self.mode_var,
            values=[m.value for m in GameMode],
            state="readonly",
            width=22,
            font=("Segoe UI", 9),
        )
        mode_menu.pack(side=tk.LEFT, padx=(0, 8))
        mode_menu.bind("<<ComboboxSelected>>", self._on_mode_change)

        btn_info = tk.Button(
            mode_box,
            text="❓ Rules",
            font=("Segoe UI", 9),
            bg=BG_CARD_ALT,
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._show_rules,
        )
        btn_info.pack(side=tk.LEFT)

    def _build_scoreboard(self) -> None:
        """Build statistical cards showing live player score, computer score, and streaks."""
        score_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=16, pady=12)
        score_frame.pack(fill=tk.X, pady=(0, 14))

        # 4 Column Grid: Player, Ties, Computer, Metrics
        score_frame.columnconfigure(0, weight=1)
        score_frame.columnconfigure(1, weight=1)
        score_frame.columnconfigure(2, weight=1)
        score_frame.columnconfigure(3, weight=1)

        # Player Score Card
        p_card = tk.Frame(score_frame, bg=BG_CARD)
        p_card.grid(row=0, column=0, sticky="nsew", padx=6)
        tk.Label(p_card, text="👤 PLAYER", font=("Segoe UI", 10, "bold"), fg=ACCENT_GREEN, bg=BG_CARD).pack()
        self.lbl_player_score = tk.Label(
            p_card, text="0", font=("Segoe UI", 26, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD
        )
        self.lbl_player_score.pack()

        # Tie Card
        t_card = tk.Frame(score_frame, bg=BG_CARD)
        t_card.grid(row=0, column=1, sticky="nsew", padx=6)
        tk.Label(t_card, text="🤝 DRAWS", font=("Segoe UI", 10, "bold"), fg=ACCENT_AMBER, bg=BG_CARD).pack()
        self.lbl_tie_score = tk.Label(
            t_card, text="0", font=("Segoe UI", 26, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD
        )
        self.lbl_tie_score.pack()

        # Computer Score Card
        c_card = tk.Frame(score_frame, bg=BG_CARD)
        c_card.grid(row=0, column=2, sticky="nsew", padx=6)
        tk.Label(c_card, text="🤖 COMPUTER", font=("Segoe UI", 10, "bold"), fg=ACCENT_RED, bg=BG_CARD).pack()
        self.lbl_computer_score = tk.Label(
            c_card, text="0", font=("Segoe UI", 26, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD
        )
        self.lbl_computer_score.pack()

        # Metrics Card (Rounds & Streak)
        m_card = tk.Frame(score_frame, bg=BG_CARD)
        m_card.grid(row=0, column=3, sticky="nsew", padx=6)
        self.lbl_round_count = tk.Label(
            m_card, text="Round: 0", font=("Segoe UI", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD
        )
        self.lbl_round_count.pack()
        self.lbl_win_rate = tk.Label(
            m_card, text="Win Rate: 0.0%", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_CARD
        )
        self.lbl_win_rate.pack()
        self.lbl_streak = tk.Label(
            m_card, text="Streak: -", font=("Segoe UI", 9, "bold"), fg=ACCENT_PURPLE, bg=BG_CARD
        )
        self.lbl_streak.pack()

    def _build_duel_arena(self) -> None:
        """Build the central visual showdown stage comparing user vs computer weapon."""
        arena_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=20, pady=20)
        arena_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 14))

        arena_frame.columnconfigure(0, weight=4)
        arena_frame.columnconfigure(1, weight=2)
        arena_frame.columnconfigure(2, weight=4)

        # Player Weapon Box
        self.p_box = tk.Frame(arena_frame, bg=BG_CARD_ALT, padx=16, pady=16, relief=tk.FLAT)
        self.p_box.grid(row=0, column=0, sticky="nsew", padx=8)

        tk.Label(
            self.p_box,
            text="YOUR PICK",
            font=("Segoe UI", 11, "bold"),
            fg=ACCENT_BLUE,
            bg=BG_CARD_ALT,
        ).pack()

        self.lbl_player_icon = tk.Label(
            self.p_box,
            text="❔",
            font=("Segoe UI Emoji", 54),
            fg=TEXT_PRIMARY,
            bg=BG_CARD_ALT,
            pady=10,
        )
        self.lbl_player_icon.pack()

        self.lbl_player_choice_name = tk.Label(
            self.p_box,
            text="Select weapon below",
            font=("Segoe UI", 11),
            fg=TEXT_MUTED,
            bg=BG_CARD_ALT,
        )
        self.lbl_player_choice_name.pack()

        # Center VS Graphic / Suspense Indicator
        vs_box = tk.Frame(arena_frame, bg=BG_CARD)
        vs_box.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            vs_box,
            text="VS",
            font=("Segoe UI", 28, "bold"),
            fg=ACCENT_AMBER,
            bg=BG_CARD,
            pady=25,
        ).pack()

        self.lbl_arena_status = tk.Label(
            vs_box,
            text="Awaiting duel",
            font=("Segoe UI", 9, "italic"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        self.lbl_arena_status.pack()

        # Computer Weapon Box
        self.c_box = tk.Frame(arena_frame, bg=BG_CARD_ALT, padx=16, pady=16, relief=tk.FLAT)
        self.c_box.grid(row=0, column=2, sticky="nsew", padx=8)

        tk.Label(
            self.c_box,
            text="COMPUTER PICK",
            font=("Segoe UI", 11, "bold"),
            fg=ACCENT_RED,
            bg=BG_CARD_ALT,
        ).pack()

        self.lbl_computer_icon = tk.Label(
            self.c_box,
            text="❔",
            font=("Segoe UI Emoji", 54),
            fg=TEXT_PRIMARY,
            bg=BG_CARD_ALT,
            pady=10,
        )
        self.lbl_computer_icon.pack()

        self.lbl_computer_choice_name = tk.Label(
            self.c_box,
            text="Waiting for your move...",
            font=("Segoe UI", 11),
            fg=TEXT_MUTED,
            bg=BG_CARD_ALT,
        )
        self.lbl_computer_choice_name.pack()

    def _build_result_banner(self) -> None:
        """Build status banner showing outcome title and explanatory text."""
        self.banner_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=16, pady=12)
        self.banner_frame.pack(fill=tk.X, pady=(0, 14))

        self.lbl_result_headline = tk.Label(
            self.banner_frame,
            text="🎯 Choose Rock, Paper, or Scissors to Begin!",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        self.lbl_result_headline.pack()

        self.lbl_result_detail = tk.Label(
            self.banner_frame,
            text="Rock beats Scissors • Scissors beats Paper • Paper beats Rock",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        self.lbl_result_detail.pack(pady=(2, 0))

    def _build_controls(self) -> None:
        """Build weapon selection buttons and action buttons."""
        controls_frame = tk.Frame(self.main_container, bg=BG_DARK)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            controls_frame,
            text="CHOOSE YOUR WEAPON",
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_MUTED,
            bg=BG_DARK,
        ).pack(anchor="w", pady=(0, 6))

        # 3 Choice Buttons
        btn_grid = tk.Frame(controls_frame, bg=BG_DARK)
        btn_grid.pack(fill=tk.X, pady=(0, 12))
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)
        btn_grid.columnconfigure(2, weight=1)

        self.btn_rock = self._create_weapon_button(
            btn_grid,
            choice=Choice.ROCK,
            column=0,
            hotkey_str="[R]",
        )
        self.btn_paper = self._create_weapon_button(
            btn_grid,
            choice=Choice.PAPER,
            column=1,
            hotkey_str="[P]",
        )
        self.btn_scissors = self._create_weapon_button(
            btn_grid,
            choice=Choice.SCISSORS,
            column=2,
            hotkey_str="[S]",
        )

        # Action Toolbar (Play Again, Match History, Reset)
        action_bar = tk.Frame(controls_frame, bg=BG_DARK)
        action_bar.pack(fill=tk.X)

        self.btn_play_again = tk.Button(
            action_bar,
            text="🔄 Play Next Round [Space]",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_BLUE,
            fg=TEXT_PRIMARY,
            activebackground="#2563eb",
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.reset_round_display,
        )
        self.btn_play_again.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_history = tk.Button(
            action_bar,
            text="📜 Match History [H]",
            font=("Segoe UI", 10),
            bg=BG_CARD_ALT,
            fg=TEXT_PRIMARY,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self._show_history,
        )
        self.btn_history.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_reset = tk.Button(
            action_bar,
            text="🗑️ Reset Scores",
            font=("Segoe UI", 10),
            bg=BG_CARD_ALT,
            fg="#f87171",
            activebackground=BG_CARD,
            activeforeground="#ef4444",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self._confirm_reset_scores,
        )
        self.btn_reset.pack(side=tk.RIGHT)

    def _create_weapon_button(
        self,
        parent: tk.Widget,
        choice: Choice,
        column: int,
        hotkey_str: str,
    ) -> tk.Button:
        """Helper to generate styled, responsive weapon choice button."""
        btn_text = f"{choice.emoji}  {choice.value.upper()}\n{hotkey_str}"
        btn = tk.Button(
            parent,
            text=btn_text,
            font=("Segoe UI", 12, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            activebackground=BG_CARD_ALT,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=12,
            cursor="hand2",
            command=lambda c=choice: self.handle_player_selection(c),
        )
        btn.grid(row=0, column=column, padx=6, sticky="nsew")

        # Visual Hover Effects
        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=BG_CARD_ALT))
        btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=BG_CARD))
        return btn

    def _build_footer(self) -> None:
        """Build footer with asset attribution and version tag."""
        footer_frame = tk.Frame(self.main_container, bg=BG_DARK)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 0))

        lbl_attr = tk.Label(
            footer_frame,
            text=f"Production Python GUI • CodSoft Task 3 • Asset ID: {ASSET_ID}",
            font=("Segoe UI", 8),
            fg=TEXT_MUTED,
            bg=BG_DARK,
        )
        lbl_attr.pack(side=tk.LEFT)

        lbl_hint = tk.Label(
            footer_frame,
            text="Press R, P, or S on keyboard to throw",
            font=("Segoe UI", 8, "italic"),
            fg=TEXT_MUTED,
            bg=BG_DARK,
        )
        lbl_hint.pack(side=tk.RIGHT)

    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts to gameplay triggers."""
        self.root.bind("<r>", lambda e: self.handle_player_selection(Choice.ROCK))
        self.root.bind("<R>", lambda e: self.handle_player_selection(Choice.ROCK))
        self.root.bind("<p>", lambda e: self.handle_player_selection(Choice.PAPER))
        self.root.bind("<P>", lambda e: self.handle_player_selection(Choice.PAPER))
        self.root.bind("<s>", lambda e: self.handle_player_selection(Choice.SCISSORS))
        self.root.bind("<S>", lambda e: self.handle_player_selection(Choice.SCISSORS))
        self.root.bind("<space>", lambda e: self.reset_round_display())
        self.root.bind("<h>", lambda e: self._show_history())
        self.root.bind("<H>", lambda e: self._show_history())
        self.root.bind("<Control-r>", lambda e: self._confirm_reset_scores())

    def handle_player_selection(self, user_choice: Choice) -> None:
        """
        Process the player's weapon choice, run visual suspense animation,
        and update the engine and UI state.
        """
        if self._is_animating:
            return  # Prevent multi-clicks during roll animation

        # Show player's choice immediately
        self.lbl_player_icon.configure(text=user_choice.emoji)
        self.lbl_player_choice_name.configure(text=f"Selected: {user_choice.value}")

        # Start brief computer suspense roll animation
        self._is_animating = True
        self._set_buttons_state(tk.DISABLED)
        self.lbl_arena_status.configure(text="Computer calculating...")

        icons = ["🪨", "📄", "✂️"]
        cycles = 6
        delay_ms = 60

        def _step(remaining: int) -> None:
            if remaining > 0:
                self.lbl_computer_icon.configure(text=icons[remaining % 3])
                self.lbl_computer_choice_name.configure(text="Choosing...")
                self.root.after(delay_ms, lambda: _step(remaining - 1))
            else:
                self._finish_round_execution(user_choice)

        _step(cycles)

    def _finish_round_execution(self, user_choice: Choice) -> None:
        """Resolve round after animation concludes."""
        self._is_animating = False
        self._set_buttons_state(tk.NORMAL)

        # Execute in GameEngine
        record = self.engine.play_round(user_choice)

        # Update Computer Duel Box
        self.lbl_computer_icon.configure(text=record.computer_choice.emoji)
        self.lbl_computer_choice_name.configure(text=f"Selected: {record.computer_choice.value}")
        self.lbl_arena_status.configure(text=f"Round #{record.round_number}")

        # Highlight Results
        self._apply_result_styling(record)
        self._refresh_scoreboard()

        # Check for Match Series completion in Best of 3 / 5
        series_result = self.engine.check_match_winner()
        if series_result:
            title, desc = series_result
            messagebox.showinfo(
                f"🏆 Series Complete: {title}",
                f"{desc}\n\nFinal Score: Player {self.engine.user_score} - {self.engine.computer_score} Computer",
                parent=self.root,
            )

    def _apply_result_styling(self, record: RoundRecord) -> None:
        """Apply color themes and headline text matching the round outcome."""
        result = record.result
        if result == GameResult.WIN:
            headline = f"🎉 YOU WIN! ({record.user_choice.value} beats {record.computer_choice.value})"
            banner_bg = "#064e3b"   # Dark green
            headline_fg = "#34d399"
        elif result == GameResult.LOSS:
            headline = f"🤖 COMPUTER WINS! ({record.computer_choice.value} beats {record.user_choice.value})"
            banner_bg = "#4c0519"   # Dark red
            headline_fg = "#f87171"
        else:
            headline = f"🤝 IT'S A TIE! (Both picked {record.user_choice.value})"
            banner_bg = "#451a03"   # Dark amber
            headline_fg = "#fbbf24"

        self.banner_frame.configure(bg=banner_bg)
        self.lbl_result_headline.configure(text=headline, bg=banner_bg, fg=headline_fg)
        self.lbl_result_detail.configure(text=record.explanation, bg=banner_bg, fg=TEXT_PRIMARY)

    def _refresh_scoreboard(self) -> None:
        """Synchronize UI scoreboard numbers with GameEngine state."""
        self.lbl_player_score.configure(text=str(self.engine.user_score))
        self.lbl_computer_score.configure(text=str(self.engine.computer_score))
        self.lbl_tie_score.configure(text=str(self.engine.tie_score))
        self.lbl_round_count.configure(text=f"Rounds: {self.engine.total_rounds}")
        self.lbl_win_rate.configure(text=f"Win Rate: {self.engine.user_win_rate}%")

        streak = self.engine.current_streak
        if streak > 0:
            streak_text = f"🔥 {streak} Win{'s' if streak > 1 else ''}"
            streak_color = "#f97316"
        elif streak < 0:
            streak_text = f"❄️ {abs(streak)} Loss{'es' if abs(streak) > 1 else ''}"
            streak_color = "#38bdf8"
        else:
            streak_text = "Streak: 0"
            streak_color = TEXT_MUTED

        self.lbl_streak.configure(text=streak_text, fg=streak_color)

    def reset_round_display(self) -> None:
        """Prepare the arena for the next round without resetting overall score stats."""
        if self._is_animating:
            return

        self.lbl_player_icon.configure(text="❔")
        self.lbl_player_choice_name.configure(text="Select weapon below")
        self.lbl_computer_icon.configure(text="❔")
        self.lbl_computer_choice_name.configure(text="Waiting for your move...")
        self.lbl_arena_status.configure(text="Ready for Next Round")

        self.banner_frame.configure(bg=BG_CARD)
        self.lbl_result_headline.configure(
            text="🎯 Choose Rock, Paper, or Scissors to Play!",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
        )
        self.lbl_result_detail.configure(
            text="Rock beats Scissors • Scissors beats Paper • Paper beats Rock",
            bg=BG_CARD,
            fg=TEXT_MUTED,
        )

    def _confirm_reset_scores(self) -> None:
        """Prompt confirmation before clearing scores and history."""
        if self.engine.total_rounds == 0:
            return

        confirmed = messagebox.askyesno(
            "Reset Scores",
            "Are you sure you want to reset all scores, streaks, and match history?",
            parent=self.root,
        )
        if confirmed:
            self.engine.reset_scores()
            self._refresh_scoreboard()
            self.reset_round_display()

    def _on_mode_change(self, event: Optional[tk.Event] = None) -> None:
        """Handle game mode selection change."""
        selected_val = self.mode_var.get()
        for mode in GameMode:
            if mode.value == selected_val:
                self.engine.set_mode(mode)
                self._refresh_scoreboard()
                self.reset_round_display()
                break

    def _set_buttons_state(self, state: str) -> None:
        """Enable or disable choice buttons."""
        self.btn_rock.configure(state=state)
        self.btn_paper.configure(state=state)
        self.btn_scissors.configure(state=state)

    def _show_history(self) -> None:
        """Open the match history modal dialog."""
        HistoryDialog(self.root, self.engine)

    def _show_rules(self) -> None:
        """Open the game rules modal dialog."""
        RulesDialog(self.root)
