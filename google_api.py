import re
import os
from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup
import requests
from selenium_test import fetch_otp_with_selenium
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request



SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_latest_code(service, user_input):
    
    query = (
        f'from:info@account.netflix.com to:{user_input} '
        'label:unread in:inbox newer_than:15m'
    )
    results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return None

    msg_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    def get_parts(payload):
        if 'parts' in payload:
            for part in payload['parts']:
                yield from get_parts(part)
        else:
            yield payload
    verify_link = None
    body_decoded = ''
    for part in get_parts(msg['payload']):
        mimeType = part.get('mimeType')
        data = part['body'].get('data')
        if data:
            decoded = urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            if mimeType in ['text/plain', 'text/html']:
                 body_decoded += decoded
            link = re.search(r'https://www\.netflix\.com/account/travel/verify\?[^"\s<\]]+', body_decoded)
            if link:
                verify_link = link.group(0)
                print("Netflix Verify Link for otp:", verify_link)
                break
            else: print("No link found")
    #  prevent error if no link found
    if not verify_link:
        print("No Netflix verify link found in email.")
        return None
    otp=''
    # GET CODE USING REQUEST
    response = requests.get(verify_link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        otp_element = soup.find(attrs={"data-uia": "travel-verification-otp"})
        if otp_element:
            print("OTP Code:", otp_element.get_text(strip=True))
            otp=otp_element.get_text(strip=True)
            return otp 
    else: ## GET CODE USING SELENIUM
        return  fetch_otp_with_selenium(verify_link)
    
def get_household_link(service, user_input):
    query = (
        f'from:info@account.netflix.com to:{user_input} '
        'label:unread in:inbox newer_than:15min'
    )
    results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found for household.")
        return None

    msg_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    def get_parts(payload):
        if 'parts' in payload:
            for part in payload['parts']:
                yield from get_parts(part)
        else:
            yield payload

    plain_body_decoded = ''
    html_body_decoded = ''

    for part in get_parts(msg['payload']):
        mimeType = part.get('mimeType')
        data = part['body'].get('data')
        if data:
            decoded = urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            if mimeType == 'text/plain':
                plain_body_decoded += decoded
            elif mimeType == 'text/html':
                html_body_decoded += decoded

     # Extract Netflix verify links
    verify_link = None
    if html_body_decoded:
        soup = BeautifulSoup(html_body_decoded, "html.parser")
        anchors = soup.find_all('a', href=True)

        # Get the 3rd link
        verify_link = anchors[2]['href'].strip() if len(anchors) > 2 else None

        return  verify_link
