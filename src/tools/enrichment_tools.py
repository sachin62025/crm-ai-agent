# src/tools/enrichment_tools.py

from langchain.tools import Tool


def research_company(company_name: str) -> str:
    """
    Simulates researching a company to find key information and buyer intent signals.
    In a real-world scenario, this function would connect to external APIs
    (e.g., news APIs, financial data services, or company intelligence platforms).

    Args:
        company_name (str): The name of the company to research.

    Returns:
        str: A summary of the research findings.
    """
    print(f"--- TOOL: Researching company: {company_name} ---")

    # Simulate finding different data points based on the company name for testing
    if "innovate" in company_name.lower():
        return (
            f"Research on '{company_name}':\n"
            f"- Industry: Tech & SaaS\n"
            f"- Recent News: Just secured $50M in Series B funding for AI development.\n"
            f"- Buyer Intent Signals: High intent detected. Actively searching for 'enterprise-grade cloud solutions' and 'AI integration platforms'. They have recently visited our pricing page.\n"
            f"- Key Contacts: Jane Doe (CTO), John Smith (VP of Innovation)."
        )
    elif "global" in company_name.lower():
        return (
            f"Research on '{company_name}':\n"
            f"- Industry: Logistics & Supply Chain\n"
            f"- Recent News: Announced expansion into the European market.\n"
            f"- Buyer Intent Signals: Medium intent. Showing interest in 'international logistics efficiency' and 'supply chain optimization software'.\n"
            f"- Key Contacts: Emily White (Director of Operations)."
        )
    else:
        return (
            f"Research on '{company_name}':\n"
            f"- Industry: General Business\n"
            f"- Recent News: No major news found.\n"
            f"- Buyer Intent Signals: Low intent detected. General browsing activity noted.\n"
            f"- Key Contacts: Could not automatically identify key contacts."
        )


company_research_tool = Tool(
    name="Company_Research_Tool",
    func=research_company,
    description="Use this tool to research a company by its name. It provides a summary of the company's industry, recent news, buyer intent signals, and potential key contacts.",
)
