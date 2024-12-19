import os
import platform

# Get Project Root Directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Base Directory for all data
DATA_ROOT = os.path.join(PROJECT_ROOT, "Digital Paper Store")

# Selenium Settings
DISCORD_LOGIN_EMAIL = "benchekroune.yassine7@gmail.com"
DISCORD_LOGIN_PASSWORD = "Malzahar77."
MIDJOURNEY_WEB_URL = "https://www.midjourney.com"

# Edge Driver Settings - Platform specific
if platform.system().lower() == 'darwin':  # macOS
    EDGE_DRIVER_PATH = "/Users/mac/Downloads/edgedriver_mac64/msedgedriver"
else:  # Windows and others
    EDGE_DRIVER_PATH = os.path.join(os.path.expanduser("~"), "WebDriver", "msedgedriver")

# Verify driver exists and is executable
if platform.system().lower() == 'darwin':
    if not os.path.exists(EDGE_DRIVER_PATH):
        raise FileNotFoundError(f"Edge driver not found at {EDGE_DRIVER_PATH}")
    # Make the driver executable if it isn't already
    if not os.access(EDGE_DRIVER_PATH, os.X_OK):
        os.chmod(EDGE_DRIVER_PATH, 0o755)

DEBUG_PORT = "9222"

# Folder Paths
BASE_OUTPUT_FOLDER = os.path.join(DATA_ROOT, "Digital Paper Store - Raw Folders")
DOWNLOADS_FOLDER = os.path.expanduser("~/Downloads")
SEAMLESS_PATTERN_FOLDER = os.path.join(DATA_ROOT, "Digital Paper Store - Seamless Pattern")
DIGITAL_PAPER_FOLDER = os.path.join(DATA_ROOT, "Digital Paper Store - Digital Paper")

# Excel Settings
INPUT_EXCEL_FILE = os.path.join(DOWNLOADS_FOLDER, "template (4).xlsx")

# Script Settings
NUMBER_OF_PROMPTS_PER_PRODUCT = 10
WAIT_TIME_BETWEEN_PROMPTS = 3
WAIT_BETWEEN_IMAGE_CHECKS = 45
MAX_IMAGE_WAIT_TIME = 900

# URLs
ORGANIZE_PAGE_URL = "https://www.midjourney.com/archive"
EXPLORE_PAGE_URL = "https://www.midjourney.com/explore?tab=top"

# Backup Settings
BACKUP_FOLDER = os.path.join(DATA_ROOT, "Digital Paper Store - Excel Sheet - Backup")

# Create necessary directories if they don't exist
REQUIRED_DIRS = [
    BASE_OUTPUT_FOLDER,
    SEAMLESS_PATTERN_FOLDER,
    DIGITAL_PAPER_FOLDER,
    BACKUP_FOLDER
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)