import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from photo_Downloader import (
    instagram_login,
    check_account_status,
    download_latest_photo_posts
)

def main():
    # 讀取 IG 帳號設定
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    username = config['username']
    password = config['password']

    # 設定 Chrome 選項
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        instagram_login(driver, username, password)
        target_user = input("請輸入要查詢的帳號: ").strip()
        status = check_account_status(driver, target_user)
        if status != "public":
            print(f"帳號狀態: {status}，結束!")
            return
        num_posts = int(input("輸入要下載幾篇圖片貼文："))
        download_latest_photo_posts(driver, target_user, num_posts)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
