# Sử dụng Python làm base image
FROM python:3.9-slim

# Cài đặt các công cụ cần thiết cho Playwright và Chromium
RUN apt-get update && apt-get install -y \
    curl \
    libx11-dev \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt Playwright và các trình duyệt (Chromium)
RUN pip install playwright \
    && playwright install

# Sao chép mã nguồn và file .env
COPY . .

# Đặt biến môi trường Flask
ENV FLASK_APP=server_recommend_ListTrip_multiple_suggestion12.py
ENV FLASK_ENV=production

# Cài đặt biến môi trường cho OpenAI API Key
# Tham chiếu tới file .env trong Docker container
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Mở cổng 5000
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["flask", "run", "--host=0.0.0.0"]
