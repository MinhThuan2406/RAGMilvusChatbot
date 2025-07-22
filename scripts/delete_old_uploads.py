import os
import time
from datetime import datetime

def delete_old_files(directory: str, max_age_hours: int = 24):
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

if __name__ == "__main__":
    # Change this path to your uploads directory inside the container or host
    uploads_dir = "/data/uploads"
    # Or, if running on host and mounting the volume, use the host path
    # uploads_dir = "./data/uploads"
    delete_old_files(uploads_dir, max_age_hours=24)
