import os
import requests
from datetime import datetime, timedelta
import pandas as pd

class CourtScheduleScraper:
    def __init__(self, phpsessid):
        self.base_url = "https://vbs.sports.taipei/_/x/xhrworkv3.php"
        self.phpsessid = phpsessid
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://vbs.sports.taipei/venues/?K=305",
            "Origin": "https://vbs.sports.taipei"
        }
        
    # def get_phpsessid(self):
    #     """使用 Selenium 獲取 PHPSESSID"""
    #     print("開始獲取 PHPSESSID...")
    #     options = webdriver.ChromeOptions()
        
    #     # 基本設定
    #     options.add_argument("--headless")
    #     options.add_argument("--no-sandbox")
    #     options.add_argument("--disable-dev-shm-usage")
        
    #     # 提高穩定性的設定
    #     options.add_argument("--disable-gpu")
    #     options.add_argument("--disable-software-rasterizer")
    #     options.add_argument("--disable-infobars")
    #     options.add_argument("--window-size=1920,1080")
    #     options.add_argument("--lang=zh-TW")
        
    #     # 防止檢測的設定
    #     options.add_argument("--disable-blink-features=AutomationControlled")
    #     options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #     options.add_experimental_option("useAutomationExtension", False)
        
    #     # 使用 Selenium Grid
    #     selenium_url = os.getenv("SELENIUM_REMOTE_URL", "http://chrome:4444/wd/hub")
    #     max_retries = 3
    #     retry_count = 0
        
    #     while retry_count < max_retries:
    #         try:
    #             print(f"嘗試連接 Selenium Grid (嘗試 {retry_count + 1}/{max_retries})...")
    #             driver = webdriver.Remote(
    #                 command_executor=selenium_url,
    #                 options=options
    #             )
                
    #             print("正在載入網頁...")
    #             driver.get("https://vbs.sports.taipei")
                
    #             # 等待 reCAPTCHA 元素出現
    #             print("等待頁面載入完成...")
    #             WebDriverWait(driver, 30).until(
    #                 EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
    #             )
                
    #             # 等待 reCAPTCHA 自動驗證
    #             print("等待 reCAPTCHA 驗證（8秒）...")
    #             time.sleep(8)
                
    #             # 再次嘗試載入頁面確認驗證已通過
    #             driver.get("https://vbs.sports.taipei")
    #             time.sleep(2)
                
    #             # 獲取 cookies
    #             cookies = driver.get_cookies()
    #             for cookie in cookies:
    #                 if cookie["name"] == "PHPSESSID":
    #                     self.phpsessid = cookie["value"]
    #                     print("✅ 成功獲取 PHPSESSID")
    #                     driver.quit()
    #                     return
                        
    #             print("未找到 PHPSESSID，將重試...")
    #             retry_count += 1
                
    #         except Exception as e:
    #             print(f"發生錯誤: {str(e)}")
    #             retry_count += 1
    #             if retry_count < max_retries:
    #                 print(f"將在 5 秒後重試...")
    #                 time.sleep(5)
    #         finally:
    #             try:
    #                 if driver:
    #                     driver.quit()
    #             except Exception:
    #                 pass
        
    #     raise Exception(f"在 {max_retries} 次嘗試後仍無法獲取 PHPSESSID")
            
    def get_schedule(self, year, month, start_date, end_date, venue_sn="302"):
        """獲取球場時間表"""
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
        
        response = session.post(self.base_url, headers=self.headers, data=data)
        response.raise_for_status()
        return response.json()
            
    def process_schedule_data(self, data):
        """處理並儲存時間表資料"""
        schedule_data = []
        
        source_data = data.get("DATA", data)
        for date, slots in source_data.items():
            if not isinstance(slots, dict):
                continue
                
            for time_slot, courts in slots.items():
                if not isinstance(courts, dict):
                    continue
                    
                row = {
                    "日期": date,
                    "時段": time_slot
                }
                for court_num, status in courts.items():
                    row[f"場地{court_num}"] = "可預約" if str(status) == "1" else "已預約"
                schedule_data.append(row)
                    
        df = pd.DataFrame(schedule_data)
        
        # 確保輸出目錄存在
        os.makedirs("data", exist_ok=True)
        
        # 儲存為 CSV
        output_file = os.path.join("data", f"球場時間表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        return df

def main():
    phpsessid = "v2q26doqmm926b3tsm2hd8og23"
    scraper = CourtScheduleScraper(phpsessid)
    
    today = datetime.now()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    year = today.year
    month = today.month
    
    try:
        data = scraper.get_schedule(year, month, start_date, end_date)
        scraper.process_schedule_data(data)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
