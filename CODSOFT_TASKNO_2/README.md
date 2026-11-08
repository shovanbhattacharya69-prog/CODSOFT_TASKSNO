# Modern Desktop Calculator Application (GUI)

A production-grade, responsive desktop calculator developed in Python using the `tkinter` GUI toolkit. Designed and engineered for **Task 2 of the CodSoft Python Development Pipeline**.

---

## 🌟 Key Features

- **Standard Arithmetic Operations**: Seamless execution of Addition (`+`), Subtraction (`−`), Multiplication (`×`), and Division (`÷`).
- **Safe Expression Evaluation**: Powered by Python's `ast` (Abstract Syntax Tree) engine. Unlike insecure `eval()` implementations, this strictly parses approved arithmetic nodes, safeguarding against arbitrary code execution.
- **Robust Error Handling**:
  - Graceful trap for `ZeroDivisionError` displaying `"Cannot divide by zero"`.
  - Syntax error protection preventing GUI crashes on invalid sequences or buffer overflows.
  - Automatic error reset upon subsequent input.
- **Enhanced Utilities**:
  - Percentage computation (`%`).
  - Negation / Sign toggle (`±`).
  - Single-character Backspace (`⌫`) & Full Clear (`C`).
  - Dual-line display with calculation history tracking.
- **Responsive Aesthetic**:
  - Dark-mode color scheme inspired by modern IDE and macOS system calculators.
  - Scalable grid design using Tkinter weighted rows and columns.
  - Dynamic font resizing to handle long numeric outputs without clipping.
- **Full Keyboard Integration**: Complete hotkey support for standard number pads, Enter, Backspace, and Escape.

---

## ⌨️ Keyboard Shortcuts

| Key | Calculator Action |
| :--- | :--- |
| `0` - `9` | Input digits |
| `.` | Input decimal point |
| `+`, `-`, `*`, `/` | Addition, Subtraction, Multiplication, Division |
| `Enter` / `=` | Calculate result |
| `Backspace` | Delete last entered digit |
| `Escape` | Clear all (Reset) |
| `%` | Convert to percentage |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher installed on your system.
- Tkinter (included by default in standard Python distributions).

### Running the Application

Execute the script directly from your terminal:

```bash
# Windows
py main.py
# or
python main.py

# macOS / Linux
python3 main.py
```

---

## 🧪 Running Unit Tests

The test suite validates arithmetic accuracy, AST security boundaries, operator precedence, and state machine transitions.

```bash
py test_calculator.py
```

### Test Coverage Highlights:
- ✅ Basic arithmetic & unicode symbol normalization (`×`, `÷`, `−`)
- ✅ Operator precedence verification (`2 + 3 * 4 = 14`)
- ✅ Zero division exception capture
- ✅ Code injection defense testing
- ✅ Decimal constraints and backspace state management

---

## 🏛️ Architecture Overview

```
CODSOFT_TASKNO_2/
├── main.py              # Application entry point, SafeEvaluator, CalculatorEngine & Tkinter UI
├── test_calculator.py   # Comprehensive unit test suite (16 test cases)
└── README.md            # Technical documentation and user guide
```

- **`SafeEvaluator`**: Pure functional class that sanitizes and executes math strings safely using `ast.parse` and recursion.
- **`CalculatorEngine`**: Decoupled state management model handling formatting, operands, and operations.
- **`CalculatorApp`**: Tkinter presentation layer managing widget grid dynamics, hover animations, and event hooks.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
