from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import logging
from config.settings import PROJECT_ROOT, SEAMLESS_PATTERN_FOLDER, DIGITAL_PAPER_FOLDER

# Global drive instance
_drive_instance = None

def init_google_drive():
    """Initialize Google Drive connection"""
    try:
        gauth = GoogleAuth()
        # Set path to client_secrets.json using PROJECT_ROOT
        gauth.settings['client_config_file'] = os.path.join(PROJECT_ROOT, 'config', 'client_secrets.json')
        gauth.LocalWebserverAuth()  # This will open the browser automatically if needed
        return GoogleDrive(gauth)
    except Exception as e:
        logging.error(f"Error initializing Google Drive: {e}")
        raise

def set_google_drive_instance(drive):
    """Set the global drive instance"""
    global _drive_instance
    _drive_instance = drive

def get_drive_instance():
    """Get the global drive instance"""
    return _drive_instance

def upload_to_google_drive(target_folder):
    """Upload the processed images folder to Google Drive maintaining folder structure"""
    try:
        print("Uploading to Google Drive...")
        drive = get_drive_instance()
        if not drive:
            raise Exception("Google Drive not initialized")

        # Determine if it's Seamless Pattern or Digital Paper from the path
        folder_type = "Seamless Pattern" if SEAMLESS_PATTERN_FOLDER in target_folder else "Digital Paper"
        
        # Create main category folder (if it doesn't exist)
        main_folder = create_or_get_folder(drive, f"Digital Paper Store - {folder_type}")
        
        # Get the product folder name from the target path
        product_folder_name = os.path.basename(target_folder)
        
        # Create product subfolder
        product_folder = create_or_get_folder(drive, product_folder_name, parent_id=main_folder['id'])
        
        # Upload all files in the folder
        for filename in os.listdir(target_folder):
            filepath = os.path.join(target_folder, filename)
            if os.path.isfile(filepath):
                file_drive = drive.CreateFile({
                    'title': filename,
                    'parents': [{'id': product_folder['id']}]
                })
                file_drive.SetContentFile(filepath)
                file_drive.Upload()
                print(f"Uploaded file: {filename}")

        # Generate and return shareable link for the product folder
        share_link = f"https://drive.google.com/drive/folders/{product_folder['id']}?usp=sharing"
        return share_link
    except Exception as e:
        logging.error(f"Error uploading to Google Drive: {e}")
        return None

def create_or_get_folder(drive, folder_name, parent_id=None):
    """Create a folder in Google Drive or get it if it already exists"""
    # Search for existing folder
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    existing_folders = drive.ListFile({'q': query}).GetList()
    
    if existing_folders:
        return existing_folders[0]
    
    # Create new folder if it doesn't exist
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [{'id': parent_id}]
    
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder