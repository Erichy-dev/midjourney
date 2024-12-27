import time
import logging
import os
import shutil
import pathlib
import subprocess
from config.settings import BASE_OUTPUT_FOLDER, DOWNLOADS_FOLDER, RAW_FOLDER
import platform

def download_with_retry(url, max_retries=5):
    """Download file using curl with retries"""
    # Change to the raw folder directory
    os.chdir(RAW_FOLDER)
    
    # Set User-Agent based on platform
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        if platform.system() == "Windows"
        else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    for attempt in range(max_retries):
        try:
            command = [
                'curl',
                '-H', f'User-Agent: {user_agent}',
                '-H', 'Referer: https://www.midjourney.com/',
                '-O',
                url
            ]
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:
                print(f"Download attempt {attempt + 1} failed. Retrying...")
                time.sleep(2)
            else:
                print(f"❌ All download attempts failed for URL: {url}")
                return False

def download_images(driver, raw_folder_name):
    """Downloads selected images from MidJourney."""
    print("Selecting and downloading images...")
    try:
        # Ensure RAW_FOLDER exists
        os.makedirs(RAW_FOLDER, exist_ok=True)
        
        # Change to raw folder for downloads
        os.chdir(RAW_FOLDER)
        print(f"📂 Changed directory to: {RAW_FOLDER}")
        
        downloaded_count = 0
        max_attempts = 3
        
        while downloaded_count < 4:
            try:
                images = driver.select_all("img")[:4]
                current_image = images[downloaded_count]
                
                current_image.click()
                time.sleep(2)
                img_element = driver.wait_for_element('img[style="filter: none;"]')
                img_url = img_element.get_attribute("src")
                
                # Download image
                if download_with_retry(img_url):
                    downloaded_count += 1
                    print(f"✅ Downloaded image {downloaded_count}/4")
                else:
                    print(f"⚠️ Failed to download image {downloaded_count + 1}")
                
                exit_button = driver.wait_for_element('button[title="Close"]')
                exit_button.click()
                
            except Exception as e:
                print(f"⚠️ Error downloading image {downloaded_count + 1}: {e}")
                time.sleep(2)
            
        # Verify downloads
        files = os.listdir(RAW_FOLDER)
        image_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:
            raise Exception("No images were downloaded successfully")
            
        print(f"✅ Successfully downloaded {len(image_files)} images to {RAW_FOLDER}")
        return RAW_FOLDER

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise 
    