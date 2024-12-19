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
    """Connect to an existing Edge instance"""
    try:
        # Set up Edge options to connect to existing instance
        options = EdgeOptions()
        options.use_chromium = True
        options.add_experimental_option("debuggerAddress", f"localhost:{DEBUG_PORT}")
        
        # Create a new Edge service
        driver_service = EdgeService(EDGE_DRIVER_PATH)
        
        # Connect to existing Edge instance
        driver = webdriver.Edge(service=driver_service, options=options)
        
        print("✅ Connected to existing Edge instance")
        return driver
            
    except Exception as e:
        logging.error(f"Unexpected error connecting to Edge: {e}")
        raise