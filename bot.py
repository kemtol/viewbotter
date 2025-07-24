#!/usr/bin/env python3
import os
import time
import json
import random
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def random_user_agent() -> str:
    uas = [
        # Desktop UAs
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        # Mobile UAs
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.5845.141 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(uas)

def get_current_ip(driver: webdriver.Chrome) -> str:
    # Gunakan api.ipify.org via HTTP, tanpa redirect ke HTTPS
    driver.get("http://api.ipify.org?format=json")
    time.sleep(random.uniform(2, 4))
    body = driver.find_element(By.TAG_NAME, "body").text
    try:
        return json.loads(body).get("ip", body)
    except json.JSONDecodeError:
        return body

def get_video_title(driver: webdriver.Chrome) -> str:
    return driver.title or "Unknown Title"

def random_scroll(driver: webdriver.Chrome, height: int):
    for _ in range(random.randint(2, 5)):
        px = random.randint(int(height/3), height)
        driver.execute_script(f"window.scrollBy(0, {px});")
        time.sleep(random.uniform(2, 6))

def random_pause_resume(driver: webdriver.Chrome):
    videos = driver.find_elements(By.TAG_NAME, "video")
    if videos and random.random() < 0.5:
        try:
            driver.execute_script("arguments[0].pause();", videos[0])
            time.sleep(random.uniform(1, 3))
            driver.execute_script("arguments[0].play();", videos[0])
        except Exception as e:
            log(f"pause/play error: {e}")

def random_click_related(driver: webdriver.Chrome) -> bool:
    if random.random() < 0.3:
        elems = driver.find_elements(By.CSS_SELECTOR, "ytd-compact-video-renderer a#thumbnail")
        if elems:
            choice = random.choice(elems[:5])
            driver.execute_script("arguments[0].scrollIntoView();", choice)
            time.sleep(random.uniform(1, 2))
            choice.click()
            time.sleep(random.uniform(3, 7))
            return True
    return False

def create_driver(proxy: str, width: int, height: int) -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument(f"--window-size={width},{height}")
    opts.add_argument(f"--proxy-server={proxy}")
    opts.add_argument(f"user-agent={random_user_agent()}")

    if os.getenv("CHROME_BIN"):
        opts.binary_location = os.getenv("CHROME_BIN")

    service = Service(executable_path=os.getenv("CHROMEDRIVER_PATH"))
    return webdriver.Chrome(service=service, options=opts)

def main():
    proxy      = os.getenv("PROXY_URL")
    video_id   = os.getenv("VIDEO_ID")
    iterations = int(os.getenv("ITERATIONS", os.getenv("REPLICAS", "1")))

    if not proxy or not video_id:
        raise RuntimeError("PROXY_URL and VIDEO_ID must be set")

    for i in range(1, iterations + 1):
        # Pilih kualitas/resolusi
        vq = random.choice(["medium", "large"])
        width, height = (640, 360) if vq == "medium" else (854, 480)

        # Inisialisasi WebDriver
        try:
            driver = create_driver(proxy, width, height)
        except Exception as e:
            log(f"Failed to start WebDriver: {e}")
            continue

        # Cek IP via proxy
        ip = get_current_ip(driver)
        log(f"START watching {video_id} @ quality={vq}")

        # Buka halaman YouTube (HTTPS) dengan autoplay & mute
        url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1&mute=1&vq={vq}"
        driver.get(url)

        # Utama: tunggu elemen judul video muncul
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "h1.title yt-formatted-string"
                ))
            )
        except TimeoutException:
            log("⚠️ Timeout waiting for video title element; will fallback to page title")

        # Fallback: tunggu page title mengandung video_id
        try:
            WebDriverWait(driver, 10).until(EC.title_contains(video_id))
        except TimeoutException:
            log("⚠️ Fallback: page title still missing video_id")

        # Ambil judul final dan device
        title = get_video_title(driver)
        ua = driver.execute_script("return navigator.userAgent")
        device = "mobile phone" if any(x in ua for x in ("Android", "iPhone")) else "desktop"

        log(f"Watching {title} with {device} at {height}p resolution")
        log(f"From US using IP {ip}")

        # Simulasi interaksi
        time.sleep(random.uniform(2, 5))
        random_scroll(driver, height)
        random_pause_resume(driver)
        random_click_related(driver)

        # Durasi tayang acak
        watch_time = random.uniform(30, 150)
        end_time   = time.time() + watch_time
        while time.time() < end_time:
            if random.random() < 0.3:
                random_scroll(driver, height)
            if random.random() < 0.2:
                random_pause_resume(driver)
            time.sleep(random.uniform(5, 10))

        log(f"END watching {video_id}")
        driver.quit()

        # Delay sebelum sesi berikutnya
        if i < iterations:
            pause = random.uniform(5, 15)
            log(f"Sleeping {pause:.1f}s before next rotation…")
            time.sleep(pause)

if __name__ == "__main__":
    main()
