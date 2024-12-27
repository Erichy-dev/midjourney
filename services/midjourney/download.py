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
        i = 0
        for i in range(4):
            images = driver.select_all("img")[:4]
            images[i].click()
            time.sleep(3)
            download_button = driver.wait_for_element('button[title="Download Image"]')
            download_button.click()
            time.sleep(3)
            exit_button = driver.wait_for_element('button[title="Close"]')
            exit_button.click()
            driver.google_get("https://www.midjourney.com/archive", bypass_cloudflare=True)

        time.sleep(10)

        print(f"Searching for latest downloaded images in: {DOWNLOADS_FOLDER}")
        
        # Wait a bit for downloads to complete
        time.sleep(5)
        
        # Get all image files from downloads folder
        downloads_path = pathlib.Path(DOWNLOADS_FOLDER)
        image_files = list(downloads_path.glob("*.png"))  # Assuming PNG format, adjust if needed
        
        if not image_files:
            raise Exception(f"No downloaded images found in {DOWNLOADS_FOLDER}")
            
        # Sort by creation time to get the 4 most recent images
        latest_images = sorted(image_files, key=os.path.getctime, reverse=True)[:4]
        print(f"Found {len(latest_images)} recent images")
        
        # Move images directly to BASE_OUTPUT_FOLDER (Raw Folders)
        for img_path in latest_images:
            dest_path = os.path.join(BASE_OUTPUT_FOLDER, img_path.name)
            shutil.move(str(img_path), dest_path)
            print(f"Moved: {img_path.name}")
        
        return BASE_OUTPUT_FOLDER

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise 
    