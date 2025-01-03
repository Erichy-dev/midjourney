import time
import logging
import os
import shutil
import pathlib
import subprocess
from config.settings import BASE_OUTPUT_FOLDER, DOWNLOADS_FOLDER, RAW_FOLDER
import platform
from PIL import Image

def validate_image(filepath):
    """Validate if the downloaded file is a valid image"""
    try:
        with Image.open(filepath) as img:
            # Try to load the image data
            img.verify()
            # If we can load and verify the image, it's valid
            return True
    except Exception as e:
        print(f"❌ Invalid image file: {e}")
        # Remove the corrupted file
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def download_with_retry(url, product_folder_path, driver=None, max_retries=5):
    """Download file using curl with retries"""
    # Create product folder if it doesn't exist
    os.makedirs(product_folder_path, exist_ok=True)
    os.chdir(product_folder_path)
    
    # Set User-Agent based on platform
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        if platform.system() == "Windows"
        else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Generate timestamp filename
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(url)[1] or '.png'  # Default to .png if no extension
    custom_filename = f"{timestamp}{file_extension}"
    filepath = os.path.join(product_folder_path, custom_filename)
    
    for attempt in range(max_retries):
        try:
            command = [
                'curl',
                '-H', f'User-Agent: {user_agent}',
                '-H', 'Referer: https://www.midjourney.com/',
                '-o', custom_filename,
                url
            ]
            subprocess.run(command, check=True)
            
            # Validate the downloaded image
            if validate_image(filepath):
                return True
            else:
                print(f"Downloaded file is not a valid image, attempt {attempt + 1}")
                # Remove the invalid file
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Removed invalid file: {filepath}")
                
                # Try immediate redownload up to 3 times
                for retry_attempt in range(3):
                    print(f"Immediate retry attempt {retry_attempt + 1}")
                    try:
                        subprocess.run(command, check=True)
                        if validate_image(filepath):
                            print(f"✅ Successful download on retry {retry_attempt + 1}")
                            return True
                        else:
                            # Clean up invalid file before next attempt
                            if os.path.exists(filepath):
                                os.remove(filepath)
                    except subprocess.CalledProcessError as e:
                        print(f"Download failed on retry {retry_attempt + 1}: {e}")
                        if os.path.exists(filepath):
                            os.remove(filepath)
                continue
                
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:
                print(f"Download attempt {attempt + 1} failed. Retrying...")
                time.sleep(2)
            else:
                print(f"❌ All download attempts failed for URL: {url}")
                return False
    
    return False

def download_images(driver, product_name, expected_count=None):
    """Downloads selected images from MidJourney."""
    print("Selecting and downloading images...")
    try:
        # Create product-specific folder within RAW_FOLDER
        product_raw_folder = os.path.join(RAW_FOLDER, product_name)
        os.makedirs(product_raw_folder, exist_ok=True)
        
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
                
                if download_with_retry(img_url, product_raw_folder, driver):
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
        return product_raw_folder

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise 
    