#!/usr/bin/env python3

from pathlib import Path
from time import time
import shutil
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the target directory and webhook URL from environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TARGET_DIR = os.getenv("TARGET_DIR")

if not WEBHOOK_URL or not TARGET_DIR:
    raise Exception("WEBHOOK_URL or TARGET_DIR is missing in the .env file.")

# Convert the target directory path to a Path object
target_dir = Path(TARGET_DIR)

if not target_dir.exists() or not target_dir.is_dir():
    raise Exception(f"{target_dir} does not exist or is not a directory.")

# 48 hours in seconds
cutoff_seconds = 48 * 3600

# Toggle dry run (False = real deletion)
dry_run = False

# Initialize deletion count
deleted_count = 0

# Go through all files and folders
for item in sorted(target_dir.rglob("*"), reverse=True):
    if not item.exists():
        continue

    try:
        age_seconds = time() - item.stat().st_mtime
        age_hours = int(age_seconds // 3600)

        if age_seconds > cutoff_seconds:
            if item.is_file():
                print(f"{'[DRY RUN]' if dry_run else '[DELETING]'} FILE: {item} — Age: {age_hours} hours")
                if not dry_run:
                    item.unlink()
                    deleted_count += 1
            elif item.is_dir():
                print(f"{'[DRY RUN]' if dry_run else '[DELETING]'} FOLDER: {item} — Age: {age_hours} hours")
                if not dry_run:
                    shutil.rmtree(item)
                    deleted_count += 1
        else:
            print(f"OK: {item} — Age: {age_hours} hours")
    except Exception as e:
        print(f"Error processing {item}: {e}")

# Prepare message for Discord
if dry_run:
    message = "Dry run completed. No files were deleted."
else:
    message = f"Download cleanup completed successfully! {deleted_count} files/folders were deleted."

# Send confirmation to Discord via webhook
try:
    payload = {
        "content": message
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    response.raise_for_status()  # Check for successful response
    print("Confirmation sent to Discord.")
except requests.exceptions.RequestException as e:
    print(f"Error sending confirmation to Discord: {e}")
