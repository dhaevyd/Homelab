# Import necessary libraries for web scraping, audio conversion, and Discord webhook integration
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
from dotenv import load_dotenv
from gtts import gTTS

# Function to send text content to Discord, ensuring each payload is under 2000 characters
# Splits the message at the last full stop within the limit to keep sentences intact

def send_to_discord(webhook_url, content):
    max_length = 2000

    while content:
        # Find the appropriate split point (last full stop before 2000 characters)
        if len(content) > max_length:
            split_point = content[:max_length].rfind('.')
            if split_point == -1:
                split_point = max_length
        else:
            split_point = len(content)

        # Prepare the message chunk and send to Discord
        message = content[:split_point + 1].strip()
        content = content[split_point + 1:].strip()

        payload = {"content": message}
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

# Function to send an audio file to Discord
# Opens the audio file and sends it as a file attachment to the webhook

def send_audio_to_discord(webhook_url, file_path):
    with open(file_path, "rb") as audio_file:
        files = {"file": audio_file}
        response = requests.post(webhook_url, files=files)
        response.raise_for_status()

# Function to convert a given text to audio using gTTS and save as an MP3 file

def convert_text_to_audio(text, filename):
    tts = gTTS(text, lang='en')
    tts.save(filename)

# Main function to scrape the latest Open Heavens devotional and send both text and audio to Discord

def scrape_latest_open_heavens():
    try:
        # Load environment variables from .env file
        load_dotenv()
        url = os.getenv("DEVOTIONAL_URL")
        webhook_url = os.getenv("DISCORD_WEBHOOK")

        # Set headers to mimic a browser to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Fetch the latest devotional page content
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the latest devotional article
        latest_article = soup.find('article') or soup.find('div', class_='post')
        if not latest_article:
            raise ValueError("Could not find the latest devotional article")

        # Extract the devotional title and topic
        title = latest_article.find('h2') or latest_article.find('h1') or latest_article.find('h3')
        if not title:
            raise ValueError("Could not find devotional title")

        title_text = title.get_text(strip=True)
        topic = re.sub(r'^.*? – ', '', title_text)

        # Extract the content of the devotional
        content = latest_article.find('div', class_='entry-content') or latest_article
        text = content.get_text('\n', strip=True)

        # Initialize sections to store different parts of the devotional
        sections = {'MEMORISE': '', 'READ': '', 'BIBLE IN ONE YEAR': '', 'MESSAGE': '', 'REFLECTION': ''}
        current_section = None
        reflection_type = ''
        lines = text.split('\n')

        # Iterate through the text lines and categorize them into sections
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if 'MEMORISE' in line:
                current_section = 'MEMORISE'
                sections[current_section] = line.replace('MEMORISE:', '').strip()
            elif 'READ' in line:
                current_section = 'READ'
                sections[current_section] = line.replace('READ:', '').strip()
            elif 'BIBLE IN ONE YEAR' in line:
                current_section = 'BIBLE IN ONE YEAR'
                sections[current_section] = line.replace('BIBLE IN ONE YEAR:', '').strip()
            elif 'MESSAGE' in line:
                current_section = 'MESSAGE'
                sections[current_section] = line.replace('MESSAGE', '').strip()
            elif any(x in line for x in ['ACTION POINT', 'KEY POINT']):
                reflection_type = 'Action Point' if 'ACTION POINT' in line else 'Key Point'
                current_section = 'REFLECTION'
                reflection_text = line.replace('ACTION POINT:', '').replace('ACTION POINT', '').replace('KEY POINT:', '').replace('KEY POINT', '').strip()
                sections[current_section] = reflection_text
                break
            elif current_section:
                sections[current_section] += '\n' + line

        # Format the output with the current date and structured content
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        output = f"DATE: {current_date}\n\nTOPIC: {topic}\n\nMEMORISE: \"{sections['MEMORISE']}\"\n\nREAD: {sections['READ']}\n\nBIBLE IN ONE YEAR: {sections['BIBLE IN ONE YEAR']}\n\nMESSAGE\n\n{sections['MESSAGE']}\n\nREFLECTION ({reflection_type})\n{sections['REFLECTION']}\n"

        # Save the formatted text to a file
        filename = "devotional_output.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)

        # Send the text content to Discord
        send_to_discord(webhook_url, output)

        # Convert the text to audio and send the audio file to Discord
        audio_filename = "devotional_audio.mp3"
        convert_text_to_audio(output, audio_filename)
        send_audio_to_discord(webhook_url, audio_filename)

        return True

    except Exception as e:
        with open("devotional_output.txt", "w", encoding="utf-8") as f:
            f.write(f"Error: {str(e)}")
        return False

# Run the script to scrape and send the latest devotional
scrape_latest_open_heavens()
