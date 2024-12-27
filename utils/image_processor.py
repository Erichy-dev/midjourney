from PIL import Image
import os
import shutil
import pathlib
import logging
import subprocess
from config.settings import SEAMLESS_PATTERN_FOLDER, DIGITAL_PAPER_FOLDER

def sanitize_name(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()

def process_images(raw_folder_path, target_folder):
    """Process all images in the raw folder and save directly to target folder"""
    try:
        # Ensure the target folder exists
        os.makedirs(target_folder, exist_ok=True)
        
        # Get list of image files from raw folder
        image_files = [f for f in os.listdir(raw_folder_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:4]
        
        if not image_files:
            print(f"⚠️ No images found in {raw_folder_path}")
            return
        
        print(f"\nProcessing {len(image_files)} images:")
        print(f"From: {raw_folder_path}")
        print(f"To: {target_folder}")
        
        for filename in image_files:
            try:
                input_path = os.path.join(raw_folder_path, filename)
                output_path = os.path.join(target_folder, filename)  # Keep original filename
                
                print(f"\nProcessing: {filename}")
                
                # Use FFmpeg for upscaling
                command = [
                    'ffmpeg',
                    '-hide_banner',     # Hide FFmpeg compilation info
                    '-loglevel', 'error',  # Only show errors
                    '-i', input_path,   # Input file
                    '-vf', 'scale=3600:3600:flags=lanczos',  # Scale to 3600x3600 using Lanczos
                    '-compression_level', '6',  # Compression level (0-9)
                    '-y',               # Overwrite output file if it exists
                    output_path
                ]
                
                print(f"Upscaling image to 3600x3600...")
                subprocess.run(command, check=True)
                
                # Set DPI using PIL
                with Image.open(output_path) as img:
                    img.save(output_path, dpi=(300, 300))
                    print(f"Set DPI to 300 and saved to: {output_path}")
                    
            except subprocess.CalledProcessError as e:
                print(f"❌ FFmpeg error processing {filename}: {e}")
                logging.error(f"FFmpeg error processing {filename}: {e}")
                continue
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
                logging.error(f"Error processing {filename}: {e}")
                continue
        
        # Verify processed files
        processed_files = [f for f in os.listdir(target_folder) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        print(f"\n✅ Processed {len(processed_files)}/{len(image_files)} images")
        
    except Exception as e:
        print(f"❌ Error processing folder: {e}")
        logging.error(f"Error processing folder: {e}")
        raise