import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_court_status():
    url = 'https://vbs.sports.taipei/venues/?K=305#Schedule'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 不開啟瀏覽器
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(5)

    # 點擊「古亭河濱公園網球場」
    target_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, '古亭河濱公園網球場'))
    )
    target_tab.click()
    time.sleep(3)

    # 解析租借狀態表格
    schedule_table = driver.find_element(By.CLASS_NAME, 'timetable')
    rows = schedule_table.find_elements(By.TAG_NAME, 'tr')

    court_data = []
    for row in rows[1:]:
        cols = row.find_elements(By.TAG_NAME, 'td')
        time_slot = cols[0].text.strip()
        status = [col.text.strip() for col in cols[1:]]
        court_data.append([time_slot] + status)

    driver.quit()

    df = pd.DataFrame(court_data, columns=['時段', '場地1', '場地2', '場地3', '場地4'])
    df.to_csv('古亭河濱公園_網球場租借狀態.csv', index=False, encoding='utf-8-sig')

    print("✅ 已儲存為 '古亭河濱公園_網球場租借狀態.csv'")

if __name__ == '__main__':
    scrape_court_status()
