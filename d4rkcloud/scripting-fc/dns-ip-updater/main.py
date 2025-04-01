import requests  # type: ignore
import json
import os
import logging
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

# Configurations
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_RECORD_ID = os.getenv("CLOUDFLARE_RECORD_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LAST_IP_FILE = "/home/dami/docker/ip-updater/last_ip.txt"
LOG_FILE = "/home/dami/docker/ip-updater/ip_updater.log"
LAST_READ_POSITION_FILE = "/home/dami/docker/ip-updater/last_read_position.txt"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        return response.json().get("ip")
    except requests.RequestException as e:
        logging.error(f"Error fetching public IP: {e}")
        return None

def read_last_ip():
    if os.path.exists(LAST_IP_FILE):
        with open(LAST_IP_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_ip(ip):
    with open(LAST_IP_FILE, "w") as f:
        f.write(ip)

def get_cloudflare_current_ip():
    url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records/{CLOUDFLARE_RECORD_ID}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        if response.status_code == 200 and result.get("success"):
            return result["result"]["content"]  # Return current IP from Cloudflare
        else:
            logging.error(f"Cloudflare Error: {result}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching Cloudflare IP: {e}")
        return None
    except json.JSONDecodeError:
        logging.error("Invalid JSON response from Cloudflare")
        return None

def update_cloudflare_dns(ip):
    url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records/{CLOUDFLARE_RECORD_ID}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A",
        "name": "d4rkcyber.xyz",  # Replace with your domain
        "content": ip,
        "ttl": 1,
        "proxied": False
    }

    try:
        response = requests.put(url, headers=headers, json=payload)
        logging.info(f"Cloudflare response: {response.status_code} - {response.text}")  # Log the response body
        response.raise_for_status()
        result = response.json()
        if response.status_code in [200, 201] and result.get("success"):
            return True
        else:
            logging.error(f"Cloudflare Error: {result}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error updating Cloudflare: {e}")
        return False
    except json.JSONDecodeError:
        logging.error("Invalid JSON response from Cloudflare")
        return False

def send_to_discord(ip, ip_changed, logs=None):
    if ip_changed:
        payload = {"content": f"New Public IP: {ip}"}
    else:
        payload = {"content": "Your IP hasn't changed since the last update."}
    
    if logs:
        payload["content"] += f"\n\nLatest Logs:\n{logs}"

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        if response.status_code == 204:
            return True
        else:
            logging.error(f"Discord Webhook Error: {response.status_code}, {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error sending to Discord: {e}")
        return False

def get_new_log_entries():
    # Read the last read position from file
    if os.path.exists(LAST_READ_POSITION_FILE):
        with open(LAST_READ_POSITION_FILE, "r") as f:
            last_position = int(f.read().strip())
    else:
        last_position = 0

    # Read the new log entries
    new_entries = ""
    try:
        with open(LOG_FILE, "r") as f:
            f.seek(last_position)  # Seek to the last read position
            new_entries = f.read()  # Read new content
            new_position = f.tell()  # Get the current position

        # Save the new position to track for the next read
        with open(LAST_READ_POSITION_FILE, "w") as f:
            f.write(str(new_position))

    except Exception as e:
        logging.error(f"Error reading logs: {e}")
        return None

    return new_entries

def main():
    # Get the current public IP from Cloudflare DNS record
    current_dns_ip = get_cloudflare_current_ip()
    if not current_dns_ip:
        logging.error("Failed to fetch the current IP from Cloudflare")
        send_to_discord("N/A", ip_changed=True, logs="Failed to fetch Cloudflare IP")
        return

    # Get the current public IP from the internet
    public_ip = get_public_ip()
    if not public_ip:
        logging.error("Failed to get public IP")
        send_to_discord("N/A", ip_changed=True, logs="Failed to fetch public IP")
        return

    # Read the last known IP from the file
    last_ip = read_last_ip()

    # Check if the public IP differs from the current DNS IP or the last IP
    if public_ip == current_dns_ip and public_ip == last_ip:
        logging.info("IP hasn't changed, no update needed.")
        return

    # If there is a change, update Cloudflare DNS and the last_ip.txt file
    if update_cloudflare_dns(public_ip):
        logging.info(f"Updated Cloudflare DNS to {public_ip}")
        write_last_ip(public_ip)  # Update the last_ip.txt with the new IP
    else:
        logging.error("Failed to update Cloudflare")
        logs = get_new_log_entries()
        send_to_discord(public_ip, ip_changed=True, logs=logs)

if __name__ == "__main__":
    main()
