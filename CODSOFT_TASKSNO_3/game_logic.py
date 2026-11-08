"""
Rock-Paper-Scissors Game - Core Game Logic & Domain Engine.

This module provides the pure domain logic, rules, statistics tracking,
and data models for the Rock-Paper-Scissors game, independent of any UI framework.
Adheres strictly to PEP-8 and includes comprehensive type annotations.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Choice(Enum):
    """Enumeration representing valid choices in Rock-Paper-Scissors."""
    ROCK = "Rock"
    PAPER = "Paper"
    SCISSORS = "Scissors"

    @property
    def emoji(self) -> str:
        """Return a visual emoji representation for the choice."""
        mapping = {
            Choice.ROCK: "🪨",
            Choice.PAPER: "📄",
            Choice.SCISSORS: "✂️",
        }
        return mapping[self]

    @property
    def defeats(self) -> Choice:
        """Return the choice that this choice defeats."""
        mapping = {
            Choice.ROCK: Choice.SCISSORS,
            Choice.PAPER: Choice.ROCK,
            Choice.SCISSORS: Choice.PAPER,
        }
        return mapping[self]

    @property
    def action_verb(self) -> str:
        """Return a descriptive action verb when this choice defeats another."""
        mapping = {
            Choice.ROCK: "crushes",
            Choice.PAPER: "covers",
            Choice.SCISSORS: "cuts",
        }
        return mapping[self]

    @classmethod
    def from_string(cls, value: str) -> Optional[Choice]:
        """Convert a string representation to a Choice enum member."""
        cleaned = value.strip().upper()
        for choice in cls:
            if choice.name == cleaned or choice.value.upper() == cleaned:
                return choice
        return None


class GameResult(Enum):
    """Enumeration representing the outcome of a round from user's perspective."""
    WIN = "Win"
    LOSS = "Loss"
    TIE = "Tie"

    @property
    def display_text(self) -> str:
        """Human-readable display text."""
        mapping = {
            GameResult.WIN: "You Win!",
            GameResult.LOSS: "Computer Wins!",
            GameResult.TIE: "It's a Tie!",
        }
        return mapping[self]

    @property
    def badge_symbol(self) -> str:
        """Symbol or emoji for score cards and banners."""
        mapping = {
            GameResult.WIN: "🎉",
            GameResult.LOSS: "🤖",
            GameResult.TIE: "🤝",
        }
        return mapping[self]


class GameMode(Enum):
    """Match mode structure."""
    CASUAL = "Endless Casual"
    BEST_OF_3 = "Best of 3 (First to 2)"
    BEST_OF_5 = "Best of 5 (First to 3)"

    @property
    def target_wins(self) -> Optional[int]:
        """Required wins to clinch a match series."""
        mapping = {
            GameMode.CASUAL: None,
            GameMode.BEST_OF_3: 2,
            GameMode.BEST_OF_5: 3,
        }
        return mapping[self]


@dataclass(frozen=True)
class RoundRecord:
    """Immutable record of a completed game round."""
    round_number: int
    user_choice: Choice
    computer_choice: Choice
    result: GameResult
    explanation: str
    timestamp: datetime = field(default_factory=datetime.now)


class GameEngine:
    """
    Core game engine managing state, rule evaluation, score calculation,
    and history tracking.
    """

    def __init__(self, mode: GameMode = GameMode.CASUAL) -> None:
        """Initialize the game engine with standard scores and default mode."""
        self.mode = mode
        self.user_score: int = 0
        self.computer_score: int = 0
        self.tie_score: int = 0
        self.current_streak: int = 0
        self.best_streak: int = 0
        self.history: List[RoundRecord] = []

    @property
    def total_rounds(self) -> int:
        """Return total rounds played in this session."""
        return len(self.history)

    @property
    def user_win_rate(self) -> float:
        """Return user win rate as a percentage [0.0 - 100.0]."""
        if self.total_rounds == 0:
            return 0.0
        return round((self.user_score / self.total_rounds) * 100, 1)

    @staticmethod
    def evaluate_round(user_choice: Choice, computer_choice: Choice) -> Tuple[GameResult, str]:
        """
        Evaluate the outcome between two choices according to official RPS rules.

        Rules:
            - Rock beats Scissors ("Rock crushes Scissors")
            - Scissors beats Paper ("Scissors cuts Paper")
            - Paper beats Rock ("Paper covers Rock")
            - Identical choices result in a Tie

        Args:
            user_choice: The Choice selected by the user.
            computer_choice: The Choice selected by the computer.

        Returns:
            A tuple of (GameResult, explanation_string).
        """
        if user_choice == computer_choice:
            return (
                GameResult.TIE,
                f"Both chose {user_choice.value}! It's a standoff.",
            )

        if user_choice.defeats == computer_choice:
            return (
                GameResult.WIN,
                f"{user_choice.value} {user_choice.action_verb} {computer_choice.value}! You score a point.",
            )

        return (
            GameResult.LOSS,
            f"{computer_choice.value} {computer_choice.action_verb} {user_choice.value}! Computer scores.",
        )

    def play_round(
        self,
        user_choice: Choice,
        fixed_computer_choice: Optional[Choice] = None,
    ) -> RoundRecord:
        """
        Execute a single game round.

        Args:
            user_choice: The choice submitted by the user.
            fixed_computer_choice: Optional predetermined choice for testing.
                                   If None, randomly selected from Choice.

        Returns:
            RoundRecord containing all data for the executed round.
        """
        if fixed_computer_choice is not None:
            computer_choice = fixed_computer_choice
        else:
            computer_choice = random.choice(list(Choice))

        result, explanation = self.evaluate_round(user_choice, computer_choice)

        # Update scoring metrics
        if result == GameResult.WIN:
            self.user_score += 1
            if self.current_streak >= 0:
                self.current_streak += 1
            else:
                self.current_streak = 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        elif result == GameResult.LOSS:
            self.computer_score += 1
            if self.current_streak <= 0:
                self.current_streak -= 1
            else:
                self.current_streak = -1
        else:
            self.tie_score += 1
            # Ties do not break positive winning streaks, or can maintain them

        record = RoundRecord(
            round_number=self.total_rounds + 1,
            user_choice=user_choice,
            computer_choice=computer_choice,
            result=result,
            explanation=explanation,
        )
        self.history.append(record)
        return record

    def check_match_winner(self) -> Optional[Tuple[str, str]]:
        """
        Check if current match mode has concluded.

        Returns:
            Tuple of (winner_title, description) if concluded, otherwise None.
        """
        target = self.mode.target_wins
        if target is None:
            return None

        if self.user_score >= target:
            return ("Victory!", f"You reached {target} wins and conquered the match!")
        if self.computer_score >= target:
            return ("Defeat!", f"Computer reached {target} wins and won the match.")
        return None

    def reset_scores(self) -> None:
        """Reset all round records, streaks, and scores to start fresh."""
        self.user_score = 0
        self.computer_score = 0
        self.tie_score = 0
        self.current_streak = 0
        self.best_streak = 0
        self.history.clear()

    def set_mode(self, new_mode: GameMode) -> None:
        """Change the game mode and reset scores for a new series."""
        self.mode = new_mode
        self.reset_scores()

    def get_summary_dict(self) -> Dict[str, object]:
        """Export current statistics summary dictionary."""
        return {
            "mode": self.mode.value,
            "total_rounds": self.total_rounds,
            "user_score": self.user_score,
            "computer_score": self.computer_score,
            "tie_score": self.tie_score,
            "win_rate": f"{self.user_win_rate}%",
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
        }
