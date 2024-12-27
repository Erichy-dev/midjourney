import openpyxl
import logging
import os

def read_prompts_from_excel(file_path):
    """Read prompts and metadata from Excel file with validation."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
            
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        headers = [cell.value for cell in sheet[1]]
        
        required_headers = ["Prompts", "Theme", "Category", "Product Type"]
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

        # Get column indices
        prompts_index = headers.index("Prompts")
        theme_index = headers.index("Theme")
        category_index = headers.index("Category")
        product_type_index = headers.index("Product Type")

        data = []
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
            if not any(row):  # Skip empty rows
                continue
                
            if not row[prompts_index]:
                print(f"⚠️ Skipping row {row_idx}: No prompts found")
                continue
                
            # Validate required fields
            if not all([row[theme_index], row[category_index], row[product_type_index]]):
                print(f"⚠️ Skipping row {row_idx}: Missing required fields")
                continue
                
            prompts = [line.strip() for line in row[prompts_index].splitlines() if line.strip()]
            
            if not prompts:
                print(f"⚠️ Skipping row {row_idx}: No valid prompts after processing")
                continue
                
            data.append({
                "Prompts": prompts,
                "Theme": row[theme_index].strip(),
                "Category": row[category_index].strip(),
                "Product Type": row[product_type_index].strip(),
                "Row Index": row_idx
            })
            
        print(f"✅ Found {len(data)} valid products to process")
        return data
        
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        raise 