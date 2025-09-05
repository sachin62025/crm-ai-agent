from langchain_core.runnables import RunnableLambda
from src.tools.generative_tools import marketing_email_tool, marketing_tool

# This agent needs to decide between two tools: drafting an email or an outline.
# We will create a simple routing logic.
def marketing_router(input_data):
    """
    Inspects the user's input and decides which marketing tool to use.
    The input_data is a dictionary, e.g., {"input": "draft an email..."}
    """
    user_input = input_data.get("input", "").lower()
    if "email" in user_input:
        # If the user asks for an email, route to the email tool.
        # The tool expects a simple string, not a dictionary.
        return marketing_email_tool.invoke(user_input)
    else:
        # Otherwise, default to the blog post outline tool.
        return marketing_tool.invoke(user_input)

def get_marketing_agent():
    """
    Initializes and returns the Marketing Agent.
    
    This is now a simple, robust chain that directly routes to the correct tool
    instead of a complex ReAct agent. This avoids parsing errors with long outputs.
    """
    # RunnableLambda wraps our router function so it can be part of a LangChain chain.
    agent = RunnableLambda(marketing_router)
    return agent