import os
from datetime import datetime

def log_access(name, status):
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "access_log.txt")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Name: {name}, Status: {status}\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)