"""
Rock-Paper-Scissors Game - Application Entry Point.

Production-grade application launcher providing GUI launch via Tkinter,
with command-line argument parsing and optional CLI fallback mode.
Adheres to PEP-8 standards.
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from typing import NoReturn

from game_logic import Choice, GameEngine, GameMode, GameResult
from gui import ASSET_ID, RockPaperScissorsGUI

APP_NAME = "Rock-Paper-Scissors Professional Edition"
VERSION = "1.0.0"


def run_gui() -> None:
    """Initialize and launch the Tkinter graphical interface."""
    root = tk.Tk()
    app = RockPaperScissorsGUI(root)
    root.mainloop()


def run_cli() -> None:
    """Run an interactive terminal-based fallback version of the game."""
    # Ensure standard streams handle UTF-8 symbols gracefully on Windows consoles
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 60)
    print(f" {APP_NAME} - Terminal Mode")
    print(f" Asset Reference ID: {ASSET_ID}")
    print("=" * 60)
    print("Rules: Rock crushes Scissors, Scissors cuts Paper, Paper covers Rock.")
    print("Type 'r' for Rock, 'p' for Paper, 's' for Scissors, or 'q' to quit.\n")

    engine = GameEngine(mode=GameMode.CASUAL)

    choice_map = {
        "r": Choice.ROCK,
        "rock": Choice.ROCK,
        "p": Choice.PAPER,
        "paper": Choice.PAPER,
        "s": Choice.SCISSORS,
        "scissors": Choice.SCISSORS,
    }

    while True:
        try:
            user_input = input("Choose (r/p/s or q to quit): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input in ("q", "quit", "exit"):
            break

        if user_input not in choice_map:
            print("Invalid choice! Please enter 'r', 'p', or 's'.")
            continue

        player_choice = choice_map[user_input]
        record = engine.play_round(player_choice)

        print("-" * 50)
        print(f"You picked     : {record.user_choice.emoji} {record.user_choice.value}")
        print(f"Computer picked: {record.computer_choice.emoji} {record.computer_choice.value}")
        print(f"Outcome        : {record.result.badge_symbol} {record.result.display_text}")
        print(f"Details        : {record.explanation}")
        print(
            f"Scoreboard     : You: {engine.user_score} | Computer: {engine.computer_score} "
            f"| Ties: {engine.tie_score} | Win Rate: {engine.user_win_rate}%"
        )
        print("-" * 50 + "\n")

    print("\nFinal Session Statistics:")
    print(f"• Total Rounds Played : {engine.total_rounds}")
    print(f"• Your Wins           : {engine.user_score}")
    print(f"• Computer Wins       : {engine.computer_score}")
    print(f"• Ties                : {engine.tie_score}")
    print(f"• Win Rate            : {engine.user_win_rate}%")
    print(f"• Best Win Streak     : {engine.best_streak}")
    print("Thank you for playing!\n")


def main() -> None:
    """Parse CLI arguments and launch the appropriate mode."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - A polished, production-ready Rock-Paper-Scissors game."
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in command-line interface (headless / terminal) mode.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} v{VERSION} (Asset ID: {ASSET_ID})",
    )

    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        try:
            run_gui()
        except tk.TclError as exc:
            print(
                f"[WARNING] Could not initialize graphical display: {exc}",
                file=sys.stderr,
            )
            print("Falling back to CLI interactive mode...\n", file=sys.stderr)
            run_cli()


if __name__ == "__main__":
    main()
