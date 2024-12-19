from PIL import Image
import os
import shutil
import pathlib
import logging
from config.settings import SEAMLESS_PATTERN_FOLDER, DIGITAL_PAPER_FOLDER

def sanitize_name(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()

def process_images(raw_folder_path, processed_folder_path, product_type):
    if not os.path.exists(processed_folder_path):
        os.makedirs(processed_folder_path)
    for idx, filename in enumerate(os.listdir(raw_folder_path)):
        if filename.lower().endswith('.png'):
            input_path = os.path.join(raw_folder_path, filename)
            output_path = os.path.join(processed_folder_path, filename)
            with Image.open(input_path) as img:
                img = img.resize((3600, 3600), Image.LANCZOS)
                img.save(output_path, dpi=(300, 300))
            print(f"Processed image {idx + 1}") 