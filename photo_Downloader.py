import os
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys('\n')
    time.sleep(5)
    print("登入成功")

def check_account_status(driver, target_user):
    driver.get(f'https://www.instagram.com/{target_user}/')
    time.sleep(3)
    page = driver.page_source
    if "很抱歉，此頁面無法使用。" in page:
        return "not_exist"
    if "此帳號不公開" in page:
        return "private"
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href,"/p/")]'))
        )
        return "public"
    except:
        return "unknown"

def get_visible_post_links(driver, target_user):
    driver.get(f'https://www.instagram.com/{target_user}/')
    time.sleep(3)
    links = []
    # ** 這裡建議嚴格比對 {target_user}/p/
    a_tags = driver.find_elements(By.XPATH, f'//a[contains(@href,"/{target_user}/p/")]')
    if not a_tags:
        a_tags = driver.find_elements(By.XPATH, '//a[contains(@href,"/p/")]')
    for a in a_tags:
        href = a.get_attribute('href')
        if href and '/p/' in href and href not in links:
            links.append(href)
    return links

def is_post_owner(driver, target_user):
    try:
        account_name = driver.find_element(By.XPATH, '//header//a').text.strip()
        return account_name == target_user
    except:
        return False

def is_photo_post(driver):
    return not bool(driver.find_elements(By.TAG_NAME, 'video'))

def safe_click(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.2)
        ActionChains(driver).move_to_element(element).perform()
        time.sleep(0.2)
        element.click()
        return True
    except Exception as e:
        print("Click failed:", e)
        return False


def download_post_images(driver, post_url, save_dir):
    driver.get(post_url)
    time.sleep(2)
    os.makedirs(save_dir, exist_ok=True)
    
    img_urls = []
    img_idx = 1
    
    while True:
        print(f"\n[LOG] ===== 進入新迴圈，已下載數: {len(img_urls)} =====")
        
        # 找到所有圖片元素
        imgs = driver.find_elements(By.CSS_SELECTOR, r"body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div.xb88tzc.xw2csxc.x1odjw0f.x5fp0pe.x1qjc9v5.xjbqb8w.x1lcm9me.x1yr5g0i.xrt01vj.x10y3i5r.xr1yuqi.xkrivgy.x4ii5y1.x1gryazu.x15h9jz8.x47corl.xh8yej3.xir0mxb.x1juhsu6 > div > article > div > div._aatk._aatl > div > div.x1lliihq.x1n2onr6 > div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x10l6tqk.x1ey2m1c.x13vifvy.x17qophe.xds687c.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1 > div > div > div > ul")
        print(f"[LOG] 這輪抓到 {len(imgs)} 個 img 元素")
        
        # 直接找第一個有效圖片
        current_src = None
        for img in imgs:
            try:
                src = img.get_attribute('src')
                if src and src.startswith('http') and img.is_displayed():
                    current_src = src
                    print(f"[LOG] 找到圖片 src = {src}")
                    break
            except Exception as e:
                print(f"[LOG] 圖片處理錯誤: {e}")
        
        # 沒抓到就跳出
        if not current_src:
            print("[LOG] 沒抓到圖片元素，結束")
            break
        
        if current_src not in img_urls:
            filepath = os.path.join(save_dir, f'image_{img_idx}.jpg')
            print(f"[LOG] 嘗試下載 {filepath}")
            try:
                with open(filepath, 'wb') as f:
                    f.write(requests.get(current_src).content)
                print(f"[LOG] 下載圖片 {img_idx}：{current_src}")
            except Exception as e:
                print(f"[LOG] 下載失敗: {e}")
            img_urls.append(current_src)
            img_idx += 1
        else:
            print("[LOG] 圖片已經下載過，略過。")
        input()
        
        # 嘗試點「下一步」按鈕
        try:
            next_btn = driver.find_element(By.XPATH, '//button[@aria-label="下一步"]')
            print("[LOG] 找到『下一步』按鈕，準備點擊。")
            next_btn.click()
            time.sleep(1.2)
        except NoSuchElementException:
            print("[LOG] 找不到『下一步』按鈕，應該已經到最後一張。")
            break
    
    print(f"[LOG] 共下載 {len(img_urls)} 張圖")
    return len(img_urls)


def download_latest_photo_posts(driver, target_user, num_posts):
    """主流程：下載最新 num_posts 篇圖片貼文"""
    downloaded = 0
    links = get_visible_post_links(driver, target_user)
    for link in links:
        if downloaded >= num_posts:
            break
        try:
            driver.get(link)
            time.sleep(1.5)
            if not is_post_owner(driver, target_user):
                continue
            if not is_photo_post(driver):
                continue
            save_dir = f"downloads/{target_user}_{downloaded+1}"
            img_count = download_post_images(driver, link, save_dir)
            if img_count > 0:
                downloaded += 1
                print(f"已下載 {downloaded} / {num_posts} 篇圖片貼文")
        except Exception as e:
            print(f"下載第 {downloaded+1} 篇時出錯: {e}")
    print(f"下載完成，共 {downloaded} 則圖片貼文")
    return downloaded
