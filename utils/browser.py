from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
import os
import time
import logging
import platform
import subprocess
from config.settings import CHROME_DRIVER_PATH, DEBUG_PORT

def launch_chrome_debug():
    print("Launching Chrome in debugging mode. Log in to MidJourney manually.")
    
    # Determine the operating system
    system = platform.system().lower()
    
    chrome_cmd = {
        'linux': 'google-chrome',
        'darwin': '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome',  # macOS
        'windows': 'chrome'
    }.get(system, 'google-chrome')  # default to 'google-chrome' for unknown systems
    
    debug_cmd = f'--remote-debugging-port={DEBUG_PORT}'
    profile_cmd = '--user-data-dir="ChromeProfile"'
    
    try:
        if system == 'windows':
            os.system(f'start {chrome_cmd} {debug_cmd} {profile_cmd}')
        else:
            subprocess.Popen([
                chrome_cmd,
                debug_cmd,
                profile_cmd
            ], shell=True)
        
        print(f"Chrome launched with debugging port {DEBUG_PORT}")
    except Exception as e:
        logging.error(f"Error launching Chrome: {e}")
        raise

def connect_to_existing_chrome():
    try:
        options = ChromeOptions()
        options.debugger_address = f"127.0.0.1:{DEBUG_PORT}"
        driver_service = ChromeService(CHROME_DRIVER_PATH)
        return webdriver.Chrome(service=driver_service, options=options)
    except Exception as e:
        print("No Chrome window detected. Launching Chrome in debugging mode...")
        launch_chrome_debug()
        time.sleep(10)
        return connect_to_existing_chrome() 