#!/usr/bin/env python3
import os, time, random, datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Pastikan folder logs ada
def ensure_log_dir():
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

# Logging helper def
def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# Mobile user agents only
def random_user_agent():
    return random.choice([
        "Mozilla/5.0 (Linux; Android 10; SM-G975F)... Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)... Mobile/15E148 Safari/604.1"
    ])

# Cek IP via plain HTTP endpoint
def get_current_ip(driver):
    try:
        driver.get("http://ipv4.icanhazip.com")
        time.sleep(random.uniform(1,2))
        return driver.find_element(By.TAG_NAME, 'body').text.strip()
    except Exception as e:
        log(f"[WARN] IP check failed: {e}")
        return "Unknown"

# Inisialisasi browser
def create_driver(proxy_url):
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--window-size=360,640")
    opts.add_argument(f"--proxy-server={proxy_url}")
    opts.add_argument(f"user-agent={random_user_agent()}")
    
    service = Service(executable_path=os.getenv("CHROMEDRIVER_PATH"))
    driver = webdriver.Chrome(service=service, options=opts)

    # Throttle jaringan
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
            'offline': False,
            'latency': 200,
            'downloadThroughput': 200*1024/8,
            'uploadThroughput': 100*1024/8
        })
    except Exception as e:
        log(f"[WARN] Network emulation failed: {e}")

    return driver

# Simpan screenshot jika kondisi terpenuhi
def maybe_screenshot(driver, log_dir, prefix):
    if random.random() < 0.2:  # 20% chance setiap loop
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(log_dir, f"{prefix}_{ts}.png")
        try:
            driver.save_screenshot(filename)
            log(f"Saved screenshot: {filename}")
        except Exception as e:
            log(f"[WARN] Screenshot failed: {e}")

# Main
 def main():
    raw_proxy = os.getenv("PROXY_URL")
    video_id  = os.getenv("VIDEO_ID")
    iters     = int(os.getenv("ITERATIONS", os.getenv("REPLICAS", "1")))

    if not raw_proxy or not video_id:
        raise RuntimeError("PROXY_URL and VIDEO_ID must be set")

    log_dir = ensure_log_dir()

    for i in range(1, iters+1):
        # Delay acak
        delay0 = random.uniform(0, 20)
        log(f"Initial delay before session {i}: {delay0:.1f}s")
        time.sleep(delay0)

        # Session suffix
        from urllib.parse import urlparse
        p = urlparse(raw_proxy)
        suffix = random.randint(100000,999999)
        proxy_url = raw_proxy.replace(p.username, f"{p.username}-sess{suffix}")

        # Start WebDriver
        try:
            driver = create_driver(proxy_url)
        except Exception as e:
            log(f"[ERROR] WebDriver init failed (sess{suffix}): {e}")
            continue

        ip = get_current_ip(driver)
        prefix = f"{video_id}_sess{suffix}_ip{ip.replace('.', '_')}"
        log(f"START watching {video_id} (sess{suffix}), IP={ip}")

        # Putar video
        driver.get(f"https://www.youtube.com/watch?v={video_id}&autoplay=1&mute=1")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
        except TimeoutException:
            log("[WARN] <video> load timeout; continuing anyway")

        log("Watching…")
        watch_time = random.uniform(30, 150)
        end_ts = time.time() + watch_time
        while time.time() < end_ts:
            maybe_screenshot(driver, log_dir, prefix)
            time.sleep(5)

        log(f"END watching {video_id} (sess{suffix})")
        driver.quit()

        if i < iters:
            pause = random.uniform(5, 15)
            log(f"Sleeping {pause:.1f}s before next iteration")
            time.sleep(pause)

if __name__ == "__main__":
    main()
