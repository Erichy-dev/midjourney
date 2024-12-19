from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import WebDriverException
import os
import time
import logging
import platform
import subprocess
import socket
from config.settings import EDGE_DRIVER_PATH, DEBUG_PORT

def is_port_in_use(port):
    """Check if the debug port is already in use (indicating Edge is running)"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', int(port))) == 0
    except Exception as e:
        logging.error(f"Error checking port: {e}")
        return False

def wait_for_port(port, timeout=30):
    """Wait for the port to become available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(1)
    return False

def launch_edge_debug():
    """Launch Edge in debug mode if not already running"""
    if is_port_in_use(DEBUG_PORT):
        print(f"Edge is already running on port {DEBUG_PORT}")
        return True

    print("Launching Edge in debugging mode...")
    
    system = platform.system().lower()
    print(f"Detected operating system: {system}")
    
    edge_cmd = {
        'linux': 'microsoft-edge',
        'darwin': '/Applications/Microsoft\\ Edge.app/Contents/MacOS/Microsoft\\ Edge',
        'windows': 'msedge'
    }.get(system, 'microsoft-edge')
    
    debug_cmd = f'--remote-debugging-port={DEBUG_PORT}'
    profile_cmd = '--user-data-dir="EdgeProfile"'
    
    try:
        if system == 'darwin':  # macOS specific
            cmd = f'{edge_cmd} {debug_cmd} {profile_cmd}'
            print(f"Executing command: {cmd}")
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == 'windows':
            os.system(f'start {edge_cmd} {debug_cmd} {profile_cmd} > NUL 2>&1')
        else:
            subprocess.Popen([edge_cmd, debug_cmd, profile_cmd], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        print("\nPlease complete the following steps:")
        print("1. Set up your Edge browser (sync/account/theme)")
        print("2. Log in to MidJourney")
        print("3. Once you're ready, press Enter to continue...")
        input()
        
        # Verify Edge is running
        if not wait_for_port(DEBUG_PORT):
            raise Exception("Edge is not running on the debug port after setup")
        
        print("✅ Edge setup completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error launching Edge: {e}")
        return False

def connect_to_existing_edge():
    """Connect to Edge instance or launch a new one"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Debug information
            print(f"Looking for Edge driver at: {EDGE_DRIVER_PATH}")
            print(f"Current working directory: {os.getcwd()}")
            
            # Verify Edge driver exists
            if not os.path.exists(EDGE_DRIVER_PATH):
                raise FileNotFoundError(
                    f"Edge driver not found at {EDGE_DRIVER_PATH}. "
                    "Please download it from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/"
                )

            options = EdgeOptions()
            options.use_chromium = True
            options.debugger_address = f"127.0.0.1:{DEBUG_PORT}"
            driver_service = EdgeService(EDGE_DRIVER_PATH)
            driver = webdriver.Edge(service=driver_service, options=options)
            
            # Test the connection
            driver.current_url
            return driver
            
        except WebDriverException as e:
            retry_count += 1
            if retry_count >= max_retries:
                logging.error("Failed to connect to Edge after multiple attempts")
                raise
            
            print("No Edge window detected or connection failed. Launching Edge in debugging mode...")
            if not launch_edge_debug():
                raise Exception("Failed to launch Edge browser")
            time.sleep(5)
            
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise