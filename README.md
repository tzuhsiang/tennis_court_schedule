# 🏸 古亭河濱公園網球場租借狀態爬蟲

## 📌 專案介紹
這是一個使用 Selenium 爬取 **台北市體育場租借系統** 之「古亭河濱公園網球場」租借狀態的專案。
本專案已打包成 **Docker**，可透過 `docker-compose` 管理，輕鬆部署並定期執行。

---

## 📁 專案結構

```
tenis-court-scraper/
├── docker-compose.yml     # Docker Compose 管理
├── Dockerfile             # Docker 環境建置
├── scraper.py             # 爬取租借狀態的 Python 程式
├── requirements.txt       # 需要安裝的 Python 套件
├── README.md              # 專案說明文件
└── data/                  # 存放爬取結果的資料夾
```

---

## 🚀 快速開始

### 1️⃣ 安裝 Docker
請先確保你的系統已安裝 Docker 與 Docker Compose。
- [Docker 安裝指南](https://docs.docker.com/get-docker/)
- [Docker Compose 安裝指南](https://docs.docker.com/compose/install/)

### 2️⃣ Clone 專案
```bash
git clone https://github.com/your-repo/tennis-court-scraper.git
cd tennis-court-scraper
```

### 3️⃣ 啟動爬蟲
```bash
docker-compose up --build
```
執行後，爬取到的租借狀態會存入 `data/古亭河濱公園_網球場租借狀態.csv`

---

## 📜 設定說明

### `docker-compose.yml`
```yaml
version: '3'
services:
  court-scraper:
    build: .
    container_name: tennis-court-scraper
    volumes:
      - ./data:/app
    environment:
      - TZ=Asia/Taipei
    restart: "no"
```
此設定會：
1. 自動建置並執行爬蟲程式。
2. 設定時區為 `Asia/Taipei`。
3. 儲存爬取結果到 `data/` 資料夾。

---

## 📊 輸出範例
當爬取成功後，將產生以下 CSV 檔案：

📂 **data/古亭河濱公園_網球場租借狀態.csv**

| 時段 | 場地1 | 場地2 | 場地3 | 場地4 |
|------|------|------|------|------|
| 08:00-09:00 | 已租 | 空場 | 已租 | 已租 |
| 09:00-10:00 | 空場 | 已租 | 空場 | 已租 |

---

## ⏰ 定時執行
如果希望每天自動執行一次，可以使用 `crontab` 來設定：
```bash
crontab -e
```
新增以下排程，每天早上 8 點執行一次：
```bash
0 8 * * * cd /path/to/tennis-court-scraper && docker-compose up --build
```

---

## 📌 進階功能
✅ **加入 LINE Notify** 當場地有空位時自動通知。
✅ **匯出 Google Sheets** 讓團隊成員直接查看。
✅ **Web API 查詢** 打造前端網頁顯示即時資訊。

---

## 🤝 貢獻
歡迎提供改進意見或 PR！

📧 聯絡方式: your.email@example.com

GitHub Repo: [https://github.com/your-repo/tennis-court-scraper](https://github.com/your-repo/tennis-court-scraper)