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
import sys

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
    system = platform.system().lower()
    
    print("\nPlease complete the following steps:")
    print("\n1. Start Edge with Remote Debugging:")
    if system == 'darwin':  # macOS
        print('   Open Terminal and run:')
        print('   /Applications/Microsoft\\ Edge.app/Contents/MacOS/Microsoft\\ Edge --remote-debugging-port=9222')
    else:  # Windows
        print('   Open Command Prompt and run:')
        print('   start msedge --remote-debugging-port=9222 --user-data-dir="C:\\EdgeProfile"')
    
    print("\n2. In the Edge window that opens:")
    print("   - Log in to your Discord account")
    print("   - Open MidJourney in Discord")
    print("   - Disable 'Ask where to save each file before downloading'")
    print("     (Edge Settings > Downloads > Turn off 'Ask where to save each file before downloading')")
    
    print("\n3. Once you're ready, press Enter to continue...")
    print("\nNote: Do not close the Edge window that was opened with remote debugging")
    input()

def connect_to_existing_edge():
    """Connect to an existing Edge instance"""
    try:
        print("\n🌟 Browser Setup")
        print("================")
        
        # First check if Edge is running with remote debugging
        if not is_port_in_use(DEBUG_PORT):
            system = platform.system().lower()
            print("\n❌ Edge is not running with remote debugging enabled!")
            print("\nPlease follow these steps:")
            print("\n1. Open a new Terminal/Command Prompt window")
            print("2. Copy and run this command:")
            if system == 'darwin':  # macOS
                print('\n   /Applications/Microsoft\\ Edge.app/Contents/MacOS/Microsoft\\ Edge --remote-debugging-port=9222')
            else:  # Windows
                print('\n   start msedge --remote-debugging-port=9222')
            
            print("\n3. Press Enter once Edge is running...")
            input()
            
            # Verify Edge is now running
            if not is_port_in_use(DEBUG_PORT):
                print("\n❌ Edge still not detected with remote debugging.")
                print("Please make sure you ran the command correctly and try again.")
                sys.exit(1)
        
        print("✅ Found Edge running with remote debugging")
        
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