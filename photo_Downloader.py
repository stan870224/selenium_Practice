import os
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys('\n')
    time.sleep(5)
    print("登入成功")

def is_private_account(driver):
    page_source = driver.page_source

    if "很抱歉，此頁面無法使用。" in page_source:
        print("查無帳號")
        return "not_exist"

    if "此帳號不公開" in page_source:
        print("該帳號為私人帳號")
        return "private"

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href,"/p/")]'))
        )
        print("帳號為公開帳號，含有貼文")
        return "public"
    except:
        print("帳號沒有找到貼文或載入異常")
        return "unknown"

def get_latest_post_links(driver, target_user, num_posts):
    driver.get(f'https://www.instagram.com/{target_user}/')
    time.sleep(5)
    
    post_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while len(post_links) < num_posts * 2:  # 多抓一些以免影片被跳過
        a_tags = driver.find_elements(By.XPATH, '//a[contains(@href,"/p/")]')
        for a in a_tags:
            href = a.get_attribute('href')
            if href and href not in post_links:
                post_links.add(href)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    return list(post_links)

def is_post_image(driver):
    return not bool(driver.find_elements(By.TAG_NAME, 'video'))

def extract_images(driver):
    image_urls = set()
    imgs = driver.find_elements(By.TAG_NAME, 'img')
    for img in imgs:
        src = img.get_attribute('src')
        if src and src not in image_urls:
            image_urls.add(src)
    return list(image_urls)

def download_post_images(driver, post_url, download_folder):
    driver.get(post_url)
    time.sleep(3)
    os.makedirs(download_folder, exist_ok=True)
    
    if not is_post_image(driver):
        print(f"跳過影片：{post_url}")
        return False

    image_urls = extract_images(driver)
    for idx, url in enumerate(image_urls):
        filepath = os.path.join(download_folder, f'image_{idx+1}.jpg')
        if not os.path.exists(filepath):
            response = requests.get(url, stream=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"下載圖片 {idx+1}")
    
    return len(image_urls) > 0
