import sys
import os

# Ensure the 'src' directory is in the Python path
sys.path.append('src')

# We need to load the environment variables from the .env file
from dotenv import load_dotenv
load_dotenv()

# Import the specific function we want to test from your code
from src.crm_connector import create_note_on_deal
from src.config import PIPEDRIVE_COMPANY_DOMAIN, PIPEDRIVE_API_TOKEN

def direct_test():
    """
    A direct, simple test to verify the Pipedrive note creation functionality.
    """
    print("--- Starting Direct Pipedrive API Test ---")

    # --- Configuration Check ---
    # First, let's print the configuration to make sure it's loaded correctly.
    # We'll only show a part of the API token for security.
    print(f"✅ Loaded Pipedrive Domain: '{PIPEDRIVE_COMPANY_DOMAIN}'")
    if PIPEDRIVE_API_TOKEN:
        print(f"✅ Loaded Pipedrive API Token starting with: '{PIPEDRIVE_API_TOKEN[:6]}...'")
    else:
        print("❌ CRITICAL: PIPEDRIVE_API_TOKEN is NOT loaded. Check your .env file.")
        return

    # --- Test Parameters ---
    target_deal_id = 3
    test_content = "This is a direct test note from the script. If you see this, the connection is working."
    
    print(f"\nAttempting to add a note to Deal ID: {target_deal_id}...")
    print(f"Content of the note: '{test_content}'")

    # --- The API Call ---
    # We call the exact same function the agent uses.
    response = create_note_on_deal(deal_id=target_deal_id, content=test_content)

    # --- The Result ---
    # We will print the FULL response from Pipedrive. This is the most important part.
    print("\n--- Pipedrive API Response ---")
    if response:
        print("✅ Function returned a success-like response.")
        print("Full Response Body:")
        print(response) # This will print the entire dictionary returned by the API
    else:
        print("❌ Function returned a failure-like response (None).")
        print("   This likely means an exception occurred. Check the error message above.")
        
    print("\n--- Test Complete ---")
    print("Please check for the test note in Pipedrive on Deal ID 3 now.")

if __name__ == "__main__":
    direct_test()