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
| Input | 4x5 Matrix Keypad |
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

### ESP32 — 4×5 Keypad

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

### ESP32 (4×5)

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
│  S  │  x  │  =  │  ^  │  ← 'S' to Solve
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
3. Press **S** (dot key) to solve
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
├── main/                          # ESP32 firmware (ESP-IDF component)
│   ├── root32.c                   # C source — keypad, LCD, Newton-Raphson solver
│   └── CMakeLists.txt             # ESP-IDF component registration
│
├── raspi/                         # Raspberry Pi
│   └── rootpi.py                  # Python script — GPIO keypad, multi-root solver
│
├── scripts/                       # Python automation
│   ├── run_tests.py               # Numerical accuracy tests (JUnit XML)
│   ├── generate_report.py         # Build report generator
│   └── requirements.txt           # Python dependencies
│
├── .github/
│   └── workflows/ci.yml           # GitHub Actions CI pipeline
│
├── CMakeLists.txt                 # ESP-IDF project root config
├── Makefile                       # GNU Make build system
├── Dockerfile                     # Reproducible build environment
├── CHANGELOG.md                   # Version history
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## CI/CD Pipeline

The project uses **GitHub Actions** to automatically test each code push:

```
┌──────────┐     ┌─────────────────┐     ┌───────────────────┐
│ Checkout │────►│ 🔍 Lint C Code  │────►│ 🔨 Build ESP32    │
│ code     │     │ (cppcheck)      │     │ (gcc via ESP-IDF) │
└──────────┘     └────────┬────────┘     └───────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ 🧪 Python Tests │
                 │ (Newton-Raphson │
                 │  accuracy)      │
                 └─────────────────┘
```

- **Lint:** `cppcheck` static analysis C code
- **Build:** ESP-IDF compile firmware with `xtensa-esp32-elf-gcc`
- **Test:** Verify Newton-Raphson solver with known equation

---

## Build Instructions

### Use Make (GNU Make)

```bash
make all            # Lint + Build + Test
make build          # Build ESP32 firmware (gcc via ESP-IDF)
make lint           # Lint C (cppcheck) + Python
make test           # Run numerical accuracy tests
make clean          # Remove build artifacts
make help           # Show all targets
```

### Use ESP-IDF CLI

```bash
idf.py build                    # Build firmware
idf.py -p <PORT> flash monitor  # Flash + serial monitor
```

### Use Docker

```bash
docker build -t eq-solver .                        # Build image
docker run --rm -v $(pwd):/workspace eq-solver make lint   # Lint
docker run --rm -v $(pwd):/workspace eq-solver make test   # Test
```

---

## Testing

Numerical accuracy tests verify the Newton-Raphson algorithm:

```bash
python scripts/run_tests.py
```

| Test Case | Equation | Expected Roots | Tolerance |
|-----------|----------|---------------|----------|
| linear_simple | `2*x+6=0` | -3.0 | 0.01 |
| quadratic_simple | `x^2=4` | ±2.0 | 0.01 |
| quadratic_factored | `x^2+3*x-10=0` | -5.0, 2.0 | 0.01 |
| cubic_simple | `x^3-x=0` | -1.0, 0.0, 1.0 | 0.01 |

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) — version history.
