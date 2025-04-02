# Script to scrape Url and paste formatted text to Discord

Simple Python script to scrape a devotional website and parse the text through webhook to discord. audio-converter.py converts the stored text using free TTS models and then sends the converted audio file via the same webhook, just incase you're not in the reading mood.


## Current Deployments
- Running the script using n8n automation tool. Script is set using cron to run daily

## Future Deployments

- Use UptimeKuma as a trigger for N8N. Kuma can scour the url for keywords like the current date and then send trigger to n8n to begin workflow. This way the script will activate only after a new article has been posted...