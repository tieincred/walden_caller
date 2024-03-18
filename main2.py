import os
import json
import random
import requests
import logging
from functools import wraps
from time import time
from utils.classify import classifier_zeroshot, classify_faqs
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from utils.transcribe import transcript
from concurrent.futures import ThreadPoolExecutor

# Load your environment variables (if using .env files)
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def log_function_time(func):
    """
    2. Decorator to log the execution time of functions.
    """
    @wraps(func)
    def wrap(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        logging.info(f"{func.__name__} executed in {end_time - start_time} seconds")
        return result
    return wrap

session = requests.Session()
with open('id_url.json', 'r') as file:
    # Load its content and convert it into a Python dictionary
    audio_links = json.load(file)
app = Flask(__name__)
# https://drive.google.com/file/d/1Wpa9mFU8RUFCLjQWwfgP_9JbxntDjyRq/view?usp=sharing
# Replace this with your Google Drive audio file's public URL
GOOGLE_DRIVE_AUDIO_URL = 'https://drive.google.com/uc?export=download&id=1Wpa9mFU8RUFCLjQWwfgP_9JbxntDjyRq'

# Create a session for reuse
# Replace these with your Twilio account credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

print(TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_SID)

# Initialize the Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@log_function_time
def download_audio_http(recording_sid, auth_token=TWILIO_AUTH_TOKEN, account_sid=TWILIO_ACCOUNT_SID):
    start_time = time()
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording_sid}.mp3"
    response = requests.get(url, auth=(account_sid, auth_token))
    if response.status_code == 200:
        with open(f"recordings/{recording_sid}.mp3", "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed to download: {response.status_code}")
    end_time = time()
    return end_time - start_time

def handle_first_conversation(url_link):
        if url_link == 'yes, yeah':
            url_link = audio_links['general_responses']['starter']
            url_link = f"https://drive.google.com/uc?export=download&id={url_link}"
        
        elif url_link == 'busy':
            url_link = audio_links['general_responses']['userbusy']
            url_link = f"https://drive.google.com/uc?export=download&id={url_link}"

        elif url_link == 'I made no such enquiry':
            url_link = audio_links['general_responses']['nosuchquery']
            url_link = f"https://drive.google.com/uc?export=download&id={url_link}"
        
        elif url_link == 'no':
            url_link = audio_links['general_responses']['no']
            url_link = f"https://drive.google.com/uc?export=download&id={url_link}"
        
        return url_link

# Twilio route to initiate the call and play the audio
@app.route("/start-call", methods=['GET', 'POST'])
@log_function_time
def start_call():
    # url_link = request.args.get('data', '')
    
    try:
        with open('detected_class.txt', "r") as file:
            url_link_and_repeat = file.read()
        url_link, repeat = url_link_and_repeat.split(';')
        logging.info(f"so we are responding to first response or to no!")
        if url_link.strip() in ['yes, yeah', 'busy', 'I made no such enquiry', 'no']:
            GOOGLE_DRIVE_AUDIO_URL = handle_first_conversation(url_link)
            response = VoiceResponse()
            # Play the Google Drive audio
            response.play(GOOGLE_DRIVE_AUDIO_URL)
            if url_link == 'yes, yeah':
                logging.info(f"It was nice time to talk so listening what he has to say!")
                response.pause(1)
                # Record the callee's message
                response.record(maxLength=30,timeout=1, action='/handle-recording', playBeep=False)
            else:
                response.hangup()
            return str(response)
        logging.info(f"we are outside everything means user is asking faqs")
        if repeat == 'repeat':
            logging.info(f"user wants to repeat")
            GOOGLE_DRIVE_AUDIO_URL = f"https://drive.google.com/uc?export=download&id={audio_links[url_link]['repeat']}"
        else:
            logging.info(f"user asked about {url_link}")
            GOOGLE_DRIVE_AUDIO_URL = f"https://drive.google.com/uc?export=download&id={audio_links[url_link]['first_response']}"
    except:
        logging.info(f"the call started and we are in EXCEPT of start call.")
        GOOGLE_DRIVE_AUDIO_URL = 'https://drive.google.com/uc?export=download&id=1768Di0Lqj-dh5drv23yb-1FA9sE2V9nd'
        response = VoiceResponse()
        # Play the Google Drive audio
        response.play(GOOGLE_DRIVE_AUDIO_URL)
        response.pause(1)
        # Record the callee's message
        logging.info(f"recording started")
        response.record(maxLength=30,timeout=1, action='/handle-recording', playBeep=False)
        logging.info(f"recording done!")
        return str(response)

    response = VoiceResponse()

    random_element = random.choice(audio_links['general_responses']['anything_else'])
    anything_else_url = f'https://drive.google.com/uc?export=download&id={random_element}'
    # Play the Google Drive audio
    response.play(GOOGLE_DRIVE_AUDIO_URL)
    response.play(anything_else_url)
    response.pause(1)
    # Record the callee's message
    response.record(maxLength=30,timeout=1, action='/handle-recording', playBeep=False)
    
    return str(response)

@app.route("/handle-recording", methods=['POST'])
@log_function_time
def handle_recording():
    recording_url = request.values.get("RecordingUrl", None)
    recording_sid = request.values.get("RecordingSid", None)
    if recording_url and recording_sid:
        download_audio_http(recording_sid)
    start = time()
    input_text = transcript(f"recordings/{recording_sid}.mp3")
    end = time()
    logging.info(f"transcription executed in {end - start} seconds")
    print(input_text)
    print("Nothing?!!!")
    # Open the JSON file for reading
    with open('prev.json', 'r') as file:
        # Load its content and convert it into a Python dictionary
        prev_data = json.load(file)

    if prev_data['conversation done']:
        logging.info(f"That's all conversation we will hangup now.")
        prev_data = {
                "conversation done": False,
                "first_response": True,
                "prev_class": None
            }
        with open('prev.json', 'w') as file:
        # Convert the Python dictionary to a JSON string and write it to the file
            json.dump(prev_data, file, indent=4)
        with open('detected_class.txt', "w") as file:
            file.write('begin;none')
        response = VoiceResponse()
        response.hangup()
        return str(response)
    
    if prev_data['first_response']:
        logging.info(f"This is first response")
        result = classifier_zeroshot(input_text, candidate_labels=['yes, yeah', 'busy', 'I made no such enquiry'], multi_class=False)
        result = result['labels'][0]
        logging.info(f"class found is {result}")
        prev_data['first_response'] = False
        logging.info(f"first response set to false.")
    else:
        logging.info(f"We are in classify faq")
        result = classify_faqs(input_text, prev_data['prev_class'])
        logging.info(f"class found is {result}")

    if result == prev_data['prev_class']:
        result = result + ';repeat'
    else:
        result = result + ';first'
    prev_data['prev_class'] = result.split(';')[0]
    if result=='no':
        logging.info(f"since class was no we update conversation done to True")
        prev_data['conversation done']=True
    print(result)
    # To loop back and play the audio again, you would redirect to "/start-call",
    # but to avoid an endless loop in this example, let's just hang up.
    # Open the file for writing
    with open('prev.json', 'w') as file:
        # Convert the Python dictionary to a JSON string and write it to the file
        json.dump(prev_data, file, indent=4)
    # Writing the sentence to the text file
    with open('detected_class.txt', "w") as file:
        file.write(result)
    
    logging.info(f"saved results and redirected to start-call")
    response = VoiceResponse()
    response.redirect(f"/start-call")
    response.hangup()

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
