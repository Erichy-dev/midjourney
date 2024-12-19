from concurrent.futures import ThreadPoolExecutor
import time
import logging
import os
import openpyxl
from config.settings import INPUT_EXCEL_FILE, BACKUP_FOLDER
from utils.browser import connect_to_existing_edge
from utils.excel import read_prompts_from_excel
from services.midjourney import process_product
from services.google_drive import init_google_drive, set_google_drive_instance

def process_with_delay(args):
    """Process a single product with initial delay"""
    idx, product_data, delay = args
    try:
        # Wait for the specified delay
        if delay > 0:
            print(f"\n⏳ Waiting {delay} seconds before processing product {idx+1}...")
            time.sleep(delay)
        
        # Create a new browser instance for each thread
        driver = connect_to_existing_edge()
        try:
            process_product(driver, product_data, idx)
            print(f"✅ Product {idx+1} completed successfully!")
        finally:
            driver.quit()
            
    except Exception as e:
        logging.error(f"⚠️ Process halted for product {idx+1}: {e}")
        
        # Use the configured backup folder
        os.makedirs(BACKUP_FOLDER, exist_ok=True)
        backup_path = os.path.join(BACKUP_FOLDER, f"progress_backup_product_{idx+1}.xlsx")
        
        workbook = openpyxl.load_workbook(INPUT_EXCEL_FILE)
        workbook.save(backup_path)
        print(f"⚠️ Backup saved to {backup_path}")
        return False
    
    return True

def process_all_products():
    # Initialize services
    print("\n🔄 Initializing services...")
    
    # Initialize Google Drive
    print("\n📁 Connecting to Google Drive...")
    drive_instance = init_google_drive()
    set_google_drive_instance(drive_instance)
    print("✅ Connected to Google Drive")
    
    # Get browser instance
    driver = connect_to_existing_edge()
    
    print("\n🔍 Before we begin, please verify:")
    print("1. You're logged into Discord")
    print("2. You're on the MidJourney archive page")
    print("\nPress Enter when ready, or Ctrl+C to exit...")
    input()
    
    data = read_prompts_from_excel(INPUT_EXCEL_FILE)
    if not data:
        print("No valid data found in the Excel sheet.")
        return

    # Create arguments for each product with staggered delays
    process_args = [
        (idx, product_data, idx * 90)  # 90-second delay between each product
        for idx, product_data in enumerate(data)
    ]

    # Process products in parallel with a maximum of 3 concurrent processes
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_with_delay, process_args))

    # Check if all products were processed successfully
    if all(results):
        print("✅ All products completed successfully!")
    else:
        print("⚠️ Some products failed to process. Check the logs for details.")

if __name__ == "__main__":
    process_all_products() 