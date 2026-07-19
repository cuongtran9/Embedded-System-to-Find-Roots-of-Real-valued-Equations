# ==============================================================================
# CMakeLists.txt — ESP-IDF Project Root
# ==============================================================================

# Yêu cầu CMake phiên bản 3.16 trở lên
cmake_minimum_required(VERSION 3.16)

# Import hệ thống build ESP-IDF
# $ENV{IDF_PATH} = đường dẫn đến thư mục ESP-IDF trên máy
# Ví dụ: /home/user/esp/esp-idf hoặc C:/Espressif/frameworks/esp-idf
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Đặt tên project — tên này sẽ thành tên firmware output
project(equation_solver)
