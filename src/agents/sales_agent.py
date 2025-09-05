from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools.render import render_text_description

from src.llm_connector import get_llm
from src.tools.crm_tools import sales_agent_tools

# --- THIS IS THE CRITICAL FIX ---
# We are making the instructions for Action Input much more explicit to prevent parsing errors.
AGENT_PROMPT_TEMPLATE = """
You are the Breeze AI Sales Agent. Your primary goal is to assist users by
accessing CRM data and performing actions within the CRM.

You have access to the following tools:
{tools}

To answer the user's request, you MUST use the following format:

Question: the user's input question you must answer
Thought: you should always think about what to do. You should use information from previous observations to inform your subsequent actions. For example, if you look up a deal and find its ID, you should use that specific ID in the next step.
Action: the action to take, should be one of [{tool_names}]
Action Input: The input to the action.
- If the tool takes a single string argument, the input should be a simple string.
- If the tool takes multiple arguments (like create_crm_note), the input MUST be a valid JSON dictionary with the correct argument names as keys. For example: {{"deal_id": 123, "content": "This is a summary."}}
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

def get_sales_agent():
    """
    Initializes and returns the Sales Agent executor using the reliable
    ReAct agent type, which is compatible with a wide range of LLMs.
    """
    llm = get_llm(temperature=0.0) # ReAct agents work best with precise LLMs
    tools = sales_agent_tools
    
    prompt = PromptTemplate.from_template(AGENT_PROMPT_TEMPLATE).partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
    )
    
    # We are back to using the reliable 'create_react_agent'
    agent = create_react_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor