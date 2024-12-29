from PIL import Image
import os
import shutil
import pathlib
import logging
import subprocess
from config.settings import SEAMLESS_PATTERN_FOLDER, DIGITAL_PAPER_FOLDER

def sanitize_name(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()

def process_images(raw_folder_path, target_folder, expected_count=None):
    """Process images in the raw folder with count verification"""
    try:
        os.makedirs(target_folder, exist_ok=True)
        
        # Get list of image files sorted by creation time (newest first)
        image_files = [f for f in os.listdir(raw_folder_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        image_files.sort(key=lambda x: os.path.getctime(os.path.join(raw_folder_path, x)), reverse=True)
        
        # Take only the expected number of most recent images
        if expected_count:
            if len(image_files) < expected_count:
                print(f"⚠️ Warning: Found fewer images ({len(image_files)}) than expected ({expected_count})")
            image_files = image_files[:expected_count]  # Take only the expected number of most recent images
        
        if not image_files:
            print(f"⚠️ No images found in {raw_folder_path}")
            return
        
        print(f"\nProcessing {len(image_files)} images:")
        print(f"From: {raw_folder_path}")
        print(f"To: {target_folder}")
        
        processed_count = 0
        for filename in image_files:
            try:
                input_path = os.path.join(raw_folder_path, filename)
                output_path = os.path.join(target_folder, filename)
                
                print(f"\nProcessing: {filename}")
                
                # Process using PIL
                with Image.open(input_path) as img:
                    # Resize to 3600x3600 using Lanczos resampling
                    img = img.resize((3600, 3600), Image.Resampling.LANCZOS)
                    # Save with high quality and DPI settings
                    img.save(
                        output_path,
                        quality=95,  # High quality for JPEGs
                        dpi=(300, 300),  # Set DPI to 300
                        optimize=True  # Enable optimization
                    )
                processed_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
                logging.error(f"Error processing {filename}: {e}")
                continue
        
        print(f"\n✅ Processed {processed_count}/{expected_count if expected_count else len(image_files)} images")
        
    except Exception as e:
        print(f"❌ Error processing folder: {e}")
        logging.error(f"Error processing folder: {e}")
        raise