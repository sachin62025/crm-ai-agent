from langchain_core.runnables import RunnableLambda
from src.tools.generative_tools import service_tool
from src.tools.crm_tools import crm_rag_tool


def service_router(input_data: dict) -> str:
    """
    Inspects the user's input and decides which service tool to use.
    """
    user_input = input_data.get("input", "").lower()
    # Check for keywords that indicate a user wants to draft a response.
    draft_keywords = ["draft", "write", "respond", "response", "reply"]

    if any(keyword in user_input for keyword in draft_keywords):
        # If the user wants to draft something, use the generative tool.
        return service_tool.invoke(user_input)
    else:
        # Otherwise, assume it's a question about CRM data and use the RAG tool.
        return crm_rag_tool.invoke(user_input)


def get_service_agent():
    """
    Initializes and returns the Service Agent.
    This is now a simple, robust chain that directly routes to the correct tool,
    avoiding parsing errors with long, creative outputs.
    """
    agent = RunnableLambda(service_router)
    return agent
