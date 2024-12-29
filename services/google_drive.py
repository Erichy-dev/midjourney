from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import logging
from config.settings import PROJECT_ROOT, SEAMLESS_PATTERN_FOLDER, DIGITAL_PAPER_FOLDER
import time

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

def upload_to_google_drive(target_folder, max_retries=3):
    """Upload the processed images folder to Google Drive maintaining folder structure"""
    for attempt in range(max_retries):
        try:
            print("Uploading to Google Drive...")
            drive = get_drive_instance()
            if not drive:
                raise Exception("Google Drive not initialized")

            # Determine if it's Seamless Pattern or Digital Paper from the path
            folder_type = "Seamless Pattern" if SEAMLESS_PATTERN_FOLDER in target_folder else "Digital Paper"
            
            # Create main category folder (if it doesn't exist) - No public permissions
            main_folder = create_or_get_folder(drive, f"Digital Paper Store - {folder_type}")
            
            # Get the product folder name from the target path
            product_folder_name = os.path.basename(target_folder)
            
            # Create product subfolder and make it public
            product_folder = create_or_get_folder(drive, product_folder_name, parent_id=main_folder['id'])
            # Set public permissions for product folder
            product_folder.InsertPermission({
                'type': 'anyone',
                'role': 'reader',
                'withLink': True
            })
            
            # Get list of local files to upload
            local_files = [f for f in os.listdir(target_folder) if os.path.isfile(os.path.join(target_folder, f))]
            uploaded_count = 0
            uploaded_files_links = []
            
            # Upload all files in the folder and make them public
            for filename in local_files:
                filepath = os.path.join(target_folder, filename)
                try:
                    file_drive = drive.CreateFile({
                        'title': filename,
                        'parents': [{'id': product_folder['id']}]
                    })
                    file_drive.SetContentFile(filepath)
                    file_drive.Upload()
                    # Make each file public
                    file_drive.InsertPermission({
                        'type': 'anyone',
                        'role': 'reader',
                        'withLink': True
                    })
                    file_link = f"https://drive.google.com/uc?id={file_drive['id']}"
                    uploaded_files_links.append(file_link)
                    uploaded_count += 1
                    print(f"✅ Uploaded file: {filename}")
                except Exception as e:
                    print(f"⚠️ Failed to upload {filename}: {e}")

            # Verify upload count
            if uploaded_count == 0:
                raise Exception("No files were uploaded successfully")
            print(f"✅ Successfully uploaded {uploaded_count}/{len(local_files)} files")

            # Return both folder link and individual file links
            folder_link = f"https://drive.google.com/drive/folders/{product_folder['id']}?usp=sharing"
            return {
                'folder_link': folder_link,
                'file_links': uploaded_files_links
            }
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Upload attempt {attempt + 1} failed, retrying...")
                time.sleep(5)
            else:
                logging.error(f"All upload attempts failed: {e}")
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