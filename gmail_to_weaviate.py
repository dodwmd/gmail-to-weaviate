import os
import base64
import argparse
import time
from email.utils import parseaddr, parsedate_to_datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import weaviate
import logging
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Weaviate setup
weaviate_url = os.getenv('WEAVIATE_URL', 'http://localhost:8080')
client = weaviate.Client(weaviate_url)


def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            logger.error(f"Error reading token.json: {e}")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def create_weaviate_schema():
    schema = {
        "classes": [{
            "class": "Email",
            "description": "An email message",
            "properties": [
                {"name": "subject", "dataType": ["string"]},
                {"name": "body", "dataType": ["text"]},
                {"name": "sender", "dataType": ["string"]},
                {"name": "date", "dataType": ["date"]},
                {"name": "gmail_id", "dataType": ["string"]}
            ]
        }]
    }
    client.schema.create(schema)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_emails(service, max_results=100, page_token=None):
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results, pageToken=page_token).execute()
        messages = results.get('messages', [])
        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                add_to_weaviate(msg)
            except HttpError as e:
                logger.error(f"Error fetching message {message['id']}: {str(e)}")

        next_page_token = results.get('nextPageToken')
        return next_page_token
    except HttpError as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise


def add_to_weaviate(email):
    try:
        gmail_id = email['id']
        # Check if email already exists
        result = (
            client.query
            .get("Email", ["gmail_id"])
            .with_where({
                "path": ["gmail_id"],
                "operator": "Equal",
                "valueString": gmail_id
            })
            .do()
        )

        if result['data']['Get']['Email']:
            logger.info(f"Email with ID {gmail_id} already exists in Weaviate. Skipping.")
            return

        client.data_object.create(
            "Email",
            {
                "subject": get_subject(email),
                "body": get_body(email),
                "sender": get_sender(email),
                "date": get_date(email),
                "gmail_id": gmail_id
            }
        )
        logger.info(f"Added email with subject: {get_subject(email)}")
    except Exception as e:
        logger.error(f"Error adding email to Weaviate: {str(e)}")


def get_subject(email):
    headers = email['payload']['headers']
    return next((header['value'] for header in headers if header['name'].lower() == 'subject'), '')


def get_body(email):
    try:
        if 'parts' in email['payload']:
            parts = email['payload']['parts']
            body = next((part['body']['data'] for part in parts if part['mimeType'] == 'text/plain'), '')
        else:
            body = email['payload']['body']['data']
        return base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8')
    except Exception as e:
        logger.error(f"Error decoding email body: {str(e)}")
        return ""


def get_sender(email):
    headers = email['payload']['headers']
    from_header = next((header['value'] for header in headers if header['name'].lower() == 'from'), '')
    _, sender_email = parseaddr(from_header)
    return sender_email


def get_date(email):
    headers = email['payload']['headers']
    date_header = next((header['value'] for header in headers if header['name'].lower() == 'date'), '')
    try:
        return parsedate_to_datetime(date_header).isoformat()
    except Exception as e:
        logger.error(f"Error parsing date: {str(e)}")
        return ""


def main(args):
    try:
        create_weaviate_schema()
    except weaviate.exceptions.UnexpectedStatusCodeException:
        logger.info("Weaviate schema already exists")

    service = get_gmail_service()
    page_token = None
    total_processed = 0

    while total_processed < args.max_emails:
        page_token = fetch_emails(service, min(args.batch_size, args.max_emails - total_processed), page_token)
        total_processed += args.batch_size
        if not page_token:
            break
        time.sleep(1)  # Avoid hitting rate limits

    logger.info(f"Processed {total_processed} emails")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch emails from Gmail and store in Weaviate')
    parser.add_argument('--max_emails', type=int, default=1000, help='Maximum number of emails to process')
    parser.add_argument('--batch_size', type=int, default=100, help='Number of emails to fetch in each batch')
    args = parser.parse_args()
    main(args)
