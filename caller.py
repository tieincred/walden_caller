from twilio.rest import Client
import os
import json
# Load your environment variables (if using .env files)
from dotenv import load_dotenv
load_dotenv()

# Twilio setup
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_NUMBER')
target_number = os.getenv('TARGET_NUMBER')

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

client = Client(account_sid, auth_token)

call = client.calls.create(
    to=target_number,
    from_=twilio_number,
    url="https://e675-2401-4900-1cbc-1a58-fb21-bf73-e8e-821d.ngrok-free.app/start-call"  # URL to your Flask app's /start-call endpoint
)

print(f"Call initiated with SID: {call.sid}")
