import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
from dotenv import load_dotenv


def send_to_discord(webhook_url, content):
    max_length = 2000

    while content:
        # Find the split point at the last full stop within 2000 characters
        if len(content) > max_length:
            split_point = content[:max_length].rfind('.')
            if split_point == -1:
                split_point = max_length  # No full stop, break at max length
        else:
            split_point = len(content)

        # Prepare the message and reduce the content
        message = content[:split_point + 1].strip()
        content = content[split_point + 1:].strip()

        # Send the message to Discord
        payload = {"content": message}
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()


def scrape_latest_open_heavens(url):
    try:
        # Load environment variables
        load_dotenv()
        webhook_url = os.getenv("DISCORD_WEBHOOK")

        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Get the page content
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the latest devotional (first article)
        latest_article = soup.find('article') or soup.find('div', class_='post')
        if not latest_article:
            raise ValueError("Could not find the latest devotional article")

        # Extract and clean the title
        title = latest_article.find('h2') or latest_article.find('h1') or latest_article.find('h3')
        if not title:
            raise ValueError("Could not find devotional title")

        # Process title to remove everything before '-'
        title_text = title.get_text(strip=True)
        topic = re.sub(r'^.*? – ', '', title_text)

        # Get the content
        content = latest_article.find('div', class_='entry-content') or latest_article
        text = content.get_text('\n', strip=True)

        # Process sections
        sections = {
            'MEMORISE': '',
            'READ': '',
            'BIBLE IN ONE YEAR': '',
            'MESSAGE': '',
            'REFLECTION': ''
        }

        current_section = None
        reflection_trigger = None
        lines = text.split('\n')

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
                sections[current_section] = ''
            elif 'ACTION POINT' in line or 'KEY POINT' in line:
                reflection_trigger = 'Action Point' if 'ACTION POINT' in line else 'Key Point'
                current_section = 'REFLECTION'
                reflection_text = line.replace('ACTION POINT:', '').replace('KEY POINT:', '').replace('ACTION POINT', '').replace('KEY POINT', '').strip()
                sections[current_section] = reflection_text
            elif 'HYMN' in line:
                break
            elif current_section:
                sections[current_section] += '\n' + line

        # Format output with current date
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        output = f"DATE: {current_date}\n\n"
        output += f"TOPIC: {topic}\n\n"
        output += f"MEMORISE: \"{sections['MEMORISE']}\"\n\n"
        output += f"READ: {sections['READ']}\n\n"
        output += f"BIBLE IN ONE YEAR: {sections['BIBLE IN ONE YEAR']}\n\n"
        output += f"MESSAGE\n\n"
        output += f"{sections['MESSAGE']}\n\n"
        if reflection_trigger:
            output += f"REFLECTION ({reflection_trigger})\n{sections['REFLECTION']}\n"

        # Save to file
        filename = "devotional_output.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)

        # Send to Discord
        send_to_discord(webhook_url, output)

        return True

    except Exception as e:
        with open("devotional_output.txt", "w", encoding="utf-8") as f:
            f.write(f"Error: {str(e)}")
        return False


# URL to scrape
url = "https://flatimes.com/open-heavens/"

# Get the latest devotional
scrape_latest_open_heavens(url)
