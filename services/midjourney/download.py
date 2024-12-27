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
    os.chdir(BASE_OUTPUT_FOLDER)
    
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
        # Create raw folder if it doesn't exist
        raw_folder_path = os.path.join(RAW_FOLDER, raw_folder_name)
        os.makedirs(raw_folder_path, exist_ok=True)
        
        # Change to raw folder for downloads
        os.chdir(raw_folder_path)
        
        # Select and download images
        images = driver.select_all("img")[:4]
        for image in images:
            image.click()
            img_element = driver.wait_for_element('img[style="filter: none;"]')
            img_url = img_element.get_attribute("src")
            download_with_retry(img_url)
            
            exit_button = driver.wait_for_element('button[title="Close"]')
            exit_button.click()

        return raw_folder_path

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise 
    