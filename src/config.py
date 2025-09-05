import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the parent directory
# This makes the script runnable from the project root.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- LLM Configuration ---
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_API_BASE = os.getenv("NEBIUS_API_BASE")

LLM_MODEL_NAME = "openai/gpt-oss-120b" 
EMBEDDING_MODEL_NAME = "intfloat/e5-mistral-7b-instruct"
# --- Vector DB Configuration ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "sachin08"
# --- CRM Configuration ---
PIPEDRIVE_API_TOKEN = os.getenv("PIPEDRIVE_API_TOKEN")

PIPEDRIVE_COMPANY_DOMAIN = os.getenv("PIPEDRIVE_COMPANY_DOMAIN")
# --- Validation ---
# A simple check to ensure that all critical environment variables are loaded.
# In a real production system, this could involve more complex validation.
def validate_config():
    """Validates that all necessary configuration variables are set."""
    required_vars = {
        "NEBIUS_API_KEY": NEBIUS_API_KEY,
        "NEBIUS_API_BASE": NEBIUS_API_BASE,
        "PINECONE_API_KEY": PINECONE_API_KEY,
        "PIPEDRIVE_API_TOKEN": PIPEDRIVE_API_TOKEN,
        "PIPEDRIVE_COMPANY_DOMAIN" : PIPEDRIVE_COMPANY_DOMAIN,
        "PINECONE_INDEX_NAME" : PINECONE_INDEX_NAME ,
        "EMBEDDING_MODEL_NAME": EMBEDDING_MODEL_NAME,
    }
    missing_vars = [key for key, value in required_vars.items() if value is None]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    print("✅ Configuration validated successfully.")


