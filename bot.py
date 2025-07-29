#!/usr/bin/env python3
import os, time, json, random, datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def random_user_agent():
    # Hanya UA mobile
    return random.choice([
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.5845.141 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ])

def get_current_ip(driver):
    driver.get("http://api.ipify.org?format=json")
    time.sleep(random.uniform(1, 2))
    body = driver.find_element(By.TAG_NAME, "body").text
    try:
        return json.loads(body)["ip"]
    except:
        return body

def create_driver(proxy_url):
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--window-size=360,640")  # mobile size
    opts.add_argument(f"--proxy-server={proxy_url}")
    opts.add_argument(f"user-agent={random_user_agent()}")

    service = Service(os.getenv("CHROMEDRIVER_PATH"))
    driver = webdriver.Chrome(service=service, options=opts)

    # Throttle jaringan (mobile-like)
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
            "offline": False,
            "latency": 200,                   # ms
            "downloadThroughput": 200*1024/8, # ~200kb/s
            "uploadThroughput": 100*1024/8    # ~100kb/s
        })
    except Exception as e:
        log(f"[WARN] Network emulation failed: {e}")

    return driver

def main():
    raw_proxy = os.getenv("PROXY_URL")  # e.g. http://user:pass@host:port
    video_id  = os.getenv("VIDEO_ID")
    iters     = int(os.getenv("ITERATIONS", os.getenv("REPLICAS", "1")))

    if not raw_proxy or not video_id:
        raise RuntimeError("PROXY_URL and VIDEO_ID must be set")

    for i in range(1, iters+1):
        # acak delay awal agar IP tidak sama
        delay0 = random.uniform(0, 20)
        log(f"Initial delay before session {i}: {delay0:.1f}s")
        time.sleep(delay0)

        # tambahkan session suffix untuk rotasi IP
        session_id = random.randint(100000, 999999)
        p = urlparse(raw_proxy)
        user = p.username
        host_str = raw_proxy.replace(user, f"{user}-sess{session_id}")
        driver = None
        try:
            driver = create_driver(host_str)
        except Exception as e:
            log(f"[ERROR] WebDriver init failed (sess{session_id}): {e}")
            continue

        ip = get_current_ip(driver)
        log(f"START watching {video_id} (sess{session_id}), IP={ip}")

        # load video
        url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1&mute=1"
        driver.get(url)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
        except TimeoutException:
            log("[WARN] <video> load timeout")

        log("Watching…")
        # durasi nonton
        watch_time = random.uniform(30, 150)
        end_ts = time.time() + watch_time
        while time.time() < end_ts:
            time.sleep(5)  # atau tambahkan scroll/pause simulasi seperti sebelum

        log(f"END watching {video_id} (sess{session_id})")
        driver.quit()

        if i < iters:
            pause = random.uniform(5, 15)
            log(f"Sleeping {pause:.1f}s before next iter")
            time.sleep(pause)

if __name__ == "__main__":
    main()
