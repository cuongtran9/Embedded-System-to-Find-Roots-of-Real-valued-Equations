#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Equation Solver — Numerical Accuracy Test Runner
=================================================

Output JUnit XML:
  CI systems (GitHub Actions, Jenkins) đều hiểu format JUnit XML.
  Nó cho phép CI hiển thị test results đẹp trên giao diện web.

Usage:
    python scripts/run_tests.py
    python scripts/run_tests.py --junit-xml test-results.xml
"""

import argparse
import math
import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Thêm project root vào Python path để import raspi/rootpi.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "raspi"))


# ==============================================================================
# Re-implement Newton-Raphson (portable — không cần GPIO/RPi.GPIO)
# ==============================================================================

import re
import numpy as np


def preprocess_equation(eq_str: str) -> str:
    """Chuyển equation thành biểu thức Python.

    Ví dụ: "x^2=4" → "(x**2) - (4)"
    """
    eq_str = eq_str.replace(" ", "")
    eq_str = re.sub(r"([0-9.]+)(x)", r"\1*\2", eq_str)
    eq_str = re.sub(r"(x)([0-9.]+)", r"\1*\2", eq_str)
    eq_str = eq_str.replace("^", "**")
    if "=" in eq_str:
        left, right = eq_str.split("=", 1)
        return f"({left}) - ({right})"
    return eq_str


def newton_raphson(f, x0: float, tol: float = 1e-7, max_iter: int = 100):
    """Giải phương trình f(x)=0 bằng Newton-Raphson.

    Thuật toán:
        x_{n+1} = x_n - f(x_n) / f'(x_n)

    f'(x) được tính bằng central difference:
        f'(x) ≈ (f(x+h) - f(x-h)) / (2*h)
    """
    h = 1e-5
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        dfx = (f(x + h) - f(x - h)) / (2 * h)
        if abs(dfx) < 1e-10:
            return None
        x -= fx / dfx
    return x if abs(f(x)) < tol else None


def find_roots(f, initial_guesses=None):
    """Tìm nghiệm với nhiều điểm khởi đầu."""
    if initial_guesses is None:
        initial_guesses = [-5, -2, 0, 2, 5]
    roots = []
    for x0 in initial_guesses:
        root = newton_raphson(f, x0)
        if root is not None:
            if not roots or all(abs(root - r) > 1e-4 for r in roots):
                roots.append(round(root, 6))
    return sorted(roots)


# ==============================================================================
# Test Cases
# ==============================================================================

TEST_CASES = [
    ("linear_simple",       "2*x+6=0",       [-3.0]),
    ("quadratic_simple",    "x^2=4",          [-2.0, 2.0]),
    ("quadratic_factored",  "x^2+3*x-10=0",  [-5.0, 2.0]),
    ("cubic_simple",        "x^3-x=0",        [-1.0, 0.0, 1.0]),
    ("linear_identity",     "x=5",            [5.0]),
    ("quadratic_negative",  "x^2+1=2",        [-1.0, 1.0]),
]

TOLERANCE = 0.01


class TestResult:
    """Kết quả 1 test case."""
    def __init__(self, name: str, equation: str):
        self.name = name
        self.equation = equation
        self.passed = False
        self.expected = []
        self.actual = []
        self.error_msg = ""
        self.duration = 0.0


def run_test(name: str, equation: str, expected_roots: list[float]) -> TestResult:
    """Chạy 1 test case và so sánh kết quả."""
    result = TestResult(name, equation)
    result.expected = expected_roots
    start = datetime.now()

    try:
        expr = preprocess_equation(equation)
        f = lambda x: eval(expr, {"x": x, "np": np, "__builtins__": {}})
        actual_roots = find_roots(f)
        result.actual = actual_roots

        # Kiểm tra: mỗi expected root phải có ít nhất 1 actual root gần nó
        matched = 0
        for exp in expected_roots:
            if any(abs(exp - act) < TOLERANCE for act in actual_roots):
                matched += 1

        if matched == len(expected_roots):
            result.passed = True
            print(f"  ✅ {name}: {equation} → {actual_roots}")
        else:
            result.error_msg = f"Expected {expected_roots}, got {actual_roots}"
            print(f"  ❌ {name}: {equation}")
            print(f"     Expected: {expected_roots}")
            print(f"     Got:      {actual_roots}")

    except Exception as e:
        result.error_msg = str(e)
        print(f"  ❌ {name}: {equation} → ERROR: {e}")

    result.duration = (datetime.now() - start).total_seconds()
    return result


def check_source_files() -> TestResult:
    """Verify source files tồn tại."""
    result = TestResult("source_files_exist", "Check project structure")
    start = datetime.now()

    expected = [
        PROJECT_ROOT / "main" / "root32.c",
        PROJECT_ROOT / "raspi" / "rootpi.py",
        PROJECT_ROOT / "CMakeLists.txt",
        PROJECT_ROOT / "main" / "CMakeLists.txt",
    ]

    missing = [f for f in expected if not f.exists()]

    if not missing:
        result.passed = True
        print(f"  ✅ All {len(expected)} source files found")
    else:
        result.error_msg = f"Missing: {', '.join(f.name for f in missing)}"
        print(f"  ❌ Missing files: {result.error_msg}")

    result.duration = (datetime.now() - start).total_seconds()
    return result


def generate_junit_xml(results: list[TestResult], output_path: str):
    """Generate JUnit XML report cho CI (GitHub Actions / Jenkins)."""
    testsuite = ET.Element("testsuite")
    testsuite.set("name", "Equation-Solver-Tests")
    testsuite.set("tests", str(len(results)))
    testsuite.set("failures", str(sum(1 for r in results if not r.passed)))
    testsuite.set("time", f"{sum(r.duration for r in results):.3f}")
    testsuite.set("timestamp", datetime.now().isoformat())

    for r in results:
        testcase = ET.SubElement(testsuite, "testcase")
        testcase.set("name", r.name)
        testcase.set("classname", "NumericalAccuracy")
        testcase.set("time", f"{r.duration:.3f}")
        if not r.passed:
            failure = ET.SubElement(testcase, "failure")
            failure.set("message", r.error_msg)
            failure.text = r.error_msg

    tree = ET.ElementTree(testsuite)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="unicode", xml_declaration=True)
    print(f"\n📄 JUnit XML report: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Equation Solver — Test Runner")
    parser.add_argument(
        "--junit-xml", type=str, default=None,
        help="Output JUnit XML report (for CI)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print(" Equation Solver — Numerical Accuracy Tests")
    print("=" * 60)

    all_results: list[TestResult] = []

    # Test 1: Source files exist
    print("\n📁 Checking project structure...")
    all_results.append(check_source_files())

    # Test 2: Numerical accuracy
    print("\n🔢 Running Newton-Raphson solver tests...")
    for name, equation, expected in TEST_CASES:
        all_results.append(run_test(name, equation, expected))

    # Summary
    passed = sum(1 for r in all_results if r.passed)
    failed = sum(1 for r in all_results if not r.passed)
    total = len(all_results)

    print("\n" + "=" * 60)
    status = "✅ ALL PASSED" if failed == 0 else "❌ SOME FAILED"
    print(f" {status}: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    if args.junit_xml:
        generate_junit_xml(all_results, args.junit_xml)

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
