from selenium import webdriver
from bs4 import BeautifulSoup

def fetch_otp_with_selenium(verify_link):
   
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-webgl")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-features=NetworkService,NetworkServiceInProcess")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.javascript": 2,
            "profile.managed_default_content_settings.notifications": 2,
            "profile.managed_default_content_settings.popups": 2, 
            "profile.managed_default_content_settings.background_sync": 2,
            "profile.managed_default_content_settings.media_stream": 2, 
            "profile.managed_default_content_settings.media_stream_mic": 2,
            "profile.managed_default_content_settings.media_stream_camera": 2,
            "profile.managed_default_content_settings.geolocation": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(verify_link)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        otp = soup.find("div", {"data-uia": "travel-verification-otp"}).get_text(strip=True)
        print("OTP Code:", otp)
        driver.quit()
        return  otp
