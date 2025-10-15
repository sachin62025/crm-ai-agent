import json
import re # <-- Add this import
from langchain.tools import Tool
from pydantic import BaseModel, Field
# from typing import Union, Dict

from src.rag_chain import get_rag_chain
from src.crm_connector import create_note_on_deal, update_deal_status
# --- Tool 1: CRM Information Lookup (Unchanged, minor func direct call update) ---
rag_chain = get_rag_chain()
crm_rag_tool = Tool(
    name="CRM_Information_Lookup",
    func=rag_chain.invoke, 
    description="Use this tool to answer any questions about CRM deals, such as status, value, owner, or contacts. The input should be a clear question (e.g., 'What are the details of the deal for Acme Corp?')."
)

# --- Tool 2: Create CRM Note (DEFINITIVE ROBUST VERSION) ---

class CreateNoteInput(BaseModel):
    deal_id: int
    content: str

def run_create_note_tool(tool_input: str) -> str:
    """
    Parses a JSON string input, validates it, and executes the
    create_note_on_deal function. Robustly handles common LLM output parsing quirks,
    including extraneous characters/newlines from the AgentExecutor.
    """
    cleaned_input = tool_input.strip()
    json_str_to_parse = None

    # --- Step 1: Robustly extract the JSON object from the input string ---
    # This regex looks for the content between the first '{' and the last '}'
    # It's designed to ignore leading/trailing non-JSON characters or extra text.
    # The re.DOTALL flag is crucial to allow '.' to match newlines within the JSON content.
    match = re.search(r'\{.*\}', cleaned_input, re.DOTALL)
    if match:
        json_str_to_parse = match.group(0)  
    
    if json_str_to_parse is None:
        # If no direct {..} object was found, it's a severe parsing problem or bad LLM output
        return f"Error: Critical: Could not extract a JSON object (missing braces) from the tool input. Received: '{tool_input}'"

    # --- Step 2: Attempt to parse the extracted JSON string ---
    input_dict = {}
    try:
        # Attempt to load it directly as a JSON object
        input_dict = json.loads(json_str_to_parse)
    except json.JSONDecodeError:
        # If direct loading fails, it might be a JSON string *literal* that needs double-parsing
        # e.g., LLM produced '"{\"key\":\"value\"}"' (a string of a JSON string)
        try:
            # First, load the outer string (which should result in the inner JSON string)
            inner_json_str = json.loads(json_str_to_parse)
            # Then, load the inner JSON string
            input_dict = json.loads(inner_json_str)
        except (json.JSONDecodeError, TypeError) as e:
            return f"Error: Failed to parse extracted content as valid JSON (tried direct and double-decode). Details: {e}. Attempted to parse: '{json_str_to_parse}'"

    # --- Step 3: Validate with Pydantic and execute ---
    try:
        validated_input = CreateNoteInput(**input_dict)
        
        result = create_note_on_deal(
            deal_id=validated_input.deal_id, 
            content=validated_input.content
        )
        
        if result:
            return f"Successfully created the note on deal ID {validated_input.deal_id}."
        else:
            return f"Failed to create the note on deal ID {validated_input.deal_id}. Pipedrive API returned no success data."
            
    except Exception as e:
        # Catches Pydantic validation errors (e.g., if deal_id is not an int)
        # or issues with the create_note_on_deal function itself
        return f"An error occurred during note creation or validation: {e}. Parsed dict: {input_dict}"

# The Tool definition (still no args_schema)
create_crm_note_tool = Tool(
    name="create_crm_note",
    func=run_create_note_tool,
    description=(
        "Use this tool to add a new note to a specific CRM deal. "
        "The input to this tool MUST be a single, valid JSON string. "
        "The JSON string must contain two keys: 'deal_id' (which must be an integer) "
        "and 'content' (which must be a string)."
    )
)


class UpdateDealStatusInput(BaseModel):
    deal_id: int = Field(description="The integer ID of the deal to update.")
    status: str = Field(description="The new status for the deal. Must be one of: 'open', 'won', or 'lost'.")

def run_update_deal_status_tool(tool_input: str) -> str:
    """
    (FIXED) Wrapper for updating a deal's status. Now uses the same robust parsing
    logic as the proven create_crm_note tool.
    """
    cleaned_input = tool_input.strip()
    match = re.search(r'\{.*\}', cleaned_input, re.DOTALL)
    if not match:
        return f"Error: Could not extract a JSON object from the tool input. Received: '{tool_input}'"
    
    json_str_to_parse = match.group(0)
    
    try:
        input_dict = json.loads(json_str_to_parse)
    except json.JSONDecodeError:
        try:
            input_dict = json.loads(json.loads(json_str_to_parse))
        except (json.JSONDecodeError, TypeError) as e:
            return f"Error: Failed to parse extracted content as valid JSON. Details: {e}. Attempted to parse: '{json_str_to_parse}'"

    try:
        validated_input = UpdateDealStatusInput(**input_dict)
        result = update_deal_status(deal_id=validated_input.deal_id, status=validated_input.status)
        if result:
            return f"Successfully updated status for deal ID {validated_input.deal_id} to '{validated_input.status}'."
        else:
            return f"Failed to update status for deal ID {validated_input.deal_id}."
    except Exception as e:
        return f"An error occurred during status update or validation: {e}. Parsed dict: {input_dict}"

update_deal_status_tool = Tool(
    name="update_deal_status",
    func=run_update_deal_status_tool,
    description="Use this tool to update the status of a specific CRM deal. The input must be a valid JSON string with 'deal_id' (integer) and 'status' (string: 'open', 'won', or 'lost') as keys."
)

# --- Final, Updated Toolbox (NO CHANGES) ---
sales_agent_tools = [crm_rag_tool, create_crm_note_tool, update_deal_status_tool]