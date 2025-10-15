import sys
import gradio as gr
from langchain_core.messages import HumanMessage
import time

sys.path.append("src")
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
        if (
            hasattr(last_message, "name")
            and last_message.name
            and last_message.name != "supervisor"
        ):
            print(f"--- Output from: {last_message.name} ---")
            print(last_message.content)
            print("----------------------------------------")
            # This part handles the streaming display in the UI
            full_content = last_message.content
            for char in full_content:
                response_stream += char
                time.sleep(0.005)  # speed of streaming
                yield response_stream

    # If for some reason no agent responded, provide a fallback message
    if not response_stream:
        yield "I'm sorry, I couldn't process that request. Please try rephrasing."


custom_css = """
/* General styling */
body {
    font-family: 'Roboto', sans-serif;
    background: #f5f5f5;
}

/* Main container styling */
.gradio-container {
    border-radius: 20px !important;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
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
with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="blue", secondary_hue="sky"),
    css=custom_css,
    title="Breeze AI Copilot",
) as demo:
    # Full-width header at the top
    gr.HTML("""
        <div class="header">
            <h1>🌬️ Breeze AI Copilot</h1>
            <p>Your intelligent assistant for CRM tasks.</p>
        </div>
    """)

    with gr.Row():
        # Left Column: Features
        with gr.Column(scale=1):  # This column will take up 1/3 of the width
            gr.HTML("""
                <div style="padding:20px; background:#fff; border-radius:15px; box-shadow:0 2px 8px rgba(0,0,0,0.07); margin-bottom:20px;">
                    <h2 style="color:#4a90e2; margin-bottom:10px;">✨ Features</h2>
                    <ul style="font-size:1.1em; line-height:1.7;">
                        <li>Retrieve CRM deal details instantly</li>
                        <li>Add notes to deals and contacts</li>
                        <li>Update deal status (won/lost/in progress)</li>
                        <li>Draft blog post outlines and marketing emails</li>
                        <li>Generate polite customer responses</li>
                        <li>Answer questions about your CRM data</li>
                        <li>And much more!</li>
                    </ul>
                </div>
            """)
            # You might want to add some space below the features if it looks too cramped with the window size
            gr.HTML("<div style='height: 20px;'></div>")

        # Middle Column: Chatbot
        with gr.Column(
            scale=2
        ):  # This column will take up 2/3 of the width, making it the widest
            chatbot = gr.Chatbot(
                [],
                elem_id="chatbot",
                bubble_full_width=False,
                avatar_images=(None, "src/static/bot.jpg"),
                height=600,
                label="Breeze AI",
                show_label=False,
            )

            with gr.Row():
                txt = gr.Textbox(
                    scale=4,
                    show_label=False,
                    placeholder="e.g., What is the value of the deal with Global Logistics?",
                    container=False,
                )
                submit_btn = gr.Button(
                    "Send", variant="primary", scale=1, min_width=150
                )

            gr.Examples(
                examples=[
                    "What are the details of the deal with EmpowerMove?",
                    "Add a note to deal ID 5 saying 'Customer is ready for a final demo.'",
                    "Update the status of deal ID 10 to 'won'",
                    "Draft a blog post outline about 'The benefits of proactive customer service'",
                    "Write a marketing email about our new feature: AI-powered analytics",
                    "Draft a polite response to a customer asking about an invoice delay",
                ],
                inputs=txt,
                label="Click on an example to run it",
            )

            # Right Column: Tools Used
        import gradio as gr

        # Function to generate Tools Used section
        def render_tools_used():
            tools = [
                {
                    "name": "Gradio",
                    "logo": "https://images.seeklogo.com/logo-png/51/1/gradio-logo-png_seeklogo-515011.png",
                },
                {
                    "name": "LangChain",
                    "logo": "https://avatars.githubusercontent.com/u/61469645?s=200&v=4",
                },
                {
                    "name": "Python",
                    "logo": "https://cdn-icons-png.flaticon.com/512/5968/5968350.png",
                },
            ]

            html_content = """
            <div style="padding:20px; background:#fff; border-radius:15px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.07); margin-top:0;">
                <h2 style="color:#4a90e2; margin-bottom:10px;">🛠️ Tools Used</h2>
            """

            for tool in tools:
                html_content += f"""
                    <li>
                        <img src="{tool["logo"]}" alt="{tool["name"]}" 
                            style="height:40px;vertical-align:middle;margin-right:12px;">
                        {tool["name"]}
                    </li>
                """

            html_content += """
                </ul>
            </div>
            """
            return html_content

        # Example usage in your layout
        with gr.Column(scale=1):  # Right column
            gr.HTML(render_tools_used())
            gr.HTML("<div style='height: 20px;'></div>")

    # --- Event Listeners for Chat Functionality ---
    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        user_message = history[-1][0]
        history[-1][1] = ""
        for response_chunk in chat_responder(user_message, history):
            history[-1][1] = response_chunk
            yield history

    submit_btn.click(user, [txt, chatbot], [txt, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    txt.submit(user, [txt, chatbot], [txt, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

if __name__ == "__main__":
    print("--- Launching Gradio Web UI ---")
    demo.launch(debug=True)
