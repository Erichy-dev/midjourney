from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from config.settings import ORGANIZE_PAGE_URL

def ensure_on_organize_page(driver):
    """Ensures the browser is on the MidJourney organize page."""
    try:
        print("Navigating to the Organize page...")
        driver.get(ORGANIZE_PAGE_URL)
        
        # Always refresh and check for verification
        driver.refresh()
        time.sleep(5)
        
        if is_verification_page(driver):
            print("\n⚠️ Verification page detected!")
            print("\nPlease follow these steps:")
            print("1. Open a new tab with this URL:", ORGANIZE_PAGE_URL)
            print("2. Close this current tab")
            print("3. Complete any verification if needed")
            print("\nPress Enter when you're done and on the organize page...")
            input()
            
            # After user confirmation, verify we're on the organize page
            driver.get(ORGANIZE_PAGE_URL)
            
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
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
