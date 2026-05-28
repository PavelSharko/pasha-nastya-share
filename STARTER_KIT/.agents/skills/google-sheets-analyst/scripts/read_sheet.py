#!/usr/bin/env python3
import sys
import json
import re
import os

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Error: Required libraries not found. Please run: pip install gspread google-auth")
    sys.exit(1)

def extract_sheet_id(url_or_id):
    """Extracts the exact Sheet ID from a full Google Sheets URL, or returns it if it's already an ID."""
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url_or_id)
    if match:
        return match.group(1)
    return url_or_id

def read_sheet(sheet_identifier):
    """Reads all data from the first worksheet of the provided Google Sheet."""
    
    # Path to the credentials file (should be in the same folder as this script)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    cred_path = os.path.join(script_dir, 'credentials.json')
    
    if not os.path.exists(cred_path):
        print(f"Error: Credentials file not found at {cred_path}.")
        print("Please follow the setup guide in references/setup_guide.md to create credentials.json.")
        sys.exit(1)

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    try:
        credentials = Credentials.from_service_account_file(cred_path, scopes=scopes)
        gc = gspread.authorize(credentials)
        
        sheet_id = extract_sheet_id(sheet_identifier)
        workbook = gc.open_by_key(sheet_id)
        
        # Open the first worksheet by default
        worksheet = workbook.get_worksheet(0)
        
        # Get all records (list of dictionaries)
        records = worksheet.get_all_records()
        
        if not records:
            # Fallback to getting all values as a 2D array if headers are weird
            values = worksheet.get_all_values()
            print(json.dumps(values, ensure_ascii=False, indent=2))
            return

        print(json.dumps(records, ensure_ascii=False, indent=2))
        
    except gspread.exceptions.APIError as e:
        print(f"Google API Error. Ensure the Service Account email has Viewer access to this sheet. Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_sheet.py <sheet_url_or_id>")
        sys.exit(1)
        
    target_sheet = sys.argv[1]
    read_sheet(target_sheet)