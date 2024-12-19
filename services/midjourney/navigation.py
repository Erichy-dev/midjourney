from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from config.settings import ORGANIZE_PAGE_URL

def ensure_on_organize_page(driver):
    """Ensures the browser is on the MidJourney organize page."""
    try:
        if "archive" not in driver.current_url.lower():
            print("Navigating to the Organize page...")
            driver.get(ORGANIZE_PAGE_URL)
            driver.refresh()
            time.sleep(5)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            
            # Final confirmation after refresh
            print("\n🔍 Please verify:")
            print("1. You can see the browser window")
            print("2. You're logged into MidJourney")
            print("3. You're on the archive page")
            print("\nPress Enter to begin processing, or Ctrl+C to exit...")
            input()
            
        if is_verification_page(driver):
            input("Please complete the verification and press Enter to continue...")
        print("Successfully navigated to the Organize page.")

    except Exception as e:
        logging.error(f"Error navigating to the Organize page: {e}")
        raise

def is_verification_page(driver):
    """Checks if the current page is a verification page."""
    try:
        verification_elements = [
            (By.XPATH, "//p[@id='TBuuD2' and contains(text(), 'Verify you are human by completing the action below.')]"),
            (By.XPATH, "//span[contains(@class, 'cb-lb-t') and contains(text(), 'Verify you are human')]"),
            (By.XPATH, "//iframe[contains(@src, 'captcha')]"),
            (By.XPATH, "//div[contains(@class, 'verification')]"),
            (By.XPATH, "//div[contains(text(), 'Verify you are human')]"),
            (By.XPATH, "//div[contains(text(), 'human verification')]")
        ]
        for by, value in verification_elements:
            if driver.find_elements(by, value):
                logging.info("Verification page detected.")
                return True
        return False
    except Exception as e:
        logging.error(f"Error checking for verification page: {e}")
        return False
