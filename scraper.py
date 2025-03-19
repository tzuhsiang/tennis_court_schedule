import os
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import pandas as pd

def get_random_delay():
    return random.uniform(2, 5)

def scrape_court_status():
    url = 'https://vbs.sports.taipei/venues/?K=305#Schedule'
    
    # 使用 undetected-chromedriver
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')
    
    # 使用隨機 user agent
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')
    
    # 添加其他反檢測選項
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    
    print(f"使用 User Agent: {user_agent}")
    
    try:
        driver = uc.Chrome(
            options=options,
            driver_executable_path="/usr/bin/chromedriver",
            browser_executable_path="/usr/bin/chromium"
        )
        
        # 訪問網頁
        print(f"開始訪問網頁: {url}")
        driver.get(url)
        
        # 等待並添加一些隨機延遲
        print("等待頁面載入...")
        time.sleep(get_random_delay())
        
        # 模擬真實用戶行為
        scroll_height = random.randint(300, 700)
        driver.execute_script(f"window.scrollTo(0, {scroll_height})")
        time.sleep(get_random_delay())
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(get_random_delay())
        
        print(f"目前頁面標題: {driver.title}")
        print(f"目前頁面 URL: {driver.current_url}")
        
        # 等待表格元素出現
        print("尋找場地狀態表格...")
        try:
            table = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'timetable'))
            )
            print("✅ 找到表格元素")
            
            # 截圖以便偵錯
            driver.save_screenshot('/app/data/page.png')
            print("✅ 已儲存頁面截圖")
            
        except Exception as e:
            print(f"❌ 等待表格元素時發生錯誤: {str(e)}")
            if driver.page_source:
                with open('/app/data/error_page.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("已儲存錯誤頁面原始碼")
            driver.save_screenshot('/app/data/error_page.png')
            print("已儲存錯誤頁面截圖")
            raise
        
        # 解析租借狀態表格
        rows = table.find_elements(By.TAG_NAME, 'tr')
        print(f"找到 {len(rows)} 行資料")
        
        court_data = []
        for row in rows[1:]:  # 跳過表頭
            time.sleep(0.1)  # 小延遲避免過快
            cols = row.find_elements(By.TAG_NAME, 'td')
            if cols:
                time_slot = cols[0].text.strip()
                status = [col.text.strip() for col in cols[1:]]
                court_data.append([time_slot] + status)
        
        # 儲存資料
        if court_data:
            df = pd.DataFrame(court_data, columns=['時段', '場地1', '場地2', '場地3', '場地4'])
            output_file = '/app/data/古亭河濱公園_網球場租借狀態.csv'
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"✅ 已儲存場地狀態資料至 {output_file}")
            print(f"共 {len(court_data)} 筆資料")
        else:
            print("❌ 未找到場地狀態資料")
            
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        if driver:
            driver.save_screenshot('/app/data/error.png')
            print("已儲存錯誤截圖")
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    scrape_court_status()
