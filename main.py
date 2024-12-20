import time
import logging
import os
import openpyxl
from services.midjourney.process import update_excel_with_results
from utils.browser import connect_to_existing_edge
from utils.excel import read_prompts_from_excel
from services.midjourney import process_product
from services.google_drive import init_google_drive, set_google_drive_instance
from config.settings import INPUT_EXCEL_FILE  # Import from settings

# Constants
BACKUP_FOLDER = "backups"

def process_all_products():
    """Process all products sequentially"""
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
    
    data = read_prompts_from_excel(INPUT_EXCEL_FILE)  # Use the imported constant
    if not data:
        print("No valid data found in the Excel sheet.")
        return

    success_count = 0
    total_products = len(data)

    try:
        for idx, product_data in enumerate(data):
            print(f"\n🎯 Processing product {idx+1} of {total_products}")
            try:
                # Process the product and get the results
                updated_product_data = {
                    'Product Name': product_data.get('Product Name', 'Untitled Product'),
                    'Product Type': product_data.get('Product Type', 'Unknown Type'),
                    'Category': product_data.get('Category', 'Uncategorized'),
                    'Theme': product_data.get('Theme', 'No Theme'),
                    'Prompts': product_data.get('Prompts', []),
                    'Title': product_data.get('Title', ''),
                    'Hook': product_data.get('Hook', ''),
                    'Premade Description': product_data.get('Premade Description', ''),
                    'Full Description': product_data.get('Full Description', '')
                }
                
                # Process the product and get the results
                updated_product_data, raw_path, processed_path, share_link = process_product(driver, updated_product_data, idx)
                
                # Update Excel with results using the updated product data
                update_excel_with_results(updated_product_data, raw_path, processed_path, share_link)
                
                print(f"✅ Product {idx+1} completed successfully!")
                success_count += 1
                
                # Wait between products (optional, adjust time as needed)
                if idx < total_products - 1:  # Don't wait after the last product
                    print(f"\n⏳ Waiting 30 seconds before next product...")
                    time.sleep(10)
                
            except Exception as e:
                logging.error(f"⚠️ Process halted for product {idx+1}: {e}")
                
                # Create backup
                os.makedirs(BACKUP_FOLDER, exist_ok=True)
                backup_path = os.path.join(BACKUP_FOLDER, f"progress_backup_product_{idx+1}.xlsx")
                workbook = openpyxl.load_workbook(INPUT_EXCEL_FILE)
                workbook.save(backup_path)
                print(f"⚠️ Backup saved to {backup_path}")
                
                # Ask user if they want to continue
                response = input("\n❓ Do you want to continue with the next product? (y/n): ")
                if response.lower() != 'y':
                    print("\n🛑 Processing stopped by user")
                    break

    finally:
        # Clean up
        driver.quit()
        
    # Final summary
    print(f"\n📊 Processing complete!")
    print(f"✅ Successfully processed: {success_count}/{total_products} products")
    if success_count < total_products:
        print(f"⚠️ Failed: {total_products - success_count} products")
        print("Check the backup files in the 'backups' folder for details")

if __name__ == "__main__":
    process_all_products() 