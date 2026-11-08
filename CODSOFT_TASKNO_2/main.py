"""
Production-Ready GUI Calculator Application
===========================================
Task 2 - CodSoft Internship Pipeline

A desktop calculator built with Python and Tkinter featuring a modern,
responsive grid layout, keyboard bindings, and safe expression evaluation
via Abstract Syntax Tree (AST) parsing.

Author: Senior Python Developer
License: MIT
"""

import ast
import operator
import sys
import tkinter as tk
from typing import Any, Callable, Dict, Union


# ============================================================================
# Core Logic: Safe AST Evaluator & Calculator Engine
# ============================================================================

class SafeEvaluator:
    """
    Safely parses and evaluates mathematical expressions using Python's AST.
    Prevents code execution vulnerabilities associated with standard eval().
    """

    # Supported binary operators
    _BINARY_OPS: Dict[type, Callable[[Any, Any], Any]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    # Supported unary operators
    _UNARY_OPS: Dict[type, Callable[[Any], Any]] = {
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def evaluate(cls, expression: str) -> Union[int, float]:
        """
        Parse and evaluate an arithmetic expression string.

        Args:
            expression: String representing a math expression (e.g., '12 + 4 * 2').

        Returns:
            The evaluated integer or float result.

        Raises:
            ZeroDivisionError: When attempting to divide by zero.
            ValueError: On invalid syntax or unauthorized node types.
            OverflowError: When result exceeds floating-point bounds.
        """
        # Normalize multiplication and division display symbols
        sanitized = (
            expression.replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .strip()
        )

        if not sanitized:
            return 0

        try:
            tree = ast.parse(sanitized, mode="eval")
        except SyntaxError as exc:
            raise ValueError("Malformed expression syntax") from exc

        return cls._eval_node(tree.body)

    @classmethod
    def _eval_node(cls, node: ast.AST) -> Union[int, float]:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in cls._BINARY_OPS:
                raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)

            if op_type == ast.Div and right == 0:
                raise ZeroDivisionError("Division by zero")

            op_func = cls._BINARY_OPS[op_type]
            return op_func(left, right)

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in cls._UNARY_OPS:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

            operand = cls._eval_node(node.operand)
            return cls._UNARY_OPS[op_type](operand)

        raise ValueError(f"Disallowed expression node: {type(node).__name__}")


class CalculatorEngine:
    """
    Manages calculation state, inputs, formatting, and operations.
    """

    MAX_DISPLAY_LENGTH = 16

    def __init__(self) -> None:
        self.current_operand: str = "0"
        self.expression_history: str = ""
        self.is_new_operand: bool = True
        self.is_error_state: bool = False

    def reset(self) -> None:
        """Reset calculator state to initial defaults."""
        self.current_operand = "0"
        self.expression_history = ""
        self.is_new_operand = True
        self.is_error_state = False

    def clear_entry(self) -> None:
        """Clear the current operand without clearing entire history."""
        if self.is_error_state:
            self.reset()
            return
        self.current_operand = "0"
        self.is_new_operand = True

    def input_digit(self, digit: str) -> None:
        """
        Append a numeric digit (0-9) to current operand.
        """
        if self.is_error_state or self.is_new_operand:
            self.current_operand = digit
            self.is_new_operand = False
            self.is_error_state = False
            return

        # Avoid redundant leading zeroes
        if self.current_operand == "0":
            self.current_operand = digit
        elif len(self.current_operand) < self.MAX_DISPLAY_LENGTH:
            self.current_operand += digit

    def input_decimal(self) -> None:
        """Add a decimal point to current operand if not already present."""
        if self.is_error_state or self.is_new_operand:
            self.current_operand = "0."
            self.is_new_operand = False
            self.is_error_state = False
            return

        if "." not in self.current_operand:
            self.current_operand += "."

    def backspace(self) -> None:
        """Remove the last entered character from the current operand."""
        if self.is_error_state or self.is_new_operand:
            return

        if len(self.current_operand) > 1:
            self.current_operand = self.current_operand[:-1]
            if self.current_operand == "-":
                self.current_operand = "0"
                self.is_new_operand = True
        else:
            self.current_operand = "0"
            self.is_new_operand = True

    def toggle_sign(self) -> None:
        """Negate the current operand."""
        if self.is_error_state or self.current_operand == "0":
            return

        if self.current_operand.startswith("-"):
            self.current_operand = self.current_operand[1:]
        else:
            self.current_operand = "-" + self.current_operand

    def apply_percent(self) -> None:
        """Convert current operand into a percentage (divide by 100)."""
        if self.is_error_state:
            return

        try:
            val = float(self.current_operand) / 100.0
            self.current_operand = self._format_number(val)
            self.is_new_operand = True
        except (ValueError, OverflowError):
            self.set_error("Error")

    def input_operator(self, op: str) -> None:
        """
        Register a binary operator (+, −, ×, ÷).
        """
        if self.is_error_state:
            return

        op_symbol = op.replace("*", "×").replace("/", "÷").replace("-", "−")

        # If user presses operator consecutively without entering a new number
        if self.is_new_operand and self.expression_history:
            # Replace the trailing operator
            tokens = self.expression_history.strip().split()
            if tokens and tokens[-1] in ("+", "−", "×", "÷"):
                tokens[-1] = op_symbol
                self.expression_history = " ".join(tokens) + " "
                return

        # Append operand and operator to history
        self.expression_history += f"{self.current_operand} {op_symbol} "
        self.is_new_operand = True

    def calculate(self) -> None:
        """Evaluate the full expression and display the final result."""
        if self.is_error_state or not self.expression_history:
            return

        full_expr = f"{self.expression_history}{self.current_operand}"

        try:
            result = SafeEvaluator.evaluate(full_expr)
            formatted = self._format_number(result)
            self.expression_history = f"{full_expr} ="
            self.current_operand = formatted
            self.is_new_operand = True
        except ZeroDivisionError:
            self.set_error("Cannot divide by zero")
        except OverflowError:
            self.set_error("Overflow")
        except (ValueError, Exception):
            self.set_error("Invalid Format")

    def set_error(self, message: str) -> None:
        """Place calculator in error state with informative display text."""
        self.current_operand = message
        self.expression_history = ""
        self.is_error_state = True
        self.is_new_operand = True

    @staticmethod
    def _format_number(val: Union[int, float]) -> str:
        """Format numbers cleanly, eliminating redundant trailing zeros."""
        if isinstance(val, float) and val.is_integer():
            val = int(val)

        if isinstance(val, int):
            return str(val)

        # Handle floating precision cleanly
        rounded = round(val, 10)
        formatted = f"{rounded:.10f}".rstrip("0").rstrip(".")
        return formatted


# ============================================================================
# Presentation Layer: Modern Responsive Tkinter GUI
# ============================================================================

class CalculatorApp(tk.Tk):
    """
    Modern Desktop GUI for the Calculator application.
    Implements a responsive grid, dark UI aesthetic, and full keyboard control.
    """

    # Modern Dark Theme Color Palette
    COLOR_BG = "#181820"
    COLOR_DISPLAY_BG = "#21222d"
    COLOR_TEXT_PRIMARY = "#ffffff"
    COLOR_TEXT_MUTED = "#9ba1b0"
    COLOR_BTN_NUM = "#282a36"
    COLOR_BTN_NUM_HOVER = "#363847"
    COLOR_BTN_FUNC = "#323544"
    COLOR_BTN_FUNC_HOVER = "#42465a"
    COLOR_BTN_ACCENT = "#ff9f0a"
    COLOR_BTN_ACCENT_HOVER = "#ffb038"
    COLOR_BTN_EQUALS = "#22c55e"
    COLOR_BTN_EQUALS_HOVER = "#34d399"
    COLOR_ERROR = "#ef4444"

    def __init__(self) -> None:
        super().__init__()
        self.engine = CalculatorEngine()
        self.btn_widgets: Dict[str, tk.Button] = {}

        self._configure_window()
        self._create_widgets()
        self._bind_keyboard_events()
        self._update_display()

    def _configure_window(self) -> None:
        """Set window geometry, title, icons, and resizing parameters."""
        self.title("CodSoft | Modern Calculator")
        self.geometry("360x540")
        self.minsize(320, 480)
        self.configure(bg=self.COLOR_BG)

        # Make the main container responsive
        self.rowconfigure(0, weight=2)  # Display area
        self.rowconfigure(1, weight=5)  # Keypad grid
        self.columnconfigure(0, weight=1)

    def _create_widgets(self) -> None:
        """Construct display and keypad components."""
        # Top Display Container
        display_frame = tk.Frame(self, bg=self.COLOR_DISPLAY_BG, padx=20, pady=16)
        display_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 6))
        display_frame.columnconfigure(0, weight=1)

        # Sub-display for expression history
        self.history_label = tk.Label(
            display_frame,
            text="",
            anchor="e",
            bg=self.COLOR_DISPLAY_BG,
            fg=self.COLOR_TEXT_MUTED,
            font=("Segoe UI", 12),
        )
        self.history_label.grid(row=0, column=0, sticky="ew", pady=(4, 0))

        # Main display for current operand / result
        self.main_label = tk.Label(
            display_frame,
            text="0",
            anchor="e",
            bg=self.COLOR_DISPLAY_BG,
            fg=self.COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 28, "bold"),
        )
        self.main_label.grid(row=1, column=0, sticky="ew", pady=(4, 4))

        # Keypad Grid Frame
        keypad_frame = tk.Frame(self, bg=self.COLOR_BG, padx=8, pady=8)
        keypad_frame.grid(row=1, column=0, sticky="nsew")

        # Configure 5 rows and 4 columns with dynamic resizing weights
        for r in range(5):
            keypad_frame.rowconfigure(r, weight=1)
        for c in range(4):
            keypad_frame.columnconfigure(c, weight=1)

        # Layout specification: (text, row, col, type, command)
        button_specs = [
            ("C", 0, 0, "func", self._on_clear),
            ("⌫", 0, 1, "func", self._on_backspace),
            ("%", 0, 2, "func", self._on_percent),
            ("÷", 0, 3, "accent", lambda: self._on_operator("÷")),
            ("7", 1, 0, "num", lambda: self._on_digit("7")),
            ("8", 1, 1, "num", lambda: self._on_digit("8")),
            ("9", 1, 2, "num", lambda: self._on_digit("9")),
            ("×", 1, 3, "accent", lambda: self._on_operator("×")),
            ("4", 2, 0, "num", lambda: self._on_digit("4")),
            ("5", 2, 1, "num", lambda: self._on_digit("5")),
            ("6", 2, 2, "num", lambda: self._on_digit("6")),
            ("−", 2, 3, "accent", lambda: self._on_operator("−")),
            ("1", 3, 0, "num", lambda: self._on_digit("1")),
            ("2", 3, 1, "num", lambda: self._on_digit("2")),
            ("3", 3, 2, "num", lambda: self._on_digit("3")),
            ("+", 3, 3, "accent", lambda: self._on_operator("+")),
            ("±", 4, 0, "num", self._on_toggle_sign),
            ("0", 4, 1, "num", lambda: self._on_digit("0")),
            (".", 4, 2, "num", self._on_decimal),
            ("=", 4, 3, "equals", self._on_equals),
        ]

        for text, row, col, btype, cmd in button_specs:
            btn = self._build_button(keypad_frame, text, btype, cmd)
            btn.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            self.btn_widgets[text] = btn

    def _build_button(
        self,
        parent: tk.Widget,
        text: str,
        btype: str,
        command: Callable[[], None],
    ) -> tk.Button:
        """Create a styled button with responsive hover transitions."""
        if btype == "num":
            bg = self.COLOR_BTN_NUM
            hover = self.COLOR_BTN_NUM_HOVER
            fg = self.COLOR_TEXT_PRIMARY
            font = ("Segoe UI", 16, "bold")
        elif btype == "func":
            bg = self.COLOR_BTN_FUNC
            hover = self.COLOR_BTN_FUNC_HOVER
            fg = self.COLOR_TEXT_PRIMARY
            font = ("Segoe UI", 15, "bold")
        elif btype == "accent":
            bg = self.COLOR_BTN_ACCENT
            hover = self.COLOR_BTN_ACCENT_HOVER
            fg = "#ffffff"
            font = ("Segoe UI", 18, "bold")
        else:  # 'equals'
            bg = self.COLOR_BTN_EQUALS
            hover = self.COLOR_BTN_EQUALS_HOVER
            fg = "#ffffff"
            font = ("Segoe UI", 18, "bold")

        btn = tk.Button(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            relief="flat",
            borderwidth=0,
            font=font,
            cursor="hand2",
            command=command,
        )

        # Smooth hover feedback
        btn.bind("<Enter>", lambda e, b=btn, h=hover: b.config(bg=h))
        btn.bind("<Leave>", lambda e, b=btn, base=bg: b.config(bg=base))
        return btn

    def _bind_keyboard_events(self) -> None:
        """Map physical keyboard strokes to corresponding calculator operations."""
        self.bind("<Key>", self._on_key_press)
        self.bind("<Return>", lambda e: self._on_equals())
        self.bind("<KP_Enter>", lambda e: self._on_equals())
        self.bind("<BackSpace>", lambda e: self._on_backspace())
        self.bind("<Escape>", lambda e: self._on_clear())

    def _on_key_press(self, event: tk.Event) -> None:
        """Route standard alphanumeric keys to application features."""
        char = event.char
        if not char:
            return

        if char in "0123456789":
            self._flash_button(char)
            self._on_digit(char)
        elif char == ".":
            self._flash_button(".")
            self._on_decimal()
        elif char in "+":
            self._flash_button("+")
            self._on_operator("+")
        elif char in "-":
            self._flash_button("−")
            self._on_operator("−")
        elif char in "*xX":
            self._flash_button("×")
            self._on_operator("×")
        elif char == "/":
            self._flash_button("÷")
            self._on_operator("÷")
        elif char == "%":
            self._flash_button("%")
            self._on_percent()
        elif char == "=":
            self._flash_button("=")
            self._on_equals()

    def _flash_button(self, key_text: str) -> None:
        """Provide brief visual press feedback on keyboard entry."""
        btn = self.btn_widgets.get(key_text)
        if btn:
            orig_bg = btn.cget("bg")
            btn.config(bg=self.COLOR_BTN_FUNC_HOVER)
            self.after(120, lambda: btn.config(bg=orig_bg))

    # Event handlers
    def _on_digit(self, digit: str) -> None:
        self.engine.input_digit(digit)
        self._update_display()

    def _on_decimal(self) -> None:
        self.engine.input_decimal()
        self._update_display()

    def _on_operator(self, op: str) -> None:
        self.engine.input_operator(op)
        self._update_display()

    def _on_equals(self) -> None:
        self.engine.calculate()
        self._update_display()

    def _on_clear(self) -> None:
        self.engine.reset()
        self._update_display()

    def _on_backspace(self) -> None:
        self.engine.backspace()
        self._update_display()

    def _on_percent(self) -> None:
        self.engine.apply_percent()
        self._update_display()

    def _on_toggle_sign(self) -> None:
        self.engine.toggle_sign()
        self._update_display()

    def _update_display(self) -> None:
        """Synchronize UI labels with internal calculation states."""
        self.history_label.config(text=self.engine.expression_history)
        current = self.engine.current_operand

        # Dynamic font scaling if text exceeds standard line width
        if len(current) > 12:
            self.main_label.config(font=("Segoe UI", 20, "bold"))
        elif len(current) > 8:
            self.main_label.config(font=("Segoe UI", 24, "bold"))
        else:
            self.main_label.config(font=("Segoe UI", 28, "bold"))

        # Highlight error messages cleanly in red accent
        if self.engine.is_error_state:
            self.main_label.config(fg=self.COLOR_ERROR, text=current)
        else:
            self.main_label.config(fg=self.COLOR_TEXT_PRIMARY, text=current)


# ============================================================================
# Application Entry Point
# ============================================================================

def main() -> None:
    """Launch the Desktop Calculator GUI application."""
    try:
        app = CalculatorApp()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
