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
            # Store the current URL
            current_url = driver.current_url
            # Open new tab
            driver.execute_script("window.open(arguments[0], '_blank');", current_url)
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            # Close the old tab
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            # Switch back to our new tab
            driver.switch_to.window(driver.window_handles[0])
            
            print("\n✨ Opened a new tab.")
            print("Please:")
            print("1. Complete the verification if needed")
            print("\nPress Enter when everything looks normal...")
            input()
            
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
