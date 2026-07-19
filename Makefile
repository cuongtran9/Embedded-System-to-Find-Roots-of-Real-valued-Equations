# ==============================================================================
# Makefile — GNU Make Build System
# ==============================================================================

.PHONY: all build lint lint-c lint-py test clean help

# Target mặc định — chạy khi gõ "make" không có tham số
all: lint build test

# ==============================================================================
# help — Hiển thị hướng dẫn sử dụng
# ==============================================================================
help:
	@echo "============================================="
	@echo " Equation Solver — Build System (GNU Make)"
	@echo "============================================="
	@echo ""
	@echo "  make all        Lint + Build + Test"
	@echo "  make build      Build ESP32 firmware (idf.py / gcc)"
	@echo "  make lint       Lint C code (cppcheck) + Python"
	@echo "  make lint-c     Lint C code only"
	@echo "  make lint-py    Lint Python code only"
	@echo "  make test       Run numerical accuracy tests"
	@echo "  make clean      Remove build artifacts"
	@echo "  make help       Show this message"
	@echo ""

# ==============================================================================
# build — Build firmware ESP32
# ==============================================================================
build:
	@echo "=== Building ESP32 firmware (gcc via ESP-IDF) ==="
	idf.py build
	@echo "=== Build complete ==="

# ==============================================================================
# lint — Kiểm tra lỗi tiềm ẩn trong code
# ==============================================================================
lint: lint-c lint-py
	@echo "=== All lint checks done ==="

lint-c:
	@echo "=== Linting C code with cppcheck ==="
	cppcheck --enable=warning,style,performance \
	         --error-exitcode=0 \
	         --suppress=missingIncludeSystem \
	         --std=c11 \
	         main/root32.c
	@echo "=== C lint complete ==="

lint-py:
	@echo "=== Checking Python syntax ==="
	python -m py_compile raspi/rootpi.py
	@echo "=== Python lint complete ==="

# ==============================================================================
# test — Chạy numerical accuracy tests
# ==============================================================================
test:
	@echo "=== Running numerical accuracy tests ==="
	python scripts/run_tests.py
	@echo "=== Tests complete ==="

# ==============================================================================
# clean — Xóa files build
# ==============================================================================
clean:
	@echo "=== Cleaning build artifacts ==="
	rm -rf build/
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -f *.xml *.log build-report.md
	@echo "=== Clean complete ==="
