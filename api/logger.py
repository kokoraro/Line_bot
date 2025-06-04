import os
import json
import gspread
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# Load environment variables (only needed for local dev)
load_dotenv()

SHEET_ID = "1QfLOqsYzYl9pUJU8hD4SVRb6vFLClBY5nnYyeBoMAp4"
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")

# Validate and parse JSON from env var
if not SERVICE_ACCOUNT_JSON:
    raise ValueError("Missing environment variable: SERVICE_ACCOUNT_JSON")

try:
    service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
except json.JSONDecodeError as e:
    raise ValueError("Invalid JSON in SERVICE_ACCOUNT_JSON") from e

# Define scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Authenticate using dict instead of file
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)

# Open spreadsheet
sheet = client.open_by_key(SHEET_ID).get_worksheet(0)

# Log function
def log_to_sheet(user_id: str, user_msg: str, bot_reply: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, user_id, user_msg, bot_reply, "TRUE"])
