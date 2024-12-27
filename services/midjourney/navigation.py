import time
import logging
from config.settings import ORGANIZE_PAGE_URL
import sys
from botasaurus.browser import browser, Driver 

def ensure_on_organize_page(driver: Driver):
    """Ensures the browser is on the MidJourney organize page."""
    try:
        print("Navigating to the Organize page...")
        driver.google_get(ORGANIZE_PAGE_URL, bypass_cloudflare=True)
        time.sleep(5)
        
        driver.wait_for_element("textarea")
        print("Successfully navigated to the Organize page.")
        return True  # Return a serializable value

    except Exception as e:
        logging.error(f"Error navigating to the Organize page: {e}")
        raise

