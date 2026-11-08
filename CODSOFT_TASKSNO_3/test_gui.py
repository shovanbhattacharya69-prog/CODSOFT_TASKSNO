"""
Automated smoke test for the Tkinter Graphical User Interface.
Verifies instantiation, widget hierarchy, round execution, and score reset.
"""

import unittest
import tkinter as tk
from game_logic import Choice, GameMode, GameResult
from gui import RockPaperScissorsGUI


class TestGUIIntegration(unittest.TestCase):
    """Test case for Tkinter GUI components and handlers."""

    def setUp(self) -> None:
        """Create root window and instantiate app."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during automated test
        self.app = RockPaperScissorsGUI(self.root)
        self.root.update()

    def tearDown(self) -> None:
        """Destroy root window."""
        self.root.destroy()

    def test_gui_initial_state(self) -> None:
        """Verify initial UI labels and scoreboard values."""
        self.assertEqual(self.app.lbl_player_score.cget("text"), "0")
        self.assertEqual(self.app.lbl_computer_score.cget("text"), "0")
        self.assertEqual(self.app.lbl_tie_score.cget("text"), "0")
        self.assertEqual(self.app.lbl_round_count.cget("text"), "Rounds: 0")

    def test_gui_finish_round_execution(self) -> None:
        """Simulate round completion and check UI updates."""
        self.app._finish_round_execution(Choice.ROCK)
        self.root.update()

        # Engine should have 1 round in history
        self.assertEqual(self.app.engine.total_rounds, 1)
        self.assertIn("Round #1", self.app.lbl_arena_status.cget("text"))
        self.assertNotEqual(self.app.lbl_computer_icon.cget("text"), "❔")

    def test_reset_round_display(self) -> None:
        """Verify reset_round_display clears choices back to ready state."""
        self.app._finish_round_execution(Choice.PAPER)
        self.app.reset_round_display()
        self.root.update()

        self.assertEqual(self.app.lbl_player_icon.cget("text"), "❔")
        self.assertEqual(self.app.lbl_computer_icon.cget("text"), "❔")
        self.assertEqual(self.app.lbl_arena_status.cget("text"), "Ready for Next Round")


if __name__ == "__main__":
    unittest.main()
