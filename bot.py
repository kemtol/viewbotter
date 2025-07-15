import os
import time
import random
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

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

def random_scroll(driver, height):
    for _ in range(random.randint(2, 5)):
        px = random.randint(int(height/3), height)
        driver.execute_script(f"window.scrollBy(0, {px});")
        time.sleep(random.uniform(2, 6))

def random_pause_resume(driver):
    # Cari elemen <video> dulu
    videos = driver.find_elements(By.TAG_NAME, "video")
    if videos and random.random() < 0.5:
        try:
            # Pause & play via JS arguments[0]
            driver.execute_script("arguments[0].pause();", videos[0])
            time.sleep(random.uniform(1, 3))
            driver.execute_script("arguments[0].play();", videos[0])
        except Exception as e:
            log(f"Pause/Resume error: {e}")

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

# —————————————— Setup & Main ——————————————

proxy = os.getenv("PROXY_URL")
video = os.getenv("VIDEO_ID")

# random resolution: medium=360p, large=480p
vq = random.choice(["medium","large"])
width, height = (640,360) if vq=="medium" else (854,480)

options = Options()
options.binary_location = os.environ.get("CHROME_BIN")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument(f"--window-size={width},{height}")
options.add_argument(f"--proxy-server={proxy}")
options.add_argument(f"user-agent={random_user_agent()}")
options.add_argument("--disable-gpu")
options.add_argument("--ignore-certificate-errors")

service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
driver = webdriver.Chrome(service=service, options=options)

# build URL with autoplay & mute
url = f"https://www.youtube.com/watch?v={video}&vq={vq}&autoplay=1&mute=1"

log(f"START watching {video} @ quality={vq}")
driver.get(url)
time.sleep(random.uniform(2, 5))

# click large play button if present
try:
    btn = driver.find_element(By.CSS_SELECTOR, "button.ytp-large-play-button")
    btn.click()
    log("Clicked large play button")
    time.sleep(random.uniform(1, 3))
except Exception:
    pass

# pre-watch interactions
random_scroll(driver, height)
random_pause_resume(driver)

# watch loop
watch_time = random.uniform(30, 150)
start = time.time()
while time.time() - start < watch_time:
    if random.random() < 0.3:
        random_scroll(driver, height)
    if random.random() < 0.2:
        random_pause_resume(driver)
    time.sleep(random.uniform(5, 10))

# optional related click
if random_click_related(driver):
    log("Clicked related video and watching briefly")
    time.sleep(random.uniform(10, 30))

log(f"END watching {video}")
driver.quit()
