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
from config.settings import (
    ORGANIZE_PAGE_URL,
    WAIT_TIME_BETWEEN_PROMPTS,
    BASE_OUTPUT_FOLDER,
    SEAMLESS_PATTERN_FOLDER,
    DIGITAL_PAPER_FOLDER,
    DOWNLOADS_FOLDER
)
from utils.image_processor import process_images, sanitize_name

def ensure_on_organize_page(driver):
    """Ensures the browser is on the MidJourney organize page."""
    try:
        if "archive" not in driver.current_url.lower():
            print("Navigating to the Organize page...")
            driver.get(ORGANIZE_PAGE_URL)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            driver.refresh()
            time.sleep(5)
            
        if is_verification_page(driver):
            input("Please complete the verification and press Enter to continue...")
        print("Successfully navigated to the Organize page.")

    except Exception as e:
        logging.error(f"Error navigating to the Organize page: {e}")
        raise

def is_verification_page(driver):
    """Checks if the current page is a verification page."""
    try:
        verification_elements = [
            (By.XPATH, "//p[@id='TBuuD2' and contains(text(), 'Verify you are human by completing the action below.')]"),
            (By.XPATH, "//span[contains(@class, 'cb-lb-t') and contains(text(), 'Verify you are human')]"),
            (By.XPATH, "//iframe[contains(@src, 'captcha')]"),
            (By.XPATH, "//div[contains(@class, 'verification')]"),
            (By.XPATH, "//div[contains(text(), 'Verify you are human')]"),
            (By.XPATH, "//div[contains(text(), 'human verification')]")
        ]
        for by, value in verification_elements:
            if driver.find_elements(by, value):
                logging.info("Verification page detected.")
                return True
        return False
    except Exception as e:
        logging.error(f"Error checking for verification page: {e}")
        return False

def wait_for_last_image_to_generate(driver):
    """Waits for images to generate."""
    fixed_wait_time = 1 * 60  # 1 minute timeout
    print(f"⏳ Waiting for {fixed_wait_time // 60} minutes to allow images to generate...")
    time.sleep(fixed_wait_time)
    print("✅ Timeout reached. Assuming all images are generated.")

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
                driver.refresh()
                time.sleep(5)
                if is_verification_page(driver):
                    input("Please complete the verification and press Enter to continue...")
                images = driver.find_elements(By.CSS_SELECTOR, "img")[:4]
                for image in images:
                    ActionChains(driver).key_down(Keys.SHIFT).click(image).key_up(Keys.SHIFT).perform()

        if not download_button:
            raise Exception("Failed to locate download button after multiple attempts")

        # Process downloaded files
        zip_file_path = max(pathlib.Path(DOWNLOADS_FOLDER).glob("*.zip"), key=os.path.getctime)
        extracted_folder_path = os.path.join(BASE_OUTPUT_FOLDER, raw_folder_name)
        if not os.path.exists(extracted_folder_path):
            os.makedirs(extracted_folder_path)
        shutil.unpack_archive(zip_file_path, extracted_folder_path)
        os.remove(zip_file_path)

        return extracted_folder_path

    except Exception as e:
        logging.error(f"Error in download_images: {e}")
        raise

def send_prompts_to_midjourney(driver, data):
    """Sends prompts to MidJourney and processes the results."""
    try:
        ensure_on_organize_page(driver)
        driver.refresh()
        time.sleep(5)
        
        if is_verification_page(driver):
            input("Please complete the verification and press Enter to continue...")

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

            # Submit each prompt
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

            # Download and process images
            raw_folder_path = download_images(driver, sanitized_raw_folder_name)
            processed_folder_path = os.path.join(
                SEAMLESS_PATTERN_FOLDER if entry['Product Type'] == "Seamless Pattern" else DIGITAL_PAPER_FOLDER,
                f"{sanitized_product_name}-DPS"
            )
            process_images(raw_folder_path, processed_folder_path, entry['Product Type'])
            print(f"Folder successfully processed: {processed_folder_path}")

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