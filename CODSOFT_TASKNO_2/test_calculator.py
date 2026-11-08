"""
Unit Tests for SafeEvaluator and CalculatorEngine
=================================================
Validates correctness, edge cases, error handling, and safe evaluation.
"""

import unittest
from main import SafeEvaluator, CalculatorEngine


class TestSafeEvaluator(unittest.TestCase):
    """Test AST-based safe evaluation of arithmetic expressions."""

    def test_basic_arithmetic(self):
        self.assertEqual(SafeEvaluator.evaluate("10 + 5"), 15)
        self.assertEqual(SafeEvaluator.evaluate("20 - 7"), 13)
        self.assertEqual(SafeEvaluator.evaluate("6 * 8"), 48)
        self.assertEqual(SafeEvaluator.evaluate("24 / 4"), 6.0)

    def test_unicode_operator_symbols(self):
        self.assertEqual(SafeEvaluator.evaluate("15 × 3"), 45)
        self.assertEqual(SafeEvaluator.evaluate("100 ÷ 5"), 20.0)
        self.assertEqual(SafeEvaluator.evaluate("50 − 18"), 32)

    def test_operator_precedence(self):
        self.assertEqual(SafeEvaluator.evaluate("2 + 3 * 4"), 14)
        self.assertEqual(SafeEvaluator.evaluate("10 - 8 / 2"), 6.0)

    def test_decimals(self):
        self.assertAlmostEqual(SafeEvaluator.evaluate("0.1 + 0.2"), 0.3, places=5)
        self.assertEqual(SafeEvaluator.evaluate("2.5 * 4"), 10.0)

    def test_zero_division(self):
        with self.assertRaises(ZeroDivisionError):
            SafeEvaluator.evaluate("42 / 0")
        with self.assertRaises(ZeroDivisionError):
            SafeEvaluator.evaluate("10 ÷ 0")

    def test_security_disallowed_expressions(self):
        # Code injection attempts must fail
        with self.assertRaises(ValueError):
            SafeEvaluator.evaluate("__import__('os').system('dir')")
        with self.assertRaises(ValueError):
            SafeEvaluator.evaluate("open('main.py').read()")
        with self.assertRaises(ValueError):
            SafeEvaluator.evaluate("len([1, 2, 3])")


class TestCalculatorEngine(unittest.TestCase):
    """Test calculator state machine and user interaction flows."""

    def setUp(self):
        self.engine = CalculatorEngine()

    def test_digit_entry(self):
        self.engine.input_digit("5")
        self.engine.input_digit("2")
        self.assertEqual(self.engine.current_operand, "52")

    def test_leading_zeroes(self):
        self.engine.input_digit("0")
        self.engine.input_digit("0")
        self.assertEqual(self.engine.current_operand, "0")
        self.engine.input_digit("7")
        self.assertEqual(self.engine.current_operand, "7")

    def test_decimal_entry(self):
        self.engine.input_digit("3")
        self.engine.input_decimal()
        self.engine.input_digit("1")
        self.engine.input_decimal()  # Second decimal should be ignored
        self.engine.input_digit("4")
        self.assertEqual(self.engine.current_operand, "3.14")

    def test_backspace(self):
        self.engine.input_digit("9")
        self.engine.input_digit("8")
        self.engine.input_digit("7")
        self.engine.backspace()
        self.assertEqual(self.engine.current_operand, "98")
        self.engine.backspace()
        self.engine.backspace()
        self.assertEqual(self.engine.current_operand, "0")

    def test_toggle_sign(self):
        self.engine.input_digit("1")
        self.engine.input_digit("5")
        self.engine.toggle_sign()
        self.assertEqual(self.engine.current_operand, "-15")
        self.engine.toggle_sign()
        self.assertEqual(self.engine.current_operand, "15")

    def test_apply_percent(self):
        self.engine.input_digit("5")
        self.engine.input_digit("0")
        self.engine.apply_percent()
        self.assertEqual(self.engine.current_operand, "0.5")

    def test_basic_calculation_workflow(self):
        # 12 + 8 = 20
        self.engine.input_digit("1")
        self.engine.input_digit("2")
        self.engine.input_operator("+")
        self.engine.input_digit("8")
        self.engine.calculate()
        self.assertEqual(self.engine.current_operand, "20")
        self.assertEqual(self.engine.expression_history, "12 + 8 =")

    def test_operator_replacement(self):
        # User presses + then changes mind to ×
        self.engine.input_digit("5")
        self.engine.input_operator("+")
        self.engine.input_operator("×")
        self.engine.input_digit("4")
        self.engine.calculate()
        self.assertEqual(self.engine.current_operand, "20")

    def test_zero_division_handling(self):
        self.engine.input_digit("9")
        self.engine.input_operator("÷")
        self.engine.input_digit("0")
        self.engine.calculate()
        self.assertTrue(self.engine.is_error_state)
        self.assertEqual(self.engine.current_operand, "Cannot divide by zero")

        # Typing a digit after error should reset cleanly
        self.engine.input_digit("4")
        self.assertFalse(self.engine.is_error_state)
        self.assertEqual(self.engine.current_operand, "4")

    def test_clear_and_reset(self):
        self.engine.input_digit("4")
        self.engine.input_operator("+")
        self.engine.input_digit("2")
        self.engine.reset()
        self.assertEqual(self.engine.current_operand, "0")
        self.assertEqual(self.engine.expression_history, "")
        self.assertFalse(self.engine.is_error_state)


if __name__ == "__main__":
    unittest.main()
