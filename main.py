import sys
from langchain_core.messages import HumanMessage

# Add the 'src' directory to the Python path
sys.path.append('src')

from src.supervisor import supervisor_graph
from src.config import validate_config

def main():
    """
    Main function to run the interactive multi-agent copilot.
    """
    print("--- Breeze AI Copilot: Multi-Agent Mode ---")
    
    try:
        # First, validate that all config variables are loaded
        validate_config()
        print("✅ Initializing Supervisor Graph...")
        # The graph is already compiled when imported
        app = supervisor_graph
        print("✅ Graph ready. You can now send requests to the agent team.")
        print("   (Type 'exit' to quit)")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return

    while True:
        # Get user input
        question = input("\nYour Request: ")
        
        if question.lower().strip() == 'exit':
            print("Exiting Copilot. Goodbye!")
            break
        
        if not question:
            continue
            
        # Invoke the graph
        print("Supervisor is routing the request...")
        
        # The input to the graph is a dictionary where keys match the AgentState
        initial_state = {"messages": [HumanMessage(content=question)]}
        
        # Stream events to see the flow of the graph in real-time
        for event in app.stream(initial_state, stream_mode="values"):
            # The 'event' is the full state of the graph after a node has run
            last_message = event["messages"][-1]
            if last_message.name:
                 print(f"\n--- Output from: {last_message.name} ---")
                 print(last_message.content)
                 print("----------------------------------------")

if __name__ == "__main__":
    main()