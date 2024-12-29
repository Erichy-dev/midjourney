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
    # Set User-Agent based on platform
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        if platform.system() == "Windows"
        else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    for attempt in range(max_retries):
        try:
            command = [
                'bash',
                '-c',
                f"cd 'paste_path_here' && curl -H 'User-Agent: {user_agent}' -H 'Referer: https://www.midjourney.com/' -O {url}"
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

def download_images(driver, raw_folder_name, expected_count=None):
    """Downloads selected images from MidJourney."""
    print("Selecting and downloading images...")
    try:
        os.makedirs(RAW_FOLDER, exist_ok=True)
        os.chdir(RAW_FOLDER)
        
        # Get all available images
        images = driver.select_all("img")
        
        # Take only the expected number of most recent images
        if expected_count:
            images = images[:expected_count]  # Most recent images appear first
            total_images = expected_count
        else:
            total_images = len(images)
        
        if total_images == 0:
            raise Exception("No images found to download")
            
        print(f"Found {total_images} images to download")
        
        downloaded_count = 0
        max_attempts = 3
        
        # Download the most recent images first
        for idx in range(total_images):
            try:
                current_image = images[idx]
                current_image.click()
                time.sleep(2)
                
                img_element = driver.wait_for_element('img[style="filter: none;"]')
                img_url = img_element.get_attribute("src")
                
                if download_with_retry(img_url):
                    downloaded_count += 1
                    print(f"✅ Downloaded image {downloaded_count}/{total_images}")
                else:
                    print(f"⚠️ Failed to download image {idx + 1}")
                
                exit_button = driver.wait_for_element('button[title="Close"]')
                exit_button.click()
                
            except Exception as e:
                print(f"⚠️ Error downloading image {idx + 1}: {e}")
                time.sleep(2)
        
        if downloaded_count == 0:
            raise Exception("No images were downloaded successfully")
            
        print(f"✅ Successfully downloaded {downloaded_count} images")
        return RAW_FOLDER

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise 
    