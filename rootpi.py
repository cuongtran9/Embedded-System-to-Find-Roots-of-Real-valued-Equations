import RPi.GPIO as GPIO
import time
import re
import numpy as np

# Cấu hình GPIO
GPIO.setmode(GPIO.BCM)

rows = [17, 27, 22, 5]    # Hàng GPIO
cols = [6, 13, 19, 26]    # Cột GPIO
#cols = [23, 24, 25, 16]    # Cột GPIO

# Thiết lập các chân hàng là OUTPUT và HIGH
for row in rows:
    GPIO.setup(row, GPIO.OUT)
    GPIO.output(row, GPIO.HIGH)

# Thiết lập các chân cột là INPUT với pull-up
for col in cols:
    GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Bản đồ phím mới với '.' và '=' cùng hàng
keymap = [
    ['1', '2', '3', '+'],
    ['4', '5', '6', '-'],
    ['7', '8', '9', '*'],
    ['^', 'x', '=', '.']  # Phím '=' ở [3][2], '.' ở [3][3]
]

def read_key():
    for i, row in enumerate(rows):
        GPIO.output(row, GPIO.LOW)
        for j, col in enumerate(cols):
            if GPIO.input(col) == GPIO.LOW:
                GPIO.output(row, GPIO.HIGH)
                return keymap[i][j]
        GPIO.output(row, GPIO.HIGH)
    return None

def preprocess_equation(eq_str):
    eq_str = eq_str.replace(' ', '')
    eq_str = re.sub(r'([0-9.]+)(x)', r'\1*\2', eq_str)
    eq_str = re.sub(r'(x)([0-9.]+)', r'\1*\2', eq_str)
    eq_str = eq_str.replace('^', '**')
    if '=' in eq_str:
        left, right = eq_str.split('=', 1)
        return f'({left}) - ({right})'
    return eq_str

def newton_raphson(f, x0, tol=1e-7, max_iter=100):
    """Giải pháp trình bằng phương pháp Newton-Raphson"""
    h = 1e-5  # Bước nhảy để tính đạo hàm
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        # Tính đạo hàm số
        dfx = (f(x + h) - f(x - h)) / (2 * h)
        if abs(dfx) < 1e-10:  # Tránh chia cho 0
            return None
        x -= fx / dfx
    return x if abs(f(x)) < tol else None

def find_roots(f):
    """Tìm nghiệm bằng phương pháp Newton-Raphson với các điểm khởi đầu khác nhau"""
    roots = []
    for x0 in [-5, -2, 0, 2, 5]:
        root = newton_raphson(f, x0)
        if root is not None:
            # Kiểm tra nghiệm trùng lặp
            if not roots or all(abs(root - r) > 1e-5 for r in roots):
                roots.append(root)
                if len(roots) >= 2:
                    break
    return roots

def main():
    equation = ''
    print("Nhập phương trình (Nhấn / để giải):")
    try:
        while True:
            key = read_key()
            if key:
                if key == '.':
                    print("\nĐang giải phương trình:", equation)
                    try:
                        expr = preprocess_equation(equation)
                        f = lambda x: eval(expr, {'x': x, 'np': np})
                        roots = find_roots(f)
                        if len(roots) >= 2:
                            print(f"Nghiệm x1 = {roots[0]:.7f}")
                            print(f"Nghiệm x2 = {roots[1]:.7f}")
                        elif len(roots) == 1:
                            print(f"Nghiệm duy nhất x = {roots[0]:.7f}")
                        else:
                            print("Không tìm thấy nghiệm!")
                    except Exception as e:
                        print("Lỗi:", e)
                    equation = ''
                else:
                    equation += key
                    print("\rPhương trình:", equation, end='')
                time.sleep(0.3)
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
