import os
import datetime
import sys

def log_line(level, message):
    """
    Log a message to the log file and console
    
    Args:
        level: Log level (info, warning, error, execute)
        message: Message to log
    """
    try:
        # Format message for console
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{level.upper()}] {message}"
        
        # Print to console
        print(formatted_msg)
        
        # In test mode, we don't write to file
        if 'test_harness.py' in sys.argv[0]:
            return
            
        # Get log file path
        log_dir = os.path.expanduser("~/Documents/C4D_AI_Logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file name based on date
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"cinecommand_{today}.log")
        
        # Write to log file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    
    except Exception as e:
        print(f"Error logging: {str(e)}")