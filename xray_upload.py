import os
import base64
import json
import requests
import sys

# Read environment variables from Jenkins
XRAY_CLIENT_ID = os.getenv("XRAY_CLIENT_ID")
XRAY_CLIENT_SECRET = os.getenv("XRAY_CLIENT_SECRET")
TEST_EXEC_KEY = "IT-4"   # Xray Test Execution key
TEST_KEY = "IT-3"        # Xray Test case key

if not XRAY_CLIENT_ID or not XRAY_CLIENT_SECRET:
    print("ERROR: Xray credentials not found in environment variables.")
    sys.exit(1)

# Read logs.txt and encode as Base64
try:
    with open("logs.txt", "rb") as log_file:
        logs_base64 = base64.b64encode(log_file.read()).decode("utf-8")
except FileNotFoundError:
    print("ERROR: logs.txt file not found. Run tests before this script.")
    sys.exit(1)

# Prepare results JSON
results = {
    "testExecutionKey": TEST_EXEC_KEY,
    "info": {
        "summary": "Version creation pipeline results",
        "description": "Automated execution of version creation test"
    },
    "tests": [
        {
            "testKey": TEST_KEY,
            "status": "FAIL",  # You can adjust this based on pytest results
            "comment": "Version creation failed - check attached logs",
            "evidences": [
                {
                    "data": logs_base64,
                    "filename": "logs.txt",
                    "contentType": "text/plain"
                }
            ]
        }
    ]
}

# Authenticate with Xray
auth_url = "https://xray.cloud.getxray.app/api/v2/authenticate"
auth_payload = {
    "client_id": XRAY_CLIENT_ID,
    "client_secret": XRAY_CLIENT_SECRET
}

print("Authenticating with Xray...")
auth_response = requests.post(auth_url, json=auth_payload)

if auth_response.status_code != 200:
    print(f"Authentication failed: {auth_response.text}")
    sys.exit(1)

token = auth_response.text.strip('"')
print("Authentication successful.")

# Upload results to Xray
upload_url = "https://xray.cloud.getxray.app/api/v2/import/execution"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("Uploading results to Xray...")
upload_response = requests.post(upload_url, headers=headers, data=json.dumps(results))

if upload_response.status_code == 200:
    print("Results uploaded successfully to Xray.")
else:
    print(f"Upload failed: {upload_response.status_code} - {upload_response.text}")
    sys.exit(1)
