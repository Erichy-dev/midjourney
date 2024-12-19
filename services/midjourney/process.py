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
        workbook = openpyxl.load_workbook(INPUT_EXCEL_FILE)
        sheet = workbook.active
        
        # Find the row for this product
        product_name = product_data.get('Product Name', '')
        product_row = None
        
        for row in range(2, sheet.max_row + 1):  # Start from row 2 to skip header
            if sheet.cell(row=row, column=1).value == product_name:  # Assuming Product Name is in column A
                product_row = row
                break
        
        if product_row:
            # Update the cells with new information
            updates = {
                'Product Type': product_data.get('Product Type', ''),
                'Category': product_data.get('Category', ''),
                'Theme': product_data.get('Theme', ''),
                'Prompts': product_data.get('Prompts', ''),
                'Raw Folder Path': raw_folder_path,
                'Processed Folder Path': processed_folder_path,
                'Google Drive Link': share_link,
                'Listing Images Folder': os.path.join(processed_folder_path, 'listing_images') if processed_folder_path else '',
                'Downloadable File Path': os.path.join(processed_folder_path, 'download') if processed_folder_path else '',
                'Title': product_data.get('Title', ''),
                'Hook': product_data.get('Hook', ''),
                'Premade Description': product_data.get('Premade Description', ''),
                'Full Description': product_data.get('Full Description', '')
            }
            
            # Column mappings (adjust these based on your Excel structure)
            column_mappings = {
                'Product Type': 'B',
                'Category': 'C',
                'Theme': 'D',
                'Prompts': 'E',
                'Raw Folder Path': 'F',
                'Processed Folder Path': 'G',
                'Google Drive Link': 'H',
                'Listing Images Folder': 'I',
                'Downloadable File Path': 'J',
                'Title': 'K',
                'Hook': 'L',
                'Premade Description': 'M',
                'Full Description': 'N'
            }
            
            # Update each cell
            for field, value in updates.items():
                if field in column_mappings:
                    column = column_mappings[field]
                    sheet[f'{column}{product_row}'] = value
            
            # Save the workbook
            workbook.save(INPUT_EXCEL_FILE)
            print("✅ Excel file updated successfully")
            
        else:
            print(f"⚠️ Could not find row for product: {product_name}")
            
    except Exception as e:
        print(f"⚠️ Error updating Excel file: {e}")
        raise

def process_product(driver, product_data, idx):
    """Processes a single product through the MidJourney workflow."""
    try:
        product_name = f"product {idx+1}"
        print(f"🚀 Starting processing for: {product_name}")

        send_prompts_to_midjourney(driver, [product_data])

        print(f"✅ Product {product_name} processed successfully!")
    except Exception as e:
        logging.error(f"Error processing product {product_name}: {e}")
        raise 