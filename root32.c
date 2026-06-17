#include <stdio.h>
#include <string.h>
#include <math.h>
#include <ctype.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

#define I2C_PORT I2C_NUM_0
#define LCD_ADDR 0x27
#define SDA_PIN 21
#define SCL_PIN 22
#define MAX_STACK_SIZE 30
#define MAX_ITERATIONS 50

// Keypad 5x4
#define ROWS 5
#define COLS 4

const gpio_num_t row_pins[ROWS] = {GPIO_NUM_15, GPIO_NUM_2, GPIO_NUM_0, GPIO_NUM_4, GPIO_NUM_16};
const gpio_num_t col_pins[COLS] = {GPIO_NUM_17, GPIO_NUM_5, GPIO_NUM_18, GPIO_NUM_19};

const char keymap[ROWS][COLS] = {
    {'S', 'D', '^', 'x'}, // Row 0: S: Solve, D: Delete, ^: power, x: variable
    {'1', '2', '3', '+'}, // Row 1
    {'4', '5', '6', '-'}, // Row 2
    {'7', '8', '9', '*'}, // Row 3
    {'.', '0', '=', '/'}  // Row 4
};

char equation[50] = {0};
char display_buf[17] = {0};

void lcd_send(uint8_t data, uint8_t rs) {
    uint8_t buf[4];
    uint8_t high = data & 0xF0;
    uint8_t low = (data << 4) & 0xF0;
    buf[0] = high | rs | 0x04 | 0x08;
    buf[1] = high | rs | 0x08;
    buf[2] = low | rs | 0x04 | 0x08;
    buf[3] = low | rs | 0x08;
    i2c_master_write_to_device(I2C_PORT, LCD_ADDR, buf, 4, 1000/portTICK_PERIOD_MS);
}
void lcd_command(uint8_t cmd) {
    lcd_send(cmd, 0x00);
    vTaskDelay(10 / portTICK_PERIOD_MS);
}
void lcd_data(uint8_t data) {
    lcd_send(data, 0x01);
    vTaskDelay(10 / portTICK_PERIOD_MS);
}
void lcd_init() {
    vTaskDelay(50 / portTICK_PERIOD_MS);
    lcd_command(0x33);
    lcd_command(0x32);
    lcd_command(0x28);
    lcd_command(0x0C);
    lcd_command(0x06);
    lcd_command(0x01);
    vTaskDelay(100 / portTICK_PERIOD_MS);
}
void lcd_print(const char *str) {
    while(*str)
        lcd_data(*str++);
}
void keypad_init() {
    for(int i = 0; i < ROWS; i++){
        gpio_reset_pin(row_pins[i]);
        gpio_set_direction(row_pins[i], GPIO_MODE_OUTPUT);
        gpio_set_level(row_pins[i], 1);
    }
    for(int i = 0; i < COLS; i++){
        gpio_reset_pin(col_pins[i]);
        gpio_set_direction(col_pins[i], GPIO_MODE_INPUT);
        gpio_pullup_en(col_pins[i]);
    }
}
char get_key() {
    char key = 0;
    for(int r = 0; r < ROWS; r++){
        gpio_set_level(row_pins[r], 0);
        vTaskDelay(1 / portTICK_PERIOD_MS);
        for(int c = 0; c < COLS; c++){
            if(gpio_get_level(col_pins[c])) continue;
            key = keymap[r][c];
            while(!gpio_get_level(col_pins[c])) 
                vTaskDelay(10 / portTICK_PERIOD_MS);
            gpio_set_level(row_pins[r], 1);
            vTaskDelay(20 / portTICK_PERIOD_MS);
            return key;
        }
        gpio_set_level(row_pins[r], 1);
    }
    return 0;
}

