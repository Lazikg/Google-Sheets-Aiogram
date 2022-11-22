from googleapiclient.discovery import build
from google.oauth2 import service_account


# If modifying these scopes, delete the file token.json.
SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)


# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1PB_k0VZf9zRt2QjKKqCVLMDFZ2bLwrvExz3gQfN61Yc'
SAMPLE_RANGE_NAME = "Salary!A1:Q20"

service = build('sheets', 'v4', credentials=creds)

def google_sheet_data():

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()

    values = result.get('values', [])

    return values