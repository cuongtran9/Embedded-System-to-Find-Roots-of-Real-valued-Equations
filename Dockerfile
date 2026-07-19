# ==============================================================================
# Dockerfile — Reproducible Build Environment
# ==============================================================================

# Base image: ESP-IDF chính thức của Espressif
FROM espressif/idf:v5.1

# Cài thêm công cụ cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    cppcheck \
    && rm -rf /var/lib/apt/lists/*

# Cài Python dependencies
COPY scripts/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Set thư mục làm việc
WORKDIR /workspace

# Lệnh mặc định: chạy make all (lint + build + test)
CMD ["make", "all"]
