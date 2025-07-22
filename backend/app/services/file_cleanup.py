import os
import time
from datetime import datetime, timedelta
from fastapi import BackgroundTasks

def delete_old_files_task(directory: str, max_age_hours: int = 24):
    """
    Delete files older than max_age_hours in the given directory.
    """
    now = time.time()
    cutoff = now - max_age_hours * 3600
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < cutoff:
                try:
                    os.remove(file_path)
                    print(f"Deleted old file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
