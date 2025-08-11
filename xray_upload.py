#!/usr/bin/env python3
import os
import subprocess
import base64
import json
import sys
import shutil
import requests

# Jenkins will pass these as environment variables
XRAY_CLIENT_ID = os.getenv("XRAY_CLIENT_ID")
XRAY_CLIENT_SECRET = os.getenv("XRAY_CLIENT_SECRET")
TEST_EXEC_KEY = os.getenv("TEST_EXEC_KEY", "IT-4")
TEST_KEY = os.getenv("TEST_KEY", "IT-3")

def run_cmd(cmd, check=True):
    """Run a shell command and optionally fail on error."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        sys.exit(result.returncode)

def ensure_python():
    """Ensure Python and pip are available."""
    if not shutil.which("python3"):
        print("Python3 is not installed. Please install it manually.")
        sys.exit(1)
    if not shutil.which("pip3"):
        print("pip3 is not installed. Installing...")
        run_cmd("apt-get update && apt-get install -y python3-pip")

def install_requirements():
    """Install dependencies from requirements.txt."""
    if os.path.exists("requirements.txt"):
        run_cmd("pip3 install -r requirements.txt")
    else:
        print("requirements.txt not found. Skipping install.")

def run_tests():
    """Run pytest and capture logs."""
    run_cmd("pytest --tb=short -q tests/ > logs.txt || true", check=False)

def prepare_xray_json():
    """Create results.json for Xray."""
    if not os.path.exists("logs.txt"):
        print("logs.txt not found, creating empty file.")
        open("logs.txt", "w").close()

    with open("logs.txt", "rb") as f:
        logs_base64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "testExecutionKey": TEST_EXEC_KEY,
        "info": {
            "summary": "Version creation pipeline results",
            "description": "Automated execution of version creation test"
        },
        "tests": [
            {
                "testKey": TEST_KEY,
                "status": "FAIL",  # You can dynamically set based on pytest exit code
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

    with open("results.json", "w") as f:
        json.dump(payload, f, indent=2)

    print("results.json created.")

def upload_to_xray():
    """Authenticate and upload results to Xray."""
    if not XRAY_CLIENT_ID or not XRAY_CLIENT_SECRET:
        print("Xray credentials not set in environment variables.")
        sys.exit(1)

    print("Authenticating with Xray...")
    auth_resp = requests.post(
        "https://xray.cloud.getxray.app/api/v2/authenticate",
        headers={"Content-Type": "application/json"},
        json={"client_id": XRAY_CLIENT_ID, "client_secret": XRAY_CLIENT_SECRET}
    )

    if auth_resp.status_code != 200:
        print(f"Auth failed: {auth_resp.text}")
        sys.exit(1)

    token = auth_resp.text.strip('"')

    print("Uploading results to Xray...")
    with open("results.json", "rb") as f:
        upload_resp = requests.post(
            "https://xray.cloud.getxray.app/api/v2/import/execution",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            data=f.read()
        )

    print(f"Xray response: {upload_resp.status_code} - {upload_resp.text}")

def main():
    ensure_python()
    install_requirements()
    run_tests()
    prepare_xray_json()
    upload_to_xray()

if __name__ == "__main__":
    main()
