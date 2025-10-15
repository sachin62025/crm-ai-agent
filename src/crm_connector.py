# import os
import requests
import config

BASE_URL = f"https://{config.PIPEDRIVE_COMPANY_DOMAIN}.pipedrive.com/api/v1"
API_TOKEN = config.PIPEDRIVE_API_TOKEN


def get_recent_deals(limit: int = 5):
    """
    Fetch recent deals from Pipedrive REST API.
    """
    try:
        url = f"{BASE_URL}/deals"
        params = {"api_token": API_TOKEN, "sort": "add_time DESC", "limit": limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching deals: {e}")
        return []


def create_note_on_deal(deal_id: int, content: str):
    """
    Creates a new note associated with a specific deal ID in Pipedrive.

    Args:
        deal_id (int): The ID of the deal to add the note to.
        content (str): The text content of the note.

    Returns:
        dict: The API response from Pipedrive, or None if it failed.
    """
    try:
        url = f"{BASE_URL}/notes"
        params = {"api_token": API_TOKEN}
        payload = {"content": content, "deal_id": deal_id}
        response = requests.post(url, params=params, json=payload)
        response.raise_for_status()
        print(f"✅ Successfully created note on deal ID {deal_id}.")
        return response.json().get("data")
    except Exception as e:
        print(f"❌ Error creating note on deal ID {deal_id}: {e}")
        return None


def update_deal_status(deal_id: int, status: str):
    """
    Updates the status of a specific deal in Pipedrive.

    Args:
        deal_id (int): The ID of the deal to update.
        status (str): The new status. Must be one of 'open', 'won', 'lost'.

    Returns:
        dict: The API response from Pipedrive, or None if it failed.
    """
    if status not in ["open", "won", "lost"]:
        print(
            f"❌ Invalid status provided: '{status}'. Must be 'open', 'won', or 'lost'."
        )
        return None

    try:
        url = f"{BASE_URL}/deals/{deal_id}"
        params = {"api_token": API_TOKEN}
        payload = {"status": status}
        response = requests.put(url, params=params, json=payload)
        response.raise_for_status()
        print(f"✅ Successfully updated status for deal ID {deal_id} to '{status}'.")
        return response.json().get("data")
    except Exception as e:
        print(f"❌ Error updating status for deal ID {deal_id}: {e}")
        return None


if __name__ == "__main__":
    print("--- Running a direct test of the CRM Connector ---")
    deals = get_recent_deals()
    if deals:
        print(f"✅ Successfully fetched {len(deals)} deals:")
        for i, deal in enumerate(deals, start=1):
            title = deal.get("title", "No Title")
            value = deal.get("value", 0)
            currency = deal.get("currency", "")
            print(f"{i}. {title} - {value} {currency}")
    else:
        print("⚠️ No deals returned (check if your CRM has deals).")
