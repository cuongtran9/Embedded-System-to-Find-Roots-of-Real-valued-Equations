# Embedded System to Find Roots of Real-valued Equations

An embedded system project that solves real-valued equations using the **Newton-Raphson** numerical method. The system allows users to input mathematical equations via a **matrix keypad** and displays the computed roots on an **LCD screen** (ESP32) or **terminal** (Raspberry Pi).

Two hardware platforms are supported:

| Platform | Source File | Language |
|---|---|---|
| **ESP32** (FreeRTOS) | `root32.c` | C |
| **Raspberry Pi** | `rootpi.py` | Python |

---

## Table of Contents

- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Pin Configuration](#pin-configuration)
- [Keypad Layout](#keypad-layout)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Examples](#examples)
- [Project Structure](#project-structure)

---

## Features

- 🔢 **Equation Input** — Enter equations character-by-character using a physical matrix keypad
- ⚙️ **Newton-Raphson Solver** — Numerical root-finding with central difference derivative approximation
- 🔁 **Multiple Initial Guesses** — Automatically retries with different starting points to improve convergence
- 📟 **Real-time Display** — Live feedback on I2C LCD (ESP32) or terminal (Raspberry Pi)
- ➕ **Operator Support** — Addition (`+`), Subtraction (`-`), Multiplication (`*`), Division (`/`), Power (`^`)
- 🧮 **Multi-root Detection** — Raspberry Pi version can find up to 2 distinct roots

---

## Hardware Requirements

### ESP32 Version (`root32.c`)

| Component | Specification |
|---|---|
| Microcontroller | ESP32 DevKit |
| Display | 16×2 I2C LCD (PCF8574, address `0x27`) |
| Input | 5×4 Matrix Keypad |
| Framework | ESP-IDF with FreeRTOS |

### Raspberry Pi Version (`rootpi.py`)

| Component | Specification |
|---|---|
| Board | Raspberry Pi (any model with GPIO) |
| Input | 4×4 Matrix Keypad |
| Output | Terminal / Console |
| Dependencies | `RPi.GPIO`, `numpy` |

---

## Pin Configuration

### ESP32 — I2C LCD

| Signal | GPIO Pin |
|---|---|
| SDA | GPIO 21 |
| SCL | GPIO 22 |

### ESP32 — 5×4 Keypad

| Function | GPIO Pins |
|---|---|
| Rows (output) | GPIO 15, 2, 0, 4, 16 |
| Columns (input) | GPIO 17, 5, 18, 19 |

### Raspberry Pi — 4×4 Keypad

| Function | GPIO Pins (BCM) |
|---|---|
| Rows (output) | GPIO 17, 27, 22, 5 |
| Columns (input) | GPIO 6, 13, 19, 26 |

---

## Keypad Layout

### ESP32 (5×4)

```
┌─────┬─────┬─────┬─────┐
│  S  │  D  │  ^  │  x  │  ← S: Solve, D: Delete
├─────┼─────┼─────┼─────┤
│  1  │  2  │  3  │  +  │
├─────┼─────┼─────┼─────┤
│  4  │  5  │  6  │  -  │
├─────┼─────┼─────┼─────┤
│  7  │  8  │  9  │  *  │
├─────┼─────┼─────┼─────┤
│  .  │  0  │  =  │  /  │
└─────┴─────┴─────┴─────┘
```

### Raspberry Pi (4×4)

```
┌─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  +  │
├─────┼─────┼─────┼─────┤
│  4  │  5  │  6  │  -  │
├─────┼─────┼─────┼─────┤
│  7  │  8  │  9  │  *  │
├─────┼─────┼─────┼─────┤
│  ^  │  x  │  =  │  .  │  ← '.' to Solve
└─────┴─────┴─────┴─────┘
```

---

## How It Works

### Newton-Raphson Method

Both implementations use the **Newton-Raphson** iterative method to find roots of `f(x) = 0`:

$$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$

The derivative `f'(x)` is approximated numerically using the **central difference formula**:

$$f'(x) \approx \frac{f(x+h) - f(x-h)}{2h}$$

### Equation Parsing

1. The user enters an equation in the form `LHS = RHS` (e.g., `x^2=4`)
2. The system transforms it into `f(x) = LHS - RHS`
3. Newton-Raphson is applied to find `x` where `f(x) = 0`

### Convergence Strategy

| Parameter | ESP32 | Raspberry Pi |
|---|---|---|
| Step size `h` | `1e-6` | `1e-5` |
| Tolerance `ε` | `1e-6` | `1e-7` |
| Max iterations | 50 | 100 |
| Initial guesses | `1.0`, `10.0`, `-1.0` | `-5`, `-2`, `0`, `2`, `5` |
| Max roots found | 1 | 2 |

---

## Getting Started

### ESP32

**Prerequisites:**
- [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/) installed and configured

**Build & Flash:**

```bash
idf.py build
idf.py -p <PORT> flash monitor
```

### Raspberry Pi

**Prerequisites:**
- Python 3 with `RPi.GPIO` and `numpy`

**Install dependencies:**

```bash
pip install RPi.GPIO numpy
```

**Run:**

```bash
python rootpi.py
```

---

## Usage

### ESP32

1. Power on the ESP32 — LCD displays `Input equation:`
2. Enter an equation using the keypad (e.g., `x^2=4`)
3. Press **S** (Solve) to compute the root
4. The LCD displays the result (e.g., `x=2.0000`) or `No Solution`
5. Press **D** (Delete) to clear and start over

### Raspberry Pi

1. Run `python rootpi.py` — terminal shows `Nhập phương trình`
2. Enter an equation using the keypad (e.g., `x^2=4`)
3. Press **.** (dot key) to solve
4. Results are printed to the terminal with up to 2 roots
5. The input is automatically cleared for the next equation

---

## Examples

| Input Equation | Expected Output |
|---|---|
| `x^2=4` | `x = 2.0000` or `x = -2.0000` |
| `x^2+3*x-10=0` | `x = 2.0000` |
| `2*x+6=0` | `x = -3.0000` |
| `x^3-x=0` | `x = 0.0000`, `x = 1.0000` |

---

## Project Structure

```
Embedded-System-to-Find-Roots-of-Real-valued-Equations/
├── root32.c       # ESP32 firmware (C, ESP-IDF/FreeRTOS)
├── rootpi.py      # Raspberry Pi script (Python)
└── README.md      # Project documentation
```

---

## License

This project is developed as part of a graduation thesis (Đồ án tốt nghiệp).