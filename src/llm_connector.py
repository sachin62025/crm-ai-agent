from langchain_openai import ChatOpenAI
# import config
from . import config

def get_llm(temperature: float = 0.0):
    """
    Initializes and returns the LLM client configured for Nebius AI Studio.
    """
    # --- START DEBUGGING BLOCK ---
    print("--- Debugging Information ---")
    print(f"Attempting to connect to API Base: '{config.NEBIUS_API_BASE}'")
    # We print only a portion of the key for security
    if config.NEBIUS_API_KEY:
        print(f"Using API Key starting with: '{config.NEBIUS_API_KEY[:8]}...'")
    else:
        print("API Key is NOT loaded.")
    print(f"Using Model Name: '{config.LLM_MODEL_NAME}'")
    print("---------------------------")
    # --- END DEBUGGING BLOCK ---

    # This works because Nebius provides an OpenAI-compatible API endpoint.
    llm = ChatOpenAI(
        # Using the latest parameter names for consistency
        model_name=config.LLM_MODEL_NAME,
        openai_api_key=config.NEBIUS_API_KEY,
        openai_api_base=config.NEBIUS_API_BASE,
        temperature=temperature,
    )
    return llm


# This block allows us to test the module directly
if __name__ == "__main__":
    print("--- Running a direct test of the LLM Connector ---")
    try:
        llm_instance = get_llm(temperature=0.1)

        prompt = "What are the three core components of a Retrieval-Augmented Generation (RAG) system?"
        print(f"Sending prompt: '{prompt}'")

        response = llm_instance.invoke(prompt)

        print("\n--- LLM Response ---")
        print(response.content)
        print("--------------------")

        if response.content and "retrieval" in response.content.lower():
            print("\n✅ LLM connection test successful. Received a relevant response.")
        else:
            print(
                "\n⚠️ LLM connection worked, but response seems irrelevant. Check model compatibility."
            )

    except Exception as e:
        print(f"\n❌ LLM connection failed. Error: {e}")
        print(
            "Please check your NEBIUS_API_KEY, NEBIUS_API_BASE, and model name in the .env file."
        )
