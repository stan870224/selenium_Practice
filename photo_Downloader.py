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
    try:
        # 嘗試等待有貼文連結載入
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//article//a')))
        print("帳號為公開帳號，含有貼文")
        return False
    except:
        # 若沒找到貼文，再確認是否為私人帳號
        try:
            driver.find_element(By.XPATH, "//*[contains(text(), '私人帳號')]")
            print("該帳號為私人帳號")
        except:
            print("帳號沒有找到貼文或載入異常")
        return True

def get_all_post_links(driver, target_user, min_posts):
    driver.get(f'https://www.instagram.com/{target_user}/')
    time.sleep(5)

    post_links = set()
    while len(post_links) < min_posts * 2:  # 多抓一些保險
        posts = driver.find_elements(By.XPATH, '//article//a')
        for post in posts:
            link = post.get_attribute('href')
            if link:
                post_links.add(link)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    return list(post_links)

def is_post_image(driver):
    try:
        driver.find_element(By.TAG_NAME, 'video')
        return False
    except:
        return True

def extract_image_urls(driver):
    image_urls = set()
    images = driver.find_elements(By.TAG_NAME, 'img')
    for img in images:
        src = img.get_attribute('src')
        if src:
            image_urls.add(src)
    
    divs = driver.find_elements(By.CSS_SELECTOR, 'div[style*="background-image"]')
    for div in divs:
        style = div.get_attribute('style')
        start = style.find('url("') + 5
        end = style.find('")')
        if start > 4 and end > start:
            url = style[start:end]
            image_urls.add(url)
    
    return list(image_urls)

def download_post_images(driver, post_url, download_folder):
    driver.get(post_url)
    time.sleep(3)
    os.makedirs(download_folder, exist_ok=True)
    
    if not is_post_image(driver):
        print("該貼文為影片，跳過")
        return False

    downloaded = 0
    while True:
        urls = extract_image_urls(driver)
        for idx, url in enumerate(urls):
            filepath = os.path.join(download_folder, f'image_{downloaded+1}.jpg')
            if not os.path.exists(filepath):
                response = requests.get(url, stream=True)
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                print(f"下載圖片 {downloaded+1}")
                downloaded += 1
        
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="下一步"]')
            ActionChains(driver).move_to_element(next_button).click().perform()
            time.sleep(2)
        except:
            break
    
    return downloaded > 0
