import os
import json
import time
from typing import List, Dict, Any

# We use the script's starting directory (usually /app or /home/.../smart-trade-manager)
# Better: absolute path based on the current working directory
BASE_DIR = os.path.abspath(os.getcwd())
ACTIVE_CONTRACTS_DIR = os.path.join(BASE_DIR, "data", "contracts", "active")
TRASH_CONTRACTS_DIR = os.path.join(BASE_DIR, "data", "contracts", "trash")

def ensure_directories():
    """Ensures that the required directories exist at startup."""
    os.makedirs(ACTIVE_CONTRACTS_DIR, exist_ok=True)
    os.makedirs(TRASH_CONTRACTS_DIR, exist_ok=True)

def get_active_contracts() -> str:
    """Reads the directory of active contracts."""
    try:
        files = os.listdir(ACTIVE_CONTRACTS_DIR)
        contracts = [f for f in files if f.endswith(".json")]
        if not contracts:
            return "There are currently no active contracts."
        return f"Active contracts found: {', '.join(contracts)}"
    except Exception as e:
        return f"Error reading contracts: {e}"

def create_contract(name: str, content: str) -> str:
    """Creates a new contract with metadata."""
    if not name.endswith(".json"):
        name += ".json"
    
    file_path = os.path.join(ACTIVE_CONTRACTS_DIR, name)
    
    # Check if the file already exists
    if os.path.exists(file_path):
        return f"Error: A contract with the name '{name}' already exists. Please read or overwrite it instead."

    # Metadata according to user requirements
    now = time.time()
    base_id = name.replace(".json", "")
    
    data = {
        "id": base_id,
        "created_at": now,
        "last_checked": now,
        "content": content
    }
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return f"Contract '{name}' has been successfully created."
    except Exception as e:
        return f"Error creating contract: {e}"

def read_contract(name: str) -> str:
    """Reads the content of a contract. Attempts fuzzy matching if the exact name is not found."""
    try:
        if not name.endswith(".json"):
            name += ".json"
            
        file_path = os.path.join(ACTIVE_CONTRACTS_DIR, name)
        
        # 1. Exact match attempt
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        
        # 2. Fuzzy/Case-insensitive matching attempt
        files = os.listdir(ACTIVE_CONTRACTS_DIR)
        search_name = name.lower()
        
        # Check for case-insensitive exact match
        for f in files:
            if f.lower() == search_name:
                with open(os.path.join(ACTIVE_CONTRACTS_DIR, f), "r", encoding="utf-8") as f_obj:
                    data = json.load(f_obj)
                    return json.dumps(data, indent=2)
        
        # Check for partial match (startwith or contains)
        suggestions = [f for f in files if search_name.replace(".json", "") in f.lower()]
        if suggestions:
            # If we found a unique partial match, just read it
            if len(suggestions) == 1:
                with open(os.path.join(ACTIVE_CONTRACTS_DIR, suggestions[0]), "r", encoding="utf-8") as f_obj:
                    data = json.load(f_obj)
                    return json.dumps(data, indent=2)
            return f"Error: Contract '{name}' not found. Did you mean one of these: {', '.join(suggestions)}?"
            
        return f"Error: Contract '{name}' not found. Use get_active_contracts to see available files."
    except Exception as e:
        return f"Error reading contract: {e}"

# OpenAI Function Schemas (Tools Definition)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_active_contracts",
            "description": "Returns a list of all currently active contracts in the system. Use this tool when you need an overview of ongoing operations.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_contract",
            "description": "Creates a new contract file for a new operation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file (e.g., AAPL_observation). Without path, can include .json extension."
                    },
                    "content": {
                        "type": "string",
                        "description": "The technical content of the contract (What should the boss do? Why is it being observed?)."
                    }
                },
                "required": ["name", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_contract",
            "description": "Reads the content of an existing contract file. Use this when the user asks 'what is in the contract' or 'tell me about it'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the contract file to read (e.g., AAPL). Approximate names are supported."
                    }
                },
                "required": ["name"]
            }
        }
    }
]

# Dispatcher for LLMService
def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Executes the correct Python tool based on the LLM call."""
    if tool_name == "get_active_contracts":
        return get_active_contracts()
    elif tool_name == "create_contract":
        return create_contract(
            name=arguments.get("name", "unknown"),
            content=arguments.get("content", "")
        )
    elif tool_name == "read_contract":
        return read_contract(
            name=arguments.get("name", "unknown")
        )
    else:
        return f"Error: Tool '{tool_name}' does not exist."
