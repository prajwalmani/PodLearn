# Check Listen Notes API and AssemblyAI API documentation for endpoints and API keys
# 
# For Listen Notes API:
# Ensure you have an API key from Listen Notes. Documentation for endpoints and API keys can be found at:
# https://www.listennotes.com/api/docs/
# 
# For AssemblyAI API:
# Ensure you have an API key from AssemblyAI. Documentation for endpoints and API keys can be found at:
# https://www.assemblyai.com/app

import requests
import os
from dotenv import load_dotenv
from database import create_database,check_episode_exists,insert_episode
import time 

load_dotenv()
create_database()

# Define API endpoints
url_episodes_endpoint='https://listen-api.listennotes.com/api/v2/episodes'
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

#Episode ID for the episode to process from listen notes
#this episode talks about how self care is making worst of us
episode_id='856027fd92734ebf928aa6b07e9813c8'

transcript=check_episode_exists(episode_id=episode_id)

if transcript is None:
    # If transcript does not exist, fetch and transcribe the episode

    try: 
        # code get audio url from listen notes api
        headers = {
        'X-ListenAPI-Key':os.getenv('LISTEN_NOTES_API_KEY')
        }

        url = f"{url_episodes_endpoint}/{episode_id}"

        response = requests.request('GET', url, headers=headers)
        data = response.json()
        audio_url = data['audio']

        transcript_request = {
            'audio_url': audio_url,
            'auto_chapters': False
        }

        headers = {
            "authorization": os.getenv('aai.settings.api_key'),
            "content-type": "application/json"
        }

        transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
        transcript_id = transcript_response.json()['id']
        polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        
        # Poll for transcription completion

        while True:
            transcription_result = requests.get(polling_endpoint, headers=headers).json()

            if transcription_result['status'] == 'completed' and transcription_result['text'] is not None:
                transcript_text=transcription_result['text']
                # Insert episode details into the database
                insert_episode(episode_id,audio_url,transcript_text)
                break
            elif transcription_result['status'] == 'error':
                raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

            else:
                time.sleep(3)
    except Exception as e:
        print(f"Error occurred: {e}")
        raise SystemExit(1)

else:
        print("Episode already in the database")







    



