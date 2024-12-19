from config.settings import INPUT_EXCEL_FILE, BACKUP_FOLDER, PROJECT_ROOT
from utils.browser import connect_to_existing_edge
from utils.excel import read_prompts_from_excel
from services.midjourney import process_product
import logging
import openpyxl
import os

def process_all_products():
    data = read_prompts_from_excel(INPUT_EXCEL_FILE)
    if not data:
        print("No valid data found in the Excel sheet.")
        return

    driver = connect_to_existing_edge()
    for idx, product_data in enumerate(data):
        try:
            process_product(driver, product_data, idx)
            break
        except Exception as e:
            logging.error(f"⚠️ Process halted for product {idx+1}: {e}")
            
            # Use the configured backup folder
            os.makedirs(BACKUP_FOLDER, exist_ok=True)
            backup_path = os.path.join(BACKUP_FOLDER, "progress_backup.xlsx")
            
            workbook = openpyxl.load_workbook(INPUT_EXCEL_FILE)
            workbook.save(backup_path)
            print(f"⚠️ Backup saved to {backup_path}")
            break
    print("✅ All products completed.")

if __name__ == "__main__":
    process_all_products() 