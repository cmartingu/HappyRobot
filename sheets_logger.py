import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # lo pondrás en Render
SHEET_NAME = "Sheet1"

def append_to_sheet(data):
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    row = [
        data.get("call_id", ""),
        data.get("carrier_name", ""),
        data.get("agreed_price", ""),
        data.get("load_id", ""),
        data.get("sentiment", ""),
        data.get("outcome", "")
    ]

    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [row]}
    ).execute()