double evaluate(const char *expr, double x) {
    double stack[MAX_STACK_SIZE];
    char op_stack[MAX_STACK_SIZE];
    int s_ptr = 0, o_ptr = 0;
    const char *p = expr;
    
    while(*p) {
        if(*p == 'x') {
            stack[s_ptr++] = x;
            p++;
        } else if(isdigit(*p) || *p == '.') {
            char *end;
            double num = strtod(p, &end);
            stack[s_ptr++] = num;
            p = end;
        } else if(isspace(*p)) {
            p++;
        } else {
            char op = *p++;
            // Handle unary minus: nếu '-' đứng đầu biểu thức
            if(op == '-' && s_ptr == 0) {
                stack[s_ptr++] = 0.0;
            }
            while(o_ptr > 0) {
                char prev_op = op_stack[o_ptr-1];
                int prec_prev = (prev_op == '^') ? 3 : ((prev_op == '*' || prev_op == '/') ? 2 : 1);
                int prec_curr = (op == '^') ? 3 : ((op == '*' || op == '/') ? 2 : 1);
                if(prec_prev >= prec_curr) {
                    op_stack[--o_ptr];
                    if(s_ptr < 2) return NAN;
                    double b = stack[--s_ptr];
                    double a = stack[--s_ptr];
                    switch(prev_op) {
                        case '+': stack[s_ptr++] = a + b; break;
                        case '-': stack[s_ptr++] = a - b; break;
                        case '*': stack[s_ptr++] = a * b; break;
                        case '/': 
                            if(fabs(b) < 1e-12) return NAN;
                            stack[s_ptr++] = a / b; break;
                        case '^': stack[s_ptr++] = pow(a, b); break;
                        default: return NAN;
                    }
                } else {
                    break;
                }
            }
            op_stack[o_ptr++] = op;
        }
    }
    while(o_ptr > 0) {
        if(s_ptr < 2) return NAN;
        char op = op_stack[--o_ptr];
        double b = stack[--s_ptr];
        double a = stack[--s_ptr];
        switch(op) {
            case '+': stack[s_ptr++] = a + b; break;
            case '-': stack[s_ptr++] = a - b; break;
            case '*': stack[s_ptr++] = a * b; break;
            case '/': 
                if(fabs(b) < 1e-12) return NAN;
                stack[s_ptr++] = a / b; break;
            case '^': stack[s_ptr++] = pow(a, b); break;
            default: return NAN;
        }
    }
    return (s_ptr == 1) ? stack[0] : NAN;
}

double newton_raphson(const char *eq, double x0) {
    const double h = 1e-6;
    const double eps = 1e-6;
    double x = x0;
    
    for(int i = 0; i < MAX_ITERATIONS; i++) {
        double fx = evaluate(eq, x);
        double fxh1 = evaluate(eq, x + h);
        double fxh2 = evaluate(eq, x - h);
        if(isnan(fx) || isnan(fxh1) || isnan(fxh2))
            break;
        double dfx = (fxh1 - fxh2) / (2 * h);
        if(fabs(dfx) < eps) { 
            x += 1.0; 
            continue;
        }
        double delta = fx / dfx;
        x -= delta;
        if(fabs(delta) < eps)
            return x;
    }
    return x;
}

void solve_equation() {
    // Tìm dấu '=' trong equation
    char *eq_ptr = strchr(equation, '=');
    if(!eq_ptr) {
        lcd_command(0x01);
        lcd_print("No '=' sign");
        return;
    }
    
    // Xây dựng hàm f(x)=LHS - RHS mà không thêm ngoặc thừa
    char full_eq[100];
    snprintf(full_eq, sizeof(full_eq), "%.*s-%s", (int)(eq_ptr - equation), equation, eq_ptr + 1);
    
    double root;
    // Thử với nhiều giá trị ban đầu để cải thiện khả năng hội tụ
    root = newton_raphson(full_eq, 1.0);
    if(isnan(root) || fabs(evaluate(full_eq, root)) > 1e-3)
        root = newton_raphson(full_eq, 10.0);
    if(isnan(root) || fabs(evaluate(full_eq, root)) > 1e-3)
        root = newton_raphson(full_eq, -1.0);
    
    lcd_command(0x01);
    if(isnan(root) || fabs(evaluate(full_eq, root)) > 1e-3) {
        lcd_print("No Solution");
    } else {
        char buf[17];
        snprintf(buf, sizeof(buf), "x=%.4f", root);
        lcd_print(buf);
    }
}

void setup() {
    // Cấu hình I2C, LCD, Keypad, v.v. (giữ nguyên như ban đầu)
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = SDA_PIN,
        .scl_io_num = SCL_PIN,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master = {.clk_speed = 100000}
    };
    i2c_param_config(I2C_PORT, &conf);
    i2c_driver_install(I2C_PORT, conf.mode, 0, 0, 0);
    
    lcd_init();
    keypad_init();
    lcd_print("Input equation:");
}

void loop() {
    char key = get_key();
    if (!key) {
        vTaskDelay(200 / portTICK_PERIOD_MS);
        return;
    }
    
    if(key == 'S') {  // 'S' dùng để giải phương trình
        solve_equation();
        memset(equation, 0, sizeof(equation));
    } else if(key == 'D') {  // 'D' dùng để xóa phương trình
        memset(equation, 0, sizeof(equation));
        lcd_command(0x01);
        lcd_print("Input equation:");
    } else if(strlen(equation) < sizeof(equation)-1) {
        strncat(equation, &key, 1);
        lcd_command(0xC0);
        lcd_print(equation);
    }
    
    vTaskDelay(100 / portTICK_PERIOD_MS);
}
