import requests
import time
from twilio.rest import Client
import time


def download_audio_http(recording_sid, auth_token, account_sid):
    start_time = time.time()
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording_sid}.mp3"
    response = requests.get(url, auth=(account_sid, auth_token))
    if response.status_code == 200:
        with open(f"{recording_sid}.mp3", "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed to download: {response.status_code}")
    end_time = time.time()
    return end_time - start_time


def download_audio_sdk(recording_sid, auth_token, account_sid):
    start_time = time.time()
    client = Client(account_sid, auth_token)
    recording = client.recordings(recording_sid).fetch()
    audio_url = recording.uri.replace(".json", ".mp3")
    response = requests.get(f"https://api.twilio.com{audio_url}", auth=(account_sid, auth_token))
    if response.status_code == 200:
        with open(f"{recording_sid}.mp3", "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed to download: {response.status_code}")
    end_time = time.time()
    return end_time - start_time

def benchmark_method(method, *args, iterations=10):
    times = [method(*args) for _ in range(iterations)]
    return sum(times) / len(times)

import os
from dotenv import load_dotenv
load_dotenv()
# Replace with your Twilio account credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
recording_sid = "REe7123a593c8963bb44fdf526ebfe6a7d"

# Replace these with actual credentials and a valid recording SID
http_time = benchmark_method(download_audio_http, recording_sid, auth_token, account_sid)
sdk_time = benchmark_method(download_audio_sdk, recording_sid, auth_token, account_sid)

print(f"HTTP Request Time: {http_time} seconds")
print(f"SDK Request Time: {sdk_time} seconds")