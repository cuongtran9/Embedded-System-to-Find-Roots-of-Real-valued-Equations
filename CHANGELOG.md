# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.1.0]

### Added
- **CI/CD:** GitHub Actions workflow — 3 jobs (lint, build, test)
- **Build System:** GNU Makefile with targets: build, lint, test, clean
- **Build System:** ESP-IDF CMakeLists.txt (root + main component)
- **Docker:** Reproducible build environment (ESP-IDF + gcc + cppcheck)
- **Scripts:** `scripts/run_tests.py` — numerical accuracy tests with JUnit XML
- **Scripts:** `scripts/generate_report.py` — build report generator
- **Documentation:** `CHANGELOG.md` — version history
- **Documentation:** `.gitignore` — ESP-IDF build, Python cache, IDE files

### Changed
- **Project Structure:** Migrated to ESP-IDF standard layout (`main/`, `raspi/`)
- **README:** Added CI/CD, build descriptions, testing sections

---

## [1.0.0]

### Added
- **ESP32 Firmware (`root32.c`):**
  - Newton-Raphson numerical solver (50 iterations, 3 initial guesses)
  - Stack-based expression parser with operator precedence
  - 5×4 matrix keypad input via GPIO
  - 16×2 I2C LCD output (PCF8574)
  - FreeRTOS task-based architecture
- **Raspberry Pi Script (`rootpi.py`):**
  - Newton-Raphson solver (100 iterations, 5 initial guesses)
  - Multi-root detection (up to 2 distinct roots)
  - 4×4 matrix keypad via GPIO
  - Equation preprocessing with regex
- **Documentation:** README with hardware specs, pin config, usage examples
