# # app.py

# import sys
# import gradio as gr
# from langchain_core.messages import HumanMessage

# # Add the 'src' directory to the Python path to import our modules
# sys.path.append('src')

# from src.supervisor import supervisor_graph
# from src.config import validate_config

# # --- Initialization ---
# print("--- Initializing Breeze AI Copilot ---")
# try:
#     # Validate that all config variables are loaded
#     validate_config()
#     # Initialize the supervisor graph, which is the brain of our application
#     app_supervisor = supervisor_graph
#     print("✅ Supervisor Graph initialized successfully.")
# except Exception as e:
#     print(f"❌ Critical Error on Startup: {e}")
#     # Exit if the core components can't be initialized
#     sys.exit(1)

# # --- Core Chatbot Logic ---
# def chat_responder(message, history):
#     """
#     This function is the core of the Gradio chat interface.
#     It takes a user's message and the chat history, sends it to the supervisor agent,
#     and streams the response back to the UI.
#     """
#     print(f"\n--- New Request Received ---")
#     print(f"User Message: {message}")
    
#     # The input to the graph is a dictionary matching the AgentState
#     initial_state = {"messages": [HumanMessage(content=message)]}
    
#     response_message = ""
    
#     # Stream events to see the flow of the graph in real-time
#     print("Supervisor is routing the request...")
#     for event in app_supervisor.stream(initial_state, stream_mode="values"):
#         # The 'event' is the full state of the graph after a node has run
#         last_message = event["messages"][-1]
        
#         # We only want to display the final output from the chosen agent
#         if last_message.name and last_message.name != "supervisor":
#              print(f"--- Output from: {last_message.name} ---")
#              print(last_message.content)
#              print("----------------------------------------")
#              response_message = last_message.content
    
#     # If for some reason no agent responded, provide a fallback message
#     if not response_message:
#         response_message = "I'm sorry, I couldn't process that request. Please try rephrasing."
        
#     return response_message

# # --- Build the Gradio UI ---
# with gr.Blocks(theme=gr.themes.Default(primary_hue="blue"), title="Breeze AI Copilot") as demo:
#     gr.Markdown(
#         """
#         # Breeze AI Copilot 🚀
#         Your intelligent assistant for CRM tasks. 
#         You can ask about deal statuses, ask for marketing content, or request customer service responses.
#         """
#     )
#     gr.ChatInterface(
#         fn=chat_responder,
#         chatbot=gr.Chatbot(height=600),
#         textbox=gr.Textbox(placeholder="e.g., What is the value of the deal with Global Logistics?", container=False, scale=7),
#         title=None,
#         examples=[
#             "What are the details of the deal with EmpowerMove?",
#             "Add a note to deal ID 5 saying 'Customer is ready for a final demo.'",
#             "Update the status of deal ID 10 to 'won'",
#             "Draft a blog post outline about 'The benefits of proactive customer service'",
#             "Write a marketing email about our new feature: AI-powered analytics",
#             "Draft a polite response to a customer asking about an invoice delay"
#         ],
#         cache_examples=False
#     )

# # --- Main entry point to run the server ---
# if __name__ == "__main__":
#     print("--- Launching Gradio Web UI ---")
#     # The launch() method creates a web server and provides a public URL if needed.
#     demo.launch()


#------------------------------------------------------------------------------------

# app.py

import sys
import gradio as gr
from langchain_core.messages import HumanMessage
import time
sys.path.append('src')
from src.supervisor import supervisor_graph
from src.config import validate_config

# --- Initialization ---
print("--- Initializing Breeze AI Copilot ---")
try:
    # Validate that all config variables are loaded from your config file
    validate_config()

    # Initialize your actual supervisor graph, which is the brain of the application.
    app_supervisor = supervisor_graph
    print("✅ Supervisor Graph initialized successfully.")

except Exception as e:
    print(f"❌ Critical Error on Startup: {e}")
    sys.exit(1)

