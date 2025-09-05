from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from src.llm_connector import get_llm

# This is a simple chain that will power our generative tools
llm = get_llm(temperature=0.7) # Use a higher temperature for creative tasks

# --- Marketing Agent Tool ---
marketing_prompt = PromptTemplate.from_template(
    "You are a marketing expert. Create a short, engaging blog post outline for the following topic: {topic}"
)
marketing_chain = marketing_prompt | llm

def generate_blog_outline(topic: str) -> str:
    """A tool to generate blog post outlines."""
    return marketing_chain.invoke({"topic": topic}).content

marketing_tool = Tool(
    name="Blog_Post_Outline_Generator",
    func=generate_blog_outline,
    description="Use this tool to generate a blog post outline on a given topic. The input should be the topic of the blog."
)

# --- Service Agent Tool ---
# The service agent will primarily use the existing crm_rag_tool,
# but we can give it a specific tool for drafting responses.
service_prompt = PromptTemplate.from_template(
    "You are a customer service expert. Draft a polite and helpful response to the following customer query: {query}"
)
service_chain = service_prompt | llm

def draft_customer_response(query: str) -> str:
    """A tool to draft customer service email responses."""
    return service_chain.invoke({"query": query}).content

service_tool = Tool(
    name="Customer_Response_Drafter",
    func=draft_customer_response,
    description="Use this tool to draft a response to a customer's question. The input should be the customer's full question."
)


email_prompt = PromptTemplate.from_template(
    "You are an expert marketing copywriter. Draft a compelling and professional marketing email based on the following topic. The email should have a clear subject line and call to action.\n\nTopic: {topic}"
)
email_chain = email_prompt | llm

def draft_marketing_email(topic: str) -> str:
    """A tool to draft marketing emails."""
    return email_chain.invoke({"topic": topic}).content

marketing_email_tool = Tool(
    name="Marketing_Email_Drafter",
    func=draft_marketing_email,
    description="Use this tool to draft a marketing email on a given topic. The input should be a string describing the purpose or topic of the email."
)