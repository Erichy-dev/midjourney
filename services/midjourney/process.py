import time
import logging
import os
import shutil
import openpyxl
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config.settings import (
    WAIT_TIME_BETWEEN_PROMPTS,
    SEAMLESS_PATTERN_FOLDER,
    DIGITAL_PAPER_FOLDER,
    INPUT_EXCEL_FILE
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

def update_excel_with_results(product_data, raw_folder_path, processed_folder_path, share_link):
    """Update the Excel file with processing results."""
    try:
        print("\nUpdating Excel file with results...")
        workbook = openpyxl.load_workbook("template (4).xlsx")
        sheet = workbook.active
        
        # Find the row for this product
        product_name = product_data.get('Product Name', '')
        target_row = None
        
        # Find the row with the matching product name
        for row in range(2, sheet.max_row + 1):
            if sheet.cell(row=row, column=1).value == product_name:
                target_row = row
                break
        
        # If row doesn't exist, create a new one
        if not target_row:
            target_row = sheet.max_row + 1
            print(f"Creating new row at position {target_row}")
        
        # Update the row
        sheet[f'A{target_row}'] = product_data.get('Product Name', '')
        sheet[f'B{target_row}'] = product_data.get('Product Type', '')
        sheet[f'C{target_row}'] = product_data.get('Category', '')
        sheet[f'D{target_row}'] = product_data.get('Theme', '')
        sheet[f'E{target_row}'] = str(product_data.get('Prompts', ''))
        sheet[f'F{target_row}'] = raw_folder_path
        sheet[f'G{target_row}'] = processed_folder_path
        sheet[f'H{target_row}'] = share_link
        sheet[f'I{target_row}'] = os.path.join(processed_folder_path, 'listing_images') if processed_folder_path else ''
        sheet[f'J{target_row}'] = os.path.join(processed_folder_path, 'download') if processed_folder_path else ''
        sheet[f'K{target_row}'] = product_data.get('Title', '')
        sheet[f'L{target_row}'] = product_data.get('Hook', '')
        sheet[f'M{target_row}'] = product_data.get('Premade Description', '')
        sheet[f'N{target_row}'] = product_data.get('Full Description', '')
        
        workbook.save("template (4).xlsx")
        print("✅ Excel file updated successfully")
            
    except Exception as e:
        print(f"⚠️ Error updating Excel file: {e}")
        raise

def process_product(driver, product_data, idx):
    """Processes a single product through the MidJourney workflow."""
    try:
        print(f"🚀 Starting processing for: {product_data.get('Product Name', '')}")

        raw_folder_path = None
        processed_folder_path = None
        share_link = None

        send_prompts_to_midjourney(driver, [product_data])

        # After processing is complete
        share_link = upload_to_google_drive(processed_folder_path)
        
        if share_link:
            print(f"✅ Uploaded to Google Drive: {share_link}")
            
            # Delete local folders only after successful upload
            try:
                if os.path.exists(raw_folder_path):
                    shutil.rmtree(raw_folder_path)
                    print(f"✅ Deleted raw folder: {raw_folder_path}")
                
                if os.path.exists(processed_folder_path):
                    shutil.rmtree(processed_folder_path)
                    print(f"✅ Deleted processed folder: {processed_folder_path}")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete local folders: {e}")
                print("You may want to delete them manually later")
        else:
            print("⚠️ Failed to upload to Google Drive")
            print("Keeping local folders for retry")

        print(f"✅ Product processed successfully!")
        # Return both the paths and the updated product_data
        return product_data, raw_folder_path, processed_folder_path, share_link
        
    except Exception as e:
        logging.error(f"Error processing product: {e}")
        raise 