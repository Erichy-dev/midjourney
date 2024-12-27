import time
import logging
import os
import shutil
import openpyxl
from config.settings import (
    WAIT_TIME_BETWEEN_PROMPTS,
    SEAMLESS_PATTERN_FOLDER,
    DIGITAL_PAPER_FOLDER,
    PROJECT_ROOT,
    BASE_OUTPUT_FOLDER,
    RAW_FOLDER
)
from utils.image_processor import process_images, sanitize_name
from .navigation import ensure_on_organize_page
from .download import download_images
from services.google_drive import upload_to_google_drive
from botasaurus.browser import Wait

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
            theme = entry.get("Theme", "").strip()
            category = entry.get("Category", "").strip()
            product_type = entry.get("Product Type", "").strip()
            
            # Simplified folder naming
            product_name = f"{theme} - {category} - {product_type}"
            sanitized_product_name = sanitize_name(product_name)
            
            # Determine the correct base folder based on product type
            base_folder = SEAMLESS_PATTERN_FOLDER if product_type == "Seamless Pattern" else DIGITAL_PAPER_FOLDER
            
            # Create the final folder path directly in the correct location
            processed_folder_path = os.path.join(base_folder, sanitized_product_name)
            
            print(f"Sending prompts for: {sanitized_product_name}")

            prompts = entry.get("Prompts", [])  # Extract prompts from entry
            
            for prompt_idx, prompt in enumerate(prompts):
                print(f"Submitting Prompt {prompt_idx+1}: {prompt}")
                try:
                    driver.type("textarea", prompt)  # Find textarea, clear it, and type prompt
                    driver.run_js("document.activeElement.blur()")
                    driver.click("textarea + button")  # Find and click the submit button in one go
                    time.sleep(WAIT_TIME_BETWEEN_PROMPTS)
                except Exception as e:
                    logging.error(f"Error submitting prompt: {e}")
                    continue

            wait_for_last_image_to_generate(driver)

            raw_folder_path = download_images(driver, sanitized_product_name)
            process_images(raw_folder_path, processed_folder_path)
            
            # Upload to Google Drive immediately after processing
            share_link = upload_to_google_drive(processed_folder_path)
            if share_link:
                print(f"✅ Uploaded to Google Drive: {share_link}")
            else:
                print("⚠️ Failed to upload to Google Drive")

    except Exception as e:
        logging.error(f"Error during prompt submission: {e}")
        raise

def update_excel_with_results(product_data, raw_folder_path, processed_folder_path, share_link):
    """Update the Excel file with processing results."""
    try:
        print("\nUpdating Excel file with results...")
        # Use PROJECT_ROOT to get the Excel file from the root directory
        excel_path = os.path.join(PROJECT_ROOT, "template (4).xlsx")
        workbook = openpyxl.load_workbook(excel_path)
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
        
        # Save back to the root directory
        workbook.save(excel_path)
        print("✅ Excel file updated successfully")
            
    except Exception as e:
        print(f"⚠️ Error updating Excel file: {e}")
        raise

def process_product(driver, product_data, idx):
    """Processes a single product through the MidJourney workflow."""
    try:
        print(f"🚀 Starting processing for: {product_data.get('Product Name', '')}")

        # Create folders if they don't exist
        os.makedirs(RAW_FOLDER, exist_ok=True)
        os.makedirs(SEAMLESS_PATTERN_FOLDER, exist_ok=True)
        os.makedirs(DIGITAL_PAPER_FOLDER, exist_ok=True)

        # Create product-specific folder names
        theme = product_data.get('Theme', '').strip()
        category = product_data.get('Category', '').strip()
        product_type = product_data.get('Product Type', '').strip()
        
        product_name = f"{theme} - {category} - {product_type}"
        sanitized_product_name = sanitize_name(product_name)
        
        # Define paths
        raw_folder_path = RAW_FOLDER  # Changed to use main RAW_FOLDER
        target_folder = os.path.join(
            SEAMLESS_PATTERN_FOLDER if product_type == "Seamless Pattern" else DIGITAL_PAPER_FOLDER,
            sanitized_product_name
        )

        # Create target folder
        os.makedirs(target_folder, exist_ok=True)
        print(f"📂 Created target folder: {target_folder}")

        # Send prompts and download images
        send_prompts_to_midjourney(driver, [product_data])
        
        # Verify images exist
        if not os.path.exists(raw_folder_path):
            raise FileNotFoundError(f"Raw folder not found: {raw_folder_path}")
            
        image_files = [f for f in os.listdir(raw_folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not image_files:
            raise FileNotFoundError(f"No images found in {raw_folder_path}")
            
        print(f"✅ Found {len(image_files)} images in raw folder")
        
        # Process images
        process_images(raw_folder_path, target_folder)
        
        # Upload to Google Drive
        share_link = upload_to_google_drive(target_folder)
        
        if share_link:
            print(f"✅ Uploaded to Google Drive: {share_link}")
        else:
            print("⚠️ Failed to upload to Google Drive")

        print(f"✅ Product processed successfully!")
        return product_data, raw_folder_path, target_folder, share_link
        
    except Exception as e:
        logging.error(f"Error processing product: {e}")
        raise 