import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

from src.agents.sales_agent import get_sales_agent
from src.agents.marketing_agent import get_marketing_agent
from src.agents.service_agent import get_service_agent
from src.llm_connector import get_llm


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str


# Initialize the agents
sales_agent = get_sales_agent()
marketing_agent = get_marketing_agent()
service_agent = get_service_agent()


def get_last_human_message(state):
    return state["messages"][-1].content


# --- NO CHANGE NEEDED: The Sales Agent still returns a dictionary ---
def sales_agent_node(state):
    result = sales_agent.invoke({"input": get_last_human_message(state)})
    return {
        "messages": [
            BaseMessage(content=result["output"], type="assistant", name="Sales Agent")
        ]
    }


# --- FIX 1: The result from the new Marketing Agent is now a direct string ---
def marketing_agent_node(state):
    result = marketing_agent.invoke({"input": get_last_human_message(state)})
    # The result is the final string content, so we use it directly.
    return {
        "messages": [
            BaseMessage(content=result, type="assistant", name="Marketing Agent")
        ]
    }


# --- FIX 2: Same fix for the new Service Agent node ---
def service_agent_node(state):
    result = service_agent.invoke({"input": get_last_human_message(state)})
    # The result is the final string content, so we use it directly.
    return {
        "messages": [
            BaseMessage(content=result, type="assistant", name="Service Agent")
        ]
    }


# --- Supervisor Chain (NO CHANGES NEEDED) ---
members = ["Sales Agent", "Marketing Agent", "Service Agent"]
system_prompt = (
    "You are a supervisor. Your task is to route the user's request to the appropriate expert agent.\n"
    "The available agents are: {members}.\n"
    "- Route to 'Sales Agent' for questions about CRM data, deal status, value, and for creating notes or updating deals.\n"
    "- Route to 'Marketing Agent' for requests to generate creative content like blog posts or marketing emails.\n"
    "- Route to 'Service Agent' for requests related to customer service or drafting customer-facing responses.\n"
    "Given the user's request, respond with the name of the agent that should handle it, or 'FINISH' if the request is complete."
)
options = ["FINISH"] + members
function_def = {
    "name": "route",
    "description": "Select the next agent to act or FINISH.",
    "parameters": {
        "type": "object",
        "properties": {"next": {"type": "string", "enum": options}},
    },
}
prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("human", "{messages}")]
)
llm = get_llm(temperature=0.0)
supervisor_chain = prompt | llm.with_structured_output(function_def)


def router(state):
    last_message = state["messages"][-1].content
    route = supervisor_chain.invoke(
        {
            "members": ", ".join(members),
            "messages": [HumanMessage(content=last_message)],
        }
    )
    print(f"\n--- SUPERVISOR DECISION ---\nRoute: {route}\n--- END DECISION ---\n")
    return {"next": route["next"]}


# --- Graph Definition (NO CHANGES NEEDED) ---
graph = StateGraph(AgentState)
graph.add_node("supervisor", router)
graph.add_node("Sales Agent", sales_agent_node)
graph.add_node("Marketing Agent", marketing_agent_node)
graph.add_node("Service Agent", service_agent_node)

graph.set_entry_point("supervisor")

graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {
        "Sales Agent": "Sales Agent",
        "Marketing Agent": "Marketing Agent",
        "Service Agent": "Service Agent",
        "FINISH": END,
    },
)

graph.add_edge("Sales Agent", END)
graph.add_edge("Marketing Agent", END)
graph.add_edge("Service Agent", END)

supervisor_graph = graph.compile()
