import time
import logging
import os
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config.settings import (
    WAIT_TIME_BETWEEN_PROMPTS,
    SEAMLESS_PATTERN_FOLDER,
    DIGITAL_PAPER_FOLDER
)
from utils.image_processor import process_images, sanitize_name
from .navigation import ensure_on_organize_page
from .download import download_images
from services.google_drive import upload_to_google_drive

def wait_for_last_image_to_generate(driver):
    """Waits for images to generate."""
    fixed_wait_time = 1 * 60  # 1 minute timeout
    print(f"⏳ Waiting for {fixed_wait_time // 60} minutes to allow images to generate...")
    time.sleep(fixed_wait_time)
    print("✅ Timeout reached. Assuming all images are generated.")

def send_prompts_to_midjourney(driver, data):
    """Sends prompts to MidJourney and processes the results."""
    try:
        ensure_on_organize_page(driver)

        for entry in data:
            prompts = entry.get('Prompts', [])
            theme = entry.get("Theme", "").strip()
            category = entry.get("Category", "").strip()
            product_type = entry.get("Product Type", "").strip()
            
            product_name = f"{theme} - {category} - {product_type}"
            raw_folder_name = f"Raw {product_name}"
            
            sanitized_product_name = sanitize_name(product_name)
            sanitized_raw_folder_name = sanitize_name(raw_folder_name)
            
            print(f"Sending prompts for: {sanitized_product_name}")
            print(f"Raw folder name: {sanitized_raw_folder_name}")

            for prompt_idx, prompt in enumerate(prompts):
                print(f"Submitting Prompt {prompt_idx+1}: {prompt}")
                try:
                    text_area = driver.find_element(By.TAG_NAME, "textarea")
                    text_area.clear()
                    text_area.send_keys(prompt)
                    text_area.send_keys(Keys.RETURN)
                    time.sleep(WAIT_TIME_BETWEEN_PROMPTS)
                except Exception as e:
                    logging.error(f"Error submitting prompt: {e}")
                    continue

            wait_for_last_image_to_generate(driver)

            raw_folder_path = download_images(driver, sanitized_raw_folder_name)
            processed_folder_path = os.path.join(
                SEAMLESS_PATTERN_FOLDER if entry['Product Type'] == "Seamless Pattern" else DIGITAL_PAPER_FOLDER,
                f"{sanitized_product_name}-DPS"
            )
            process_images(raw_folder_path, processed_folder_path)
            print(f"Folder successfully processed: {processed_folder_path}")

            # Upload to Google Drive
            share_link = upload_to_google_drive(processed_folder_path)
            if share_link:
                print(f"✅ Uploaded to Google Drive: {share_link}")
                
                # Delete local folders only after successful upload
                try:
                    # Delete raw folder
                    if os.path.exists(raw_folder_path):
                        shutil.rmtree(raw_folder_path)
                        print(f"✅ Deleted raw folder: {raw_folder_path}")
                    
                    # Delete processed folder
                    if os.path.exists(processed_folder_path):
                        shutil.rmtree(processed_folder_path)
                        print(f"✅ Deleted processed folder: {processed_folder_path}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not delete local folders: {e}")
                    print("You may want to delete them manually later")
            else:
                print("⚠️ Failed to upload to Google Drive")
                print("Keeping local folders for retry")

    except Exception as e:
        logging.error(f"Error during prompt submission: {e}")
        raise

def process_product(driver, product_data, product_index):
    """Processes a single product through the MidJourney workflow."""
    try:
        product_name = f"product {product_index+1}"
        print(f"🚀 Starting processing for: {product_name}")

        send_prompts_to_midjourney(driver, [product_data])

        print(f"✅ Product {product_name} processed successfully!")
    except Exception as e:
        logging.error(f"Error processing product {product_name}: {e}")
        raise 