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
            
    def get_schedule(self, year, month, start_date, end_date, venue_sn="302", max_retries=3):
        """獲取球場時間表"""
        session = requests.Session()
        session.cookies.update({"PHPSESSID": "v2q26doqmm926b3tsm2hd8og23"})
        
        data = {
            "FUNC": "LoadSched",
            "SY": str(year),
            "SM": str(month),
            "RSD": start_date,
            "RED": end_date,
            "VenueSN": venue_sn,
            "OrderNo": ""
        }
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                print(f"正在查詢 {start_date} 到 {end_date} 的場地時間... (嘗試 {retry_count + 1}/{max_retries})")
                response = session.post(self.base_url, headers=self.headers, data=data)
                
                if response.status_code != 200:
                    print(f"API 請求失敗，狀態碼: {response.status_code}")
                    raise Exception(f"API 請求失敗，狀態碼: {response.status_code}")
                
                response_text = response.text.strip()
                
                # 檢查回應是否為 RT
                if response_text == 'RT':
                    print(f"收到 RT 回應 (第 {retry_count + 1} 次)，等待 5 秒後重試...")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(5)
                        continue
                    else:
                        raise Exception("多次嘗試後仍收到 RT 回應，請更新 session")
                
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    print("API 回應解析錯誤:")
                    print(f"回應內容: {response_text}")
                    print(f"回應標頭: {dict(response.headers)}")
                    raise Exception("API 回應格式錯誤，無法解析為 JSON")
                    
            except Exception as e:
                print(f"發生錯誤: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"等待 5 秒後重試...")
                    time.sleep(5)
                else:
                    raise Exception(f"在 {max_retries} 次嘗試後仍無法獲取資料: {str(e)}")
            
    def process_schedule_data(self, data):
        """處理並儲存時間表資料"""
        print("開始處理回應資料...")
        print(f"收到的資料: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if not data:
            raise Exception("收到空的回應資料")
            
        # 檢查資料結構
        if isinstance(data, dict):
            if "DATA" not in data:
                print("警告: 回應中沒有 'DATA' 欄位")
                print(f"可用的欄位: {list(data.keys())}")
        else:
            print(f"警告: 回應不是字典格式，而是 {type(data)}")
            
        # 嘗試處理不同的資料格式
        schedule_data = []
        try:
            # 如果 data 本身就是時間表資料
            if isinstance(data, dict) and any(isinstance(v, dict) for v in data.values()):
                source_data = data
            # 如果 data 包含 "DATA" 欄位
            elif isinstance(data, dict) and "DATA" in data and isinstance(data["DATA"], dict):
                source_data = data["DATA"]
            else:
                print("無法識別的資料格式，嘗試直接處理...")
                source_data = data
                
            # 處理資料
            for date, slots in source_data.items():
                if not isinstance(slots, dict):
                    print(f"跳過無效的日期資料 {date}: {slots}")
                    continue
                    
                for time_slot, courts in slots.items():
                    if not isinstance(courts, dict):
                        print(f"跳過無效的時段資料 {time_slot}: {courts}")
                        continue
                        
                    row = {
                        "日期": date,
                        "時段": time_slot
                    }
                    # 處理每個場地的狀態
                    for court_num, status in courts.items():
                        row[f"場地{court_num}"] = "可預約" if str(status) == "1" else "已預約"
                    schedule_data.append(row)
                    
        except Exception as e:
            print(f"處理資料時發生錯誤: {str(e)}")
            raise
            
        if not schedule_data:
            print("沒有找到任何場地資料")
            return
            
        print(f"成功解析 {len(schedule_data)} 筆資料")
        df = pd.DataFrame(schedule_data)
        
        # 確保輸出目錄存在
        os.makedirs("data", exist_ok=True)
        
        # 儲存為 CSV
        output_file = os.path.join("data", f"球場時間表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 已將場地資料儲存至: {output_file}")
        
        return df

def main():
    scraper = CourtScheduleScraper()
    
    # 設定查詢時間範圍（可依需求修改）
    year = datetime.now().year
    month = datetime.now().month
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month+1 if month < 12 else 1:02d}-01"
    
    try:
        print(f"開始查詢 {year}年{month}月 的場地時間...")
        data = scraper.get_schedule(year, month, start_date, end_date)
        if data:
            scraper.process_schedule_data(data)
        else:
            print("無法獲取資料，請檢查 session 是否有效")
    except Exception as e:
        print("="*50)
        print("執行過程中發生錯誤:")
        print(str(e))
        print("="*50)

if __name__ == "__main__":
    main()
