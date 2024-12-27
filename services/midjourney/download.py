import time
import logging
import os
import shutil
import pathlib
import subprocess
from config.settings import BASE_OUTPUT_FOLDER, DOWNLOADS_FOLDER

def download_with_retry(url, max_retries=5):
    """Download file using yt-dlp with retries"""
    # Change to the raw folder directory
    os.chdir(BASE_OUTPUT_FOLDER)
    
    for attempt in range(max_retries):
        try:
            # Use yt-dlp to download the file
            command = [
                'yt-dlp',
                # '--no-warnings',
                # '--quiet',
                url
            ]
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:
                print(f"Download attempt {attempt + 1} failed. Retrying...")
                time.sleep(2)  # Wait 2 seconds before retry
            else:
                print(f"All download attempts failed for URL: {url}")
                raise e

def download_images(driver, raw_folder_name):
    """Downloads selected images from MidJourney."""
    print("Selecting and downloading images...")
    try:
        # Select images
        images = driver.select_all("img")[:4]
        for image in images:
            image.click()
            img_element = driver.wait_for_element('img[style="filter: none;"]')
            img_url = img_element.get_attribute("src")
            download_with_retry(img_url)
            
            exit_button = driver.wait_for_element('button[title="Close"]')
            exit_button.click()
            driver.google_get("https://www.midjourney.com/archive", bypass_cloudflare=True)

        return BASE_OUTPUT_FOLDER

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise 
    