import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch your ElevenLabs API Key from the .env file
API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

def convert_text_to_audio_with_elevenlabs(text, output_filename="devotional_audio.mp3"):
    # Define headers for the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Define the body of the API request (change voice settings as per your needs)
    data = {
        "text": text,  # The text you want to convert to speech
        "voice": "en_us_male",  # You can change this to 'en_us_female' or other available voices
        "model_id": "eleven_monolingual_v1",  # Default model ID, can be adjusted for better quality
        "temperature": 0.7,  # Control for speech randomness (0-1)
    }

    # Make the API request to ElevenLabs to generate audio
    response = requests.post(ELEVENLABS_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        # Save the audio file from the response
        with open(output_filename, 'wb') as audio_file:
            audio_file.write(response.content)
        print(f"Audio saved as {output_filename}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Example usage: 
# After scraping the text and saving it to 'devotional_output.txt', 
# you can call the function to convert the text to audio

with open("devotional_output.txt", "r", encoding="utf-8") as file:
    text = file.read()

convert_text_to_audio_with_elevenlabs(text)
