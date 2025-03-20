import os
import json
import time
import requests
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CourtScheduleScraper:
    def __init__(self):
        self.base_url = "https://vbs.sports.taipei/_/x/xhrworkv3.php"
        self.phpsessid = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://vbs.sports.taipei/venues/?K=305",
            "Origin": "https://vbs.sports.taipei"
        }
        
    def get_phpsessid(self):
        """使用 Selenium 獲取 PHPSESSID"""
        print("開始獲取 PHPSESSID...")
        options = webdriver.ChromeOptions()
        
        # 基本設定
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # 提高穩定性的設定
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-infobars")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=zh-TW")
        
        # 防止檢測的設定
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 使用 Selenium Grid
        selenium_url = os.getenv("SELENIUM_REMOTE_URL", "http://chrome:4444/wd/hub")
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"嘗試連接 Selenium Grid (嘗試 {retry_count + 1}/{max_retries})...")
                driver = webdriver.Remote(
                    command_executor=selenium_url,
                    options=options
                )
                
                print("正在載入網頁...")
                driver.get("https://vbs.sports.taipei")
                
                # 等待 reCAPTCHA 元素出現
                print("等待頁面載入完成...")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
                )
                
                # 等待 reCAPTCHA 自動驗證
                print("等待 reCAPTCHA 驗證（8秒）...")
                time.sleep(8)
                
                # 再次嘗試載入頁面確認驗證已通過
                driver.get("https://vbs.sports.taipei")
                time.sleep(2)
                
                # 獲取 cookies
                cookies = driver.get_cookies()
                for cookie in cookies:
                    if cookie["name"] == "PHPSESSID":
                        self.phpsessid = cookie["value"]
                        print("✅ 成功獲取 PHPSESSID")
                        driver.quit()
                        return
                        
                print("未找到 PHPSESSID，將重試...")
                retry_count += 1
                
            except Exception as e:
                print(f"發生錯誤: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"將在 5 秒後重試...")
                    time.sleep(5)
            finally:
                try:
                    if driver:
                        driver.quit()
                except Exception:
                    pass
        
        raise Exception(f"在 {max_retries} 次嘗試後仍無法獲取 PHPSESSID")
            
    def get_schedule(self, year, month, start_date, end_date, venue_sn="302"):
        """獲取球場時間表"""
        if not self.phpsessid:
            self.get_phpsessid()
            
        session = requests.Session()
        session.cookies.update({"PHPSESSID": self.phpsessid})
        
        data = {
            "FUNC": "LoadSched",
            "SY": str(year),
            "SM": str(month),
            "RSD": start_date,
            "RED": end_date,
            "VenueSN": venue_sn,
            "OrderNo": ""
        }
        
        print(f"正在查詢 {start_date} 到 {end_date} 的場地時間...")
        response = session.post(self.base_url, headers=self.headers, data=data)
        
        if response.status_code != 200:
            raise Exception(f"API 請求失敗，狀態碼: {response.status_code}")
            
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print("API 回應不是 JSON 格式")
            print("回應內容:", response.text[:500])
            raise
            
    def process_schedule_data(self, data):
        """處理並儲存時間表資料"""
        if not data or "DATA" not in data:
            raise Exception("回應資料格式錯誤")
            
        # 轉換資料為 DataFrame
        schedule_data = []
        for date, slots in data["DATA"].items():
            for time_slot, courts in slots.items():
                row = {
                    "日期": date,
                    "時段": time_slot
                }
                # 處理每個場地的狀態
                for court_num, status in courts.items():
                    row[f"場地{court_num}"] = "可預約" if status == "1" else "已預約"
                schedule_data.append(row)
                
        if not schedule_data:
            print("沒有找到任何場地資料")
            return
            
        df = pd.DataFrame(schedule_data)
        
        # 確保輸出目錄存在
        os.makedirs("data", exist_ok=True)
        
        # 儲存為 CSV
        output_file = os.path.join("data", f"球場時間表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 已將場地資料儲存至: {output_file}")
        print(f"共 {len(schedule_data)} 筆資料")
        
        return df

def main():
    scraper = CourtScheduleScraper()
    
    # 設定查詢時間範圍（可依需求修改）
    year = datetime.now().year
    month = datetime.now().month
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month+1 if month < 12 else 1:02d}-01"
    
    try:
        data = scraper.get_schedule(year, month, start_date, end_date)
        scraper.process_schedule_data(data)
    except Exception as e:
        print(f"執行過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()
