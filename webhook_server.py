# webhook_server.py

import sys
from fastapi import FastAPI, Request, HTTPException
import uvicorn
from langchain_core.messages import HumanMessage

# Add the 'src' directory to the Python path to import our modules
sys.path.append('src')

from src.supervisor import supervisor_graph
from src.config import validate_config

# --- Initialization ---
try:
    # Validate that all config variables are loaded
    validate_config()
    print("✅ Configuration validated successfully.")
    # Initialize the supervisor graph
    app_supervisor = supervisor_graph
    print("✅ Supervisor Graph initialized successfully.")
except Exception as e:
    print(f"❌ Critical Error on Startup: {e}")
    # Exit if the core components can't be initialized
    sys.exit(1)

# Create the FastAPI app instance
app = FastAPI(
    title="Breeze AI Copilot Webhook Server",
    description="Listens for Pipedrive webhooks to trigger proactive AI enrichment.",
)

# --- Webhook Endpoint ---
@app.post("/webhook/pipedrive")
async def pipedrive_webhook_receiver(request: Request):
    """
    This endpoint receives webhook notifications from Pipedrive.
    It's triggered when a new deal is created.
    """
    try:
        data = await request.json()
        print("\n--- ✅ Webhook Received ---")
        print(f"Event Type: {data.get('event')}")
        
        # We are only interested in 'added.deal' events
        if data.get('event') != 'added.deal':
            return {"status": "success", "message": "Event ignored (not a new deal)."}
            
        # Extract relevant information from the webhook payload
        deal_info = data.get("current", {})
        deal_id = deal_info.get("id")
        deal_title = deal_info.get("title")
        org_name = deal_info.get("org_name")
        
        if not all([deal_id, deal_title, org_name]):
            raise HTTPException(status_code=400, detail="Missing deal_id, title, or org_name in webhook payload.")
        
        print(f"   - Deal ID: {deal_id}")
        print(f"   - Deal Title: {deal_title}")
        print(f"   - Organization: {org_name}")
        
        # --- Formulate the Proactive Task for the AI System ---
        task = (
            f"A new CRM deal has been created with ID {deal_id} for the company '{org_name}'. "
            f"Your task is to proactively enrich this deal. "
            f"First, use the Company_Research_Tool to research the company '{org_name}'. "
            f"Then, based on your research findings, create a concise summary note on the deal. "
            f"The note should include key findings like industry, recent news, and buyer intent signals. "
            f"Finally, confirm that the note has been added."
        )

        print(f"--- 🤖 Formulated AI Task ---")
        print(task)
        
        # --- Invoke the Supervisor Agent ---
        print("\n--- 🚀 Invoking Supervisor Agent ---")
        initial_state = {"messages": [HumanMessage(content=task)]}
        
        # The graph will now run the enrichment process automatically
        # We can stream the events to see the flow in real-time in our server logs
        final_state = None
        for event in app_supervisor.stream(initial_state, stream_mode="values"):
            final_state = event
            last_message = event["messages"][-1]
            if last_message.name:
                print(f"\n--- Output from: {last_message.name} ---")
                print(last_message.content)
                print("----------------------------------------")
        
        print("\n--- ✅ Enrichment Process Complete ---")

        # Return a success response to Pipedrive
        return {
            "status": "success",
            "message": "Webhook processed and AI enrichment triggered.",
            "final_agent_response": final_state["messages"][-1].content if final_state else "No final response."
        }
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        # Return an error response to Pipedrive
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# --- Root Endpoint for Health Check ---
@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Breeze AI Copilot Webhook Server is running."}

# --- Main entry point to run the server ---
if __name__ == "__main__":
    print("--- Starting FastAPI Server ---")
    # Use uvicorn to run the app. It will be available at http://127.0.0.1:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)