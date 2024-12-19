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

        print(f"Searching for zip files in: {DOWNLOADS_FOLDER}")
        
        # Wait a bit for the download to complete and file to be visible
        time.sleep(5)
        
        # List all files in downloads directory
        downloads_path = pathlib.Path(DOWNLOADS_FOLDER)
        all_files = list(downloads_path.glob("*.zip"))
        
        print(f"Found {len(all_files)} zip files")
        for file in all_files:
            print(f"Found file: {file}")
        
        # Filter for midjourney files
        midjourney_files = [p for p in all_files if "midjourney_session" in p.name]
        print(f"Found {len(midjourney_files)} midjourney zip files")
        
        if not midjourney_files:
            raise Exception(f"No midjourney zip files found in {DOWNLOADS_FOLDER}")
            
        zip_file_path = max(midjourney_files, key=os.path.getctime)
        print(f"Selected zip file: {zip_file_path}")
        
        extracted_folder_path = os.path.join(BASE_OUTPUT_FOLDER, raw_folder_name)
        if not os.path.exists(extracted_folder_path):
            os.makedirs(extracted_folder_path)
        
        print(f"Extracting to: {extracted_folder_path}")
        shutil.unpack_archive(zip_file_path, extracted_folder_path)
        
        # Delete the zip file and confirm
        print(f"Deleting zip file: {zip_file_path}")
        os.remove(zip_file_path)
        print("✅ Zip file deleted successfully")

        return extracted_folder_path

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise 