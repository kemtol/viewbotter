import os
import time
import json
import random
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def get_video_title(driver):
    # Setelah halaman load, ambil title
    try:
        return driver.title
    except:
        return "Unknown Title"

def get_current_ip(driver):
    driver.get("https://httpbin.org/ip")
    time.sleep(random.uniform(2, 4))
    body = driver.find_element(By.TAG_NAME, "body").text
    try:
        data = json.loads(body)
        return data.get("origin", body)
    except:
        return body

# ————— Helper functions ——————
def random_user_agent():
    uas = [
        # Desktop
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)…",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)…",
        # Mobile
        "Mozilla/5.0 (Linux; Android 10; SM-G975F)…",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)…"
    ]
    return random.choice(uas)

def get_current_ip(driver):
    driver.get("https://httpbin.org/ip")
    time.sleep(random.uniform(2, 4))
    body = driver.find_element(By.TAG_NAME, "body").text
    try:
        data = json.loads(body)
        return data.get("origin", body)
    except:
        return body

def random_scroll(driver, height):
    for _ in range(random.randint(2, 5)):
        px = random.randint(int(height/3), height)
        driver.execute_script(f"window.scrollBy(0, {px});")
        time.sleep(random.uniform(2, 6))

def random_pause_resume(driver):
    videos = driver.find_elements(By.TAG_NAME, "video")
    if videos and random.random() < 0.5:
        try:
            driver.execute_script("arguments[0].pause();", videos[0])
            time.sleep(random.uniform(1, 3))
            driver.execute_script("arguments[0].play();", videos[0])
        except Exception as e:
            log(f"pause/play error: {e}")

def random_click_related(driver):
    if random.random() < 0.3:
        elems = driver.find_elements(By.CSS_SELECTOR, "ytd-compact-video-renderer a#thumbnail")
        if elems:
            choice = random.choice(elems[:5])
            driver.execute_script("arguments[0].scrollIntoView();", choice)
            time.sleep(random.uniform(1,2))
            choice.click()
            time.sleep(random.uniform(3, 7))
            return True
    return False

# ————— Main ——————
proxy      = os.getenv("PROXY_URL")
video      = os.getenv("VIDEO_ID")
iterations = int(os.getenv("ITERATIONS", "1"))

proxy      = os.getenv("PROXY_URL")
video      = os.getenv("VIDEO_ID")
iterations = int(os.getenv("ITERATIONS", "1"))

for i in range(1, iterations+1):
    # — setup resolution
    vq = random.choice(["medium","large"])
    width, height = (640,360) if vq=="medium" else (854,480)
    # — setup Chrome
    options = Options()
    options.binary_location = os.environ.get("CHROME_BIN")
    options.add_argument("--headless")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument(f"--proxy-server={proxy}")
    options.add_argument(f"user-agent={random_user_agent()}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    driver  = webdriver.Chrome(service=service, options=options)

    # — UPDATED LOG FORMAT —  
    ip = get_current_ip(driver)
    log(f"START watching {video} @ quality={vq}")
    title = get_video_title(driver) or video
    # asumsi mobile phone jika UA mengandung Android atau iPhone
    device = "mobile phone" if "Android" in driver.execute_script("return navigator.userAgent") or "iPhone" in driver.execute_script("return navigator.userAgent") else "desktop"
    log(f"Watching {title} with {device} at {height}p resolution")
    log(f"From US using IP {ip}.")

    # — play video
    url = f"https://www.youtube.com/watch?v={video}&vq={vq}&autoplay=1&mute=1"
    driver.get(url)
    time.sleep(random.uniform(2,5))
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button.ytp-large-play-button")
        btn.click()
        time.sleep(random.uniform(1,3))
    except:
        pass

    # — interactions & watch loop
    random_scroll(driver, height)
    random_pause_resume(driver)
    watch_time = random.uniform(30,150)
    end_time   = time.time() + watch_time
    while time.time() < end_time:
        if random.random()<0.3: random_scroll(driver, height)
        if random.random()<0.2: random_pause_resume(driver)
        time.sleep(random.uniform(5,10))

    # — akhir sesi
    log(f"END watching {video}")
    driver.quit()

    if i < iterations:
        pause = random.uniform(5,15)
        log(f"Sleeping {pause:.1f}s before next rotation…")
        time.sleep(pause)
