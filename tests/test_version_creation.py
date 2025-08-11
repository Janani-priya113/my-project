import pytest
import logging
import random
import time

# Configure logging
logging.basicConfig(
    filename="logs.txt",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def simulate_version_creation():
    """
    Simulates a version creation process.
    Returns True if successful, False if failed.
    """
    logging.info("Starting version creation process...")
    time.sleep(1)

    # Random fail simulation (20% chance to fail)
    result = random.choice([True, True, True, True, False])

    if result:
        logging.info("Version creation successful!")
    else:
        logging.error("Version creation failed due to unexpected error.")

    return result

def test_version_creation():
    """
    Test to check if version creation works.
    """
    success = simulate_version_creation()
    assert success, "Version creation failed. Check logs.txt for details."
