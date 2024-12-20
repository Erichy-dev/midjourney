from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging
import os
import shutil
import pathlib
from config.settings import BASE_OUTPUT_FOLDER, DOWNLOADS_FOLDER
from .navigation import ensure_on_organize_page

def download_images(driver, raw_folder_name):
    """Downloads selected images from MidJourney."""
    print("Selecting and downloading images...")
    try:
        # Select images
        images = driver.find_elements(By.CSS_SELECTOR, "img")[:4]
        for image in images:
            ActionChains(driver).key_down(Keys.SHIFT).click(image).key_up(Keys.SHIFT).perform()

        # Find and click download button
        download_button = None
        for _ in range(3):
            try:
                download_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download')]"))
                )
                download_button.click()
                time.sleep(45)
                break
            except Exception:
                ensure_on_organize_page(driver)
                images = driver.find_elements(By.CSS_SELECTOR, "img")[:4]
                for image in images:
                    ActionChains(driver).key_down(Keys.SHIFT).click(image).key_up(Keys.SHIFT).perform()

        if not download_button:
            raise Exception("Failed to locate download button after multiple attempts")

        print(f"Searching for latest Midjourney zip file in: {DOWNLOADS_FOLDER}")
        zip_files = [f for f in os.listdir(DOWNLOADS_FOLDER) 
                    if f.startswith('midjourney') and f.endswith('.zip')]
        
        if not zip_files:
            print("No Midjourney zip files found!")
            return
            
        # Wait a bit for the download to complete and file to be visible
        time.sleep(5)
        
        # Get the latest midjourney zip file
        downloads_path = pathlib.Path(DOWNLOADS_FOLDER)
        all_files = list(downloads_path.glob("midjourney_session*.zip"))
        
        if not all_files:
            raise Exception(f"No midjourney zip files found in {DOWNLOADS_FOLDER}")
            
        zip_file_path = max(all_files, key=os.path.getctime)
        print(f"Found latest zip file: {zip_file_path}")
        
        # Create and extract to destination folder
        extracted_folder_path = os.path.join(BASE_OUTPUT_FOLDER, raw_folder_name)
        os.makedirs(extracted_folder_path, exist_ok=True)
        
        print(f"Extracting to: {extracted_folder_path}")
        shutil.unpack_archive(zip_file_path, extracted_folder_path)
        
        return extracted_folder_path

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise 
    