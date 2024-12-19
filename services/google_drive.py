from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import logging

# Global drive instance
_drive_instance = None

def init_google_drive():
    """Initialize Google Drive connection"""
    try:
        gauth = GoogleAuth()
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

def upload_to_google_drive(folder_path):
    """Upload the processed images folder to Google Drive"""
    try:
        print("Uploading to Google Drive...")
        drive = get_drive_instance()
        if not drive:
            raise Exception("Google Drive not initialized")

        # Upload the folder
        folder_name = os.path.basename(folder_path)
        gdrive_folder = drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        })
        gdrive_folder.Upload()
        folder_id = gdrive_folder['id']

        # Now upload all files in the folder
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                file_drive = drive.CreateFile({
                    'title': filename,
                    'parents': [{'id': folder_id}]
                })
                file_drive.SetContentFile(filepath)
                file_drive.Upload()
                print(f"Uploaded file: {filename}")

        # Generate and return shareable link
        share_link = f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"
        return share_link
    except Exception as e:
        logging.error(f"Error uploading to Google Drive: {e}")
        return None