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
    else:
        return f"Error: Tool '{tool_name}' does not exist."
