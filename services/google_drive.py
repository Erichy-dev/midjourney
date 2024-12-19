from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import logging

def upload_to_google_drive(folder_path):
    """
    Upload the processed images folder as-is to Google Drive, set permissions to 'Anyone with link' (Editor),
    and return the shareable link.
    """
    try:
        print("Authenticating Google Drive...")
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # Authenticate user via a web server
        drive = GoogleDrive(gauth)

        # Upload the folder
        folder_name = os.path.basename(folder_path)
        gdrive_folder = drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        })
        gdrive_folder.Upload()
        folder_id = gdrive_folder['id']

        print(f"Folder '{folder_name}' uploaded to Google Drive. Setting permissions...")
        
        # Set permissions: Anyone with link can edit
        gdrive_folder.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'writer'
        })

        # Generate and return shareable link
        share_link = f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"
        print(f"Shareable Link: {share_link}")

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

        return share_link
    except Exception as e:
        logging.error(f"Error uploading folder to Google Drive: {e}")
        return None 