"""
Unit tests for the Rock-Paper-Scissors Game Logic.
"""

import unittest
from game_logic import Choice, GameEngine, GameMode, GameResult


class TestGameLogic(unittest.TestCase):
    """Test suite for Choice rules, GameEngine evaluation, and statistics."""

    def test_choice_defeats_rules(self) -> None:
        """Verify the standard rules of Rock-Paper-Scissors."""
        # Rock beats Scissors
        self.assertEqual(Choice.ROCK.defeats, Choice.SCISSORS)
        # Scissors beats Paper
        self.assertEqual(Choice.SCISSORS.defeats, Choice.PAPER)
        # Paper beats Rock
        self.assertEqual(Choice.PAPER.defeats, Choice.ROCK)

    def test_evaluate_round_outcomes(self) -> None:
        """Verify evaluation of all 9 possible combinations."""
        # Wins
        self.assertEqual(GameEngine.evaluate_round(Choice.ROCK, Choice.SCISSORS)[0], GameResult.WIN)
        self.assertEqual(GameEngine.evaluate_round(Choice.SCISSORS, Choice.PAPER)[0], GameResult.WIN)
        self.assertEqual(GameEngine.evaluate_round(Choice.PAPER, Choice.ROCK)[0], GameResult.WIN)

        # Losses
        self.assertEqual(GameEngine.evaluate_round(Choice.SCISSORS, Choice.ROCK)[0], GameResult.LOSS)
        self.assertEqual(GameEngine.evaluate_round(Choice.PAPER, Choice.SCISSORS)[0], GameResult.LOSS)
        self.assertEqual(GameEngine.evaluate_round(Choice.ROCK, Choice.PAPER)[0], GameResult.LOSS)

        # Ties
        self.assertEqual(GameEngine.evaluate_round(Choice.ROCK, Choice.ROCK)[0], GameResult.TIE)
        self.assertEqual(GameEngine.evaluate_round(Choice.PAPER, Choice.PAPER)[0], GameResult.TIE)
        self.assertEqual(GameEngine.evaluate_round(Choice.SCISSORS, Choice.SCISSORS)[0], GameResult.TIE)

    def test_game_engine_scoring_and_streaks(self) -> None:
        """Verify score accumulation, streaks, and history records."""
        engine = GameEngine()
        self.assertEqual(engine.user_score, 0)
        self.assertEqual(engine.computer_score, 0)
        self.assertEqual(engine.tie_score, 0)

        # Round 1: Win
        rec1 = engine.play_round(Choice.ROCK, fixed_computer_choice=Choice.SCISSORS)
        self.assertEqual(rec1.result, GameResult.WIN)
        self.assertEqual(engine.user_score, 1)
        self.assertEqual(engine.computer_score, 0)
        self.assertEqual(engine.current_streak, 1)
        self.assertEqual(engine.best_streak, 1)

        # Round 2: Another Win
        rec2 = engine.play_round(Choice.PAPER, fixed_computer_choice=Choice.ROCK)
        self.assertEqual(rec2.result, GameResult.WIN)
        self.assertEqual(engine.user_score, 2)
        self.assertEqual(engine.current_streak, 2)
        self.assertEqual(engine.best_streak, 2)

        # Round 3: Tie
        rec3 = engine.play_round(Choice.PAPER, fixed_computer_choice=Choice.PAPER)
        self.assertEqual(rec3.result, GameResult.TIE)
        self.assertEqual(engine.tie_score, 1)

        # Round 4: Loss
        rec4 = engine.play_round(Choice.ROCK, fixed_computer_choice=Choice.PAPER)
        self.assertEqual(rec4.result, GameResult.LOSS)
        self.assertEqual(engine.computer_score, 1)
        self.assertEqual(engine.current_streak, -1)
        self.assertEqual(engine.best_streak, 2)
        self.assertEqual(engine.total_rounds, 4)
        self.assertEqual(engine.user_win_rate, 50.0)

    def test_match_winner_series(self) -> None:
        """Verify Best of 3 mode victory triggers."""
        engine = GameEngine(mode=GameMode.BEST_OF_3)
        self.assertIsNone(engine.check_match_winner())

        engine.play_round(Choice.ROCK, fixed_computer_choice=Choice.SCISSORS)
        self.assertIsNone(engine.check_match_winner())

        engine.play_round(Choice.PAPER, fixed_computer_choice=Choice.ROCK)
        winner = engine.check_match_winner()
        self.assertIsNotNone(winner)
        self.assertEqual(winner[0], "Victory!")

    def test_reset_scores(self) -> None:
        """Verify reset functionality restores blank state."""
        engine = GameEngine()
        engine.play_round(Choice.ROCK, fixed_computer_choice=Choice.SCISSORS)
        self.assertEqual(engine.user_score, 1)
        engine.reset_scores()
        self.assertEqual(engine.user_score, 0)
        self.assertEqual(engine.total_rounds, 0)
        self.assertEqual(len(engine.history), 0)


if __name__ == "__main__":
    unittest.main()