# --- Core Chatbot Logic ---
def chat_responder(message, history):
    """
    This function is the core of the Gradio chat interface.
    It takes a user's message and the chat history, sends it to the supervisor agent,
    and streams the response back to the UI.
    """
    print(f"\n--- New Request Received ---")
    print(f"User Message: {message}")

    # The input to the graph is a dictionary matching the AgentState
    initial_state = {"messages": [HumanMessage(content=message)]}
    
    response_stream = ""
    
    # Stream events to see the flow of the graph in real-time
    print("Supervisor is routing the request...")
    for event in app_supervisor.stream(initial_state, stream_mode="values"):
        # The 'event' is the full state of the graph after a node has run
        last_message = event["messages"][-1]
        
        # We only want to display the final output from the chosen agent
        if hasattr(last_message, 'name') and last_message.name and last_message.name != "supervisor":
             print(f"--- Output from: {last_message.name} ---")
             print(last_message.content)
             print("----------------------------------------")
             # This part handles the streaming display in the UI
             full_content = last_message.content
             for char in full_content:
                 response_stream += char
                 time.sleep(0.005) # speed of streaming
                 yield response_stream
    
    # If for some reason no agent responded, provide a fallback message
    if not response_stream:
        yield "I'm sorry, I couldn't process that request. Please try rephrasing."

# --- Custom CSS for a modern look and feel ---
custom_css = """
/* General styling */
body {
    font-family: 'Roboto', sans-serif;
    background: #f5f5f5;
}

/* Main container styling */
.gradio-container {
    border-radius: 20px !important;
    box-shadow: 0 4px_8px 0 rgba(0,0,0,0.2);
    transition: 0.3s;
    background: white;
}

/* Chatbot styling */
.chatbot {
    background: #f9f9f9;
    border-radius: 15px;
    box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.06);
}

/* Textbox styling */
textarea {
    border-radius: 15px !important;
    border: 1px solid #ccc !important;
    transition: border-color 0.3s, box-shadow 0.3s;
}
textarea:focus {
    border-color: #4a90e2 !important;
    box-shadow: 0 0 5px rgba(74, 144, 226, 0.5) !important;
}

/* Button styling */
.gr-button {
    background-color: #4a90e2 !important;
    color: white !important;
    border-radius: 15px !important;
    border: none !important;
    transition: background-color 0.3s;
}
.gr-button:hover {
    background-color: #357abd !important;
}

/* Header styling */
.header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #6e8efb, #a777e3);
    color: white;
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
}
.header h1 {
    margin: 0;
    font-size: 2.5em;
    font-weight: 300;
}

/* Examples styling */
.examples {
    padding: 15px;
    background: #fafafa;
    border-radius: 15px;
    margin-top: 15px;
}
"""

# --- Build the Gradio UI with a modern theme and layout ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="sky"), css=custom_css, title="Breeze AI Copilot") as demo:
    with gr.Column():
        # Header Section
        with gr.Row():
            gr.HTML("""
                <div class="header">
                    <h1>🌬️ Breeze AI Copilot</h1>
                    <p>Your intelligent assistant for CRM tasks.</p>
                </div>
            """)

        # Main Chat Interface
        chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            bubble_full_width=False,
            avatar_images=(None, "bot.jpg"), 
            height=600,
            label="Breeze AI",
            show_label=False
        )
        
        with gr.Row():
            txt = gr.Textbox(
                scale=4,
                show_label=False,
                placeholder="e.g., What is the value of the deal with Global Logistics?",
                container=False,
            )
            submit_btn = gr.Button("Send", variant="primary", scale=1, min_width=150)
    
        # Examples Section
        gr.Examples(
            examples=[
                "What are the details of the deal with EmpowerMove?",
                "Add a note to deal ID 5 saying 'Customer is ready for a final demo.'",
                "Update the status of deal ID 10 to 'won'",
                "Draft a blog post outline about 'The benefits of proactive customer service'",
                "Write a marketing email about our new feature: AI-powered analytics",
                "Draft a polite response to a customer asking about an invoice delay"
            ],
            inputs=txt,
            label="Click on an example to run it"
        )
    
    # --- Event Listeners for Chat Functionality ---
    def user(user_message, history):
        # This function adds the user's message to the chat history
        return "", history + [[user_message, None]]

    def bot(history):
        # This function gets the user's message and streams the bot's response
        user_message = history[-1][0]
        history[-1][1] = ""
        # Call the actual chat responder logic to get the streaming response
        for response_chunk in chat_responder(user_message, history):
            history[-1][1] = response_chunk
            yield history

    # Define the click/submit events
    submit_btn.click(user, [txt, chatbot], [txt, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    txt.submit(user, [txt, chatbot], [txt, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

# --- Main entry point to run the server ---
if __name__ == "__main__":
    print("--- Launching Gradio Web UI ---")
    # The launch() method creates a web server and provides a public URL if needed.
    demo.launch(debug=True)