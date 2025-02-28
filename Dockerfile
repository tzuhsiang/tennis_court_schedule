# 使用Python官方映像檔
FROM python:3.11-slim

# 安裝必要套件
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 設定環境變數
ENV PATH="/usr/local/bin:$PATH"
ENV CHROME_BIN="/usr/bin/chromium"
ENV CHROMEDRIVER_BIN="/usr/bin/chromedriver"

# 工作目錄
WORKDIR /app

# 複製程式碼和需求檔
COPY requirements.txt requirements.txt
COPY scraper.py scraper.py

# 安裝Python套件
RUN pip install --no-cache-dir -r requirements.txt

# 設定容器預設執行程式
CMD ["python", "scraper.py"]
