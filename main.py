#!/bin/env python3

# to speech-to-text
import whisper
# for google sheet access
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
# for Credentials
from dotenv import load_dotenv
load_dotenv()
# other modules
import os
import requests
import json
from pprint import pprint
from logger import logger
import time

def load_config():
    
    
    while True:
        
        CONFIG_FILE = input("\nEnter your json config file or path: ").strip()
        
        try:
            if not CONFIG_FILE.endswith(".json"):
                print("\nEnter valid path or file\n")
                continue
            
            else:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    # print(f"Config - \n{config}\n")
                    keys = config.keys()
                    # print(f"keys - \n{keys}\n")
                    print("")
                    print("Checking Initial JSON file...")
                    time.sleep(3)
                    print("Keys: ")
                    for key in keys:
                        if key.strip() == "":
                            logger.info("\n\033[93mThese is an Empty Key!\033[0m\n")
                            break
                        else:
                            print(f"- {key}")
                print("")
        
            return config
        
        except FileNotFoundError:
            logger.error("\033[91mNo such json File!\033[0m\n")
            continue
        
        except json.decoder.JSONDecodeError:
            logger.critical("\033[91mJson is Broken\033[0m\n")
            continue
            
config = load_config()

# print(f"{config}\n")
json_val = list(config.values())
print("Values: ")
for val in json_val:
    print(f"- {val}")
 
API_KEY = config.get("openrouter_api_key")
AI_MODEL = config.get("ai_model_name")
AI_URL = config.get("ai_api_url")
GOOGLE_SHEET_ID = config.get("google_sheets_id")
GOOGLE_SHEET_NUMBER = config.get("google_sheet_number")

## == Main Logic ==

path = input("\nEnter the Audio File Path: ").strip()
SERVICE_ACCOUNT_FILE = input("\nEnter your Service Account Credential json file or its path: ").strip()

while True:
    
    required_keys = [
                "type", "project_id", "private_key_id", "private_key", "client_email", "client_id", "auth_uri", "token_uri",
                "auth_provider_x509_cert_url", "client_x509_cert_url", "universe_domain"
                ]
    try:
        if SERVICE_ACCOUNT_FILE.endswith(".json"):
            with open(SERVICE_ACCOUNT_FILE, "r") as f:
                service_account_file_details = json.load(f)
                service_account_keys = list(service_account_file_details.keys())
                print("\nChecking Google Credentials....")
                time.sleep(3)
                if not all(key in service_account_keys for key in required_keys):
                    print("\nInvalid Google Credentials, try again after a check\n")
                    exit(1)
                else:
                    print("\n\033[93mGoogle Credentials Good to GO\033[0m\n")
                    break
        else:
            print("\nPlease enter Google Credentials.json file or path\n")
            
    except FileNotFoundError:
        logger.error("\n\033[91mFile not found\033[0m\n")
        continue
    
    except json.decoder.JSONDecodeError:
        logger.critical("\n\033[91mJson is Broken\033[0m\n")
        continue
    
if (path.endswith(".mp3/") or path.endswith(".mkv/")):
    print("")
    logger.error("\033[91mPlease Enter Valid Path\033[0m\n")
    
elif not (path.endswith(".mp3") or path.endswith(".mkv")):
    logger.warning("\n\033[91mnly .mp3 and .mkv files are supported\033[0m\n")

else:
    time.sleep(2)
    print("\nTranslating Voice into Text....")
    model = whisper.load_model("base")
    def transcribe_audio(file_path):
        result = model.transcribe(file_path, fp16=False, language="en")
        return result["text"]
    result = model.transcribe(f"{path}", fp16=False, language="en")
    print(f"\n{result['text']}")
    extracted_text = result["text"]
    print("")
    logger.info("\033[93mText Extracted\033[0m\n")

    
## Google Sheet Integration
            
# Define the scope (Google Sheets + Drive)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]

# Authenticate using the service account
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Sheets API service
service = build('sheets', 'v4', credentials=creds)
SPREADSHEET_ID = GOOGLE_SHEET_ID

# RANGE_NAME = 'Sheet1'
while True:
    try:
        RANGE_NAME = f'Sheet{GOOGLE_SHEET_NUMBER}'
        break
    
    except ValueError:
        print("\nEnter Sheet Number Only\n") 
        continue

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            range=RANGE_NAME).execute()
values = result.get('values', [])

if not values:
    logger.error('\033[91mNo data found\033[0m\n')
else:
    print(values[0])
    print("")
    logger.info("\033[93mColumns Printed\033[0m\n")
    
    ## AI Integration
        
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "http://localhost",
        "Content-Type": "application/json"
    }
    data = {
        "model": f"{AI_MODEL}",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes and extracts lead data that user specify in JSON format ONLY."
            },
            {
                "role": "user",
                "content": f"""
                Summarize this {extracted_text}, ONLY FETCH {values[0]} in little brief. 
                If there is no detail regarding any column just put 'none' in it.
                Then convert this data into proper json format, DO NOT return anything outside the json
                """
            }
        ],
    }
    
    ai_url = AI_URL
    data = requests.post(f"{ai_url}", headers=headers, json=data)
    response = data.json()
    # pprint(response\n)
    
    try:
        if data.status_code == 200:
            ai_summary = response['choices'][0]['message']['content']
            print(f"\n{ai_summary}\n")
            print("")
            logger.info("\033[93mGot the AI Summary\033[0m\n")
            ai_json = json.loads(ai_summary)
        
        elif data.status_code == 404:
            print("")
            logger.error("\033[91mNothing Found, Wrong URL Used\033[0m\n")
            exit(1)
        
        elif data.status_code == 401:
            print("")
            logger.error("\033[91mInvalid API Key\033[0m\n")
            exit(1)
            
        elif data.status_code == 500:
            print("")
            logger.error("\033[91mServers are down\033[0m\n")
            exit(1)
            
        elif data.status_code == 429:
            print("")
            logger.error("\033[91mYou hit your API limit\033[0m\n")
            exit(1)
            
    except requests.exceptions.HTTPError as http_err:
        print("")
        logger.error(f"\033[91mHTTP Error Occured:: {http_err}\033[0m\n")
        exit(1)
        
    except requests.exceptions.RequestException as req_err:
        logger.error(f"\033[91mRequest Error Occured:: {req_err}\033[0m\n")
        
    except Exception as e:
        logger.critical(f"\033[91mUnexpected Error:: {e}\033[0m")
    


## Google Sheet Append Process

gc = gspread.authorize(creds)
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(RANGE_NAME)
headers = worksheet.row_values(1)
print(f"Headers : {headers}\n")
print(f"Worksheet: {worksheet}\n")

row_append = [ai_json.get(h.strip(), "") for h in headers]

try:
    if isinstance(ai_json, dict):
        worksheet.append_row(row_append)
        logger.info("\033[93mRow Appended\033[0m")
        print("\n\033[92mData Pushed Successfully...\033[0m\n")
        exit(1)
    
except Exception as e:
    logger.error(f"\033[91mAI Json Error:: {e}\n\033[0m")