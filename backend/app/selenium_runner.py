from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from app import settings
from app.utils import get_user_agent


def run_selenium():
    # Start virtual display
    display = Display(visible=0, size=settings.WINDOW_SIZE, backend="xvfb")
    display.start()
    print("✅ Virtual display started")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument(f"--window-size={settings.WINDOW_SIZE[0]},{settings.WINDOW_SIZE[1]}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # User-Agent
    user_agent = get_user_agent()
    chrome_options.add_argument(f"user-agent={user_agent}")

    # Proxy
    seleniumwire_options = {
        'proxy': {
            'http': f'https://{settings.PROXY_USER}:{settings.PROXY_PASS}@{settings.PROXY_HOST}:{settings.PROXY_PORT}',
            'https': f'https://{settings.PROXY_USER}:{settings.PROXY_PASS}@{settings.PROXY_HOST}:{settings.PROXY_PORT}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }

    service = ChromeService(executable_path=settings.CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)

    try:
        # Anti-bot tweaks
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                Object.defineProperty(navigator, 'language', { get: () => 'en-US' });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                window.screen = {width:1920, height:1080};
            """
        })

        driver.get("https://www.google.com")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("python selenium")
        search_box.submit()

        # driver.save_screenshot("debug.png")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3")))

        title = driver.title
    finally:
        driver.quit()
        display.stop()
        print("✅ Browser & display stopped")

    return title
