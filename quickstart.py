import os
import base64
import re
import time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = get_credentials()

    # Create a set to keep track of already processed emails
    processed_ids = set()

    while True:
        try:
            service = build('gmail', 'v1', credentials=creds)
            result = service.users().messages().list(userId='me').execute()

            messages = result.get('messages')

            if(messages == None):
                break

            for msg in messages:
                msg_id = msg['id']

                # Check if email is already processed
                if msg_id in processed_ids:
                    continue

                txt = service.users().messages().get(userId='me', id=msg_id).execute()
                try:
                    process_message(txt)

                    # Add the email ID to the processed set
                    processed_ids.add(msg_id)
                except Exception as e:
                    print(f"Error processing message with ID {msg_id}: {e}. Inner Except")
                    break

            # Sleep for 60 seconds (or desired duration) before checking again
            time.sleep(60)

        except:
            print(f'An error occurred: Outer Except')
            break


def get_credentials():
    # This is the same logic you provided to get credentials
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def difficulty(subject):
    if "easy" in subject.lower():
        return "Easy"
    elif "medium" in subject.lower():
        return "Medium"
    elif "hard" in subject.lower():
        return "Hard"
    else:
        return "Easy"

def process_message(txt):
    # Extracted the message processing logic into its own function
    payload = txt['payload']
    headers = payload['headers']

    subject, sender = None, None
    for d in headers:
        if d['name'] == 'Subject':
            subject = d['value']
        if d['name'] == 'From':
            sender = d['value']

    if "Daily Coding Problem" in subject:
        parts = payload.get('parts')[0]
        data = parts['body']['data']
        data = data.replace("-", "+").replace("_", "/")
        text = base64.b64decode(data)
        text = text.decode('utf-8')
        text = trimer(text.replace("   "," ").replace("  ", " ").strip())

        # Extracting the solution URL
        match_solution = re.search(r"Here's a solution to yesterday's problem\.\s*<(https?://[^\s]+)>", text)
        solution = match_solution.group(1) if match_solution else "Link not found."

        # Extracting the company name
        match_company = re.search(r"This problem was asked by (\w+).", text)
        company = match_company.group(1) if match_company else "Company not found."

        # Extracting the problem statement
        match_problem = re.search(r"This problem was asked by " + company + r"\.(.*?)Have a great day!", text,
                                  re.DOTALL)
        problem_statement = match_problem.group(1).strip() if match_problem else "Problem statement not found."

        import textwrap

        stringg = textwrap.dedent(f"""
Good morning! Here's a solution to yesterday's problem: 
<{solution}>

Here's your coding interview problem for **{datetime.today().date()}**.

Question Difficulty: **{difficulty(subject)}**
This problem was asked by **{company}**.

**{problem_statement}**

Have a great day!
""")

        send_message_to_discord(stringg)
        print("Last Posted: " + str(datetime.today().date()))

# send_message.py
def send_message_to_discord(msg):
    with open("messages.txt", "a") as file:
        file.write(msg + "\n")
def trimer(s):
    start_idx = s.find("Good morning!")
    end_idx = s.find("Have a great day!")

    if start_idx == -1 or end_idx == -1:
        # One of the phrases was not found, so return the whole string.
        return s

    # Include the length of "Have a great day!" to capture the entire phrase.
    end_idx += len("Have a great day!")

    return s[start_idx:end_idx]

if __name__ == "__main__":
    main()
