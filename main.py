import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from photo_Downloader import instagram_login, is_private_account, download_post_images, get_latest_post_links
import time

# 讀取 IG 帳號設定
with open('config.json', 'r') as f:
    config = json.load(f)

username = config['username']
password = config['password']

# 設定 Chrome 無頭模式
chrome_options = Options()
#chrome_options.add_argument("--headless")
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--window-size=1920,1080")
#chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=chrome_options)

# 先登入 Instagram
instagram_login(driver, username, password)

# 輸入目標帳號
target_user = input("請輸入要查詢的帳號: ").strip()
if not target_user:
    print("未輸入帳號，程式結束")
    driver.quit()
    exit()

# 進入指定帳號頁面檢查
driver.get(f"https://www.instagram.com/{target_user}/")
time.sleep(5)

try:
    driver.find_element(By.XPATH, "//h2[contains(text(), '查無此頁')]")
    print("查無帳號，程式結束")
    driver.quit()
    exit()
except:
    print(f"帳號 {target_user} 存在，繼續檢查...")

status = is_private_account(driver)
if status == "not_exist":
    print("查無帳號，程式結束")
    driver.quit()
    exit()
elif status == "private":
    print("帳號為私人帳號，無法存取，程式結束")
    driver.quit()
    exit()
elif status == "public":
    print("帳號為公開帳號，繼續執行")
else:
    print("帳號狀態未知，程式結束")
    driver.quit()
    exit()


num_posts = int(input("輸入要下載幾篇圖片貼文："))

# 獲取貼文連結
all_links = get_latest_post_links(driver, target_user, num_posts)
print(f"找到至少 {len(all_links)} 篇貼文，開始檢查...")

# 開始下載
downloaded_count = 0
for idx, post_url in enumerate(all_links):
    print(f"檢查第 {idx+1} 篇：{post_url}")
    if download_post_images(driver, post_url, f"downloads/{target_user}_post{downloaded_count+1}"):
        downloaded_count += 1
    else:
        print("該貼文跳過")
    if downloaded_count >= num_posts:
        break

print(f"下載完成，共下載 {downloaded_count} 篇圖片貼文")
driver.quit()
