from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import json
import os

@dataclass
class AgentConfig:
    """Agent configuration loaded from a JSON file."""
    alias: str
    router_host: str
    router_port: int
    llm_base_url: str
    llm_model_name: str
    system_prompt: str

    @classmethod
    def from_file(cls, path: str = "config.json") -> "AgentConfig":
        if not os.path.exists(path):
            # Fallback for Docker/Development: check if absolute or relative
            if not os.path.isabs(path):
                alt_path = os.path.join(os.getcwd(), path)
                if os.path.exists(alt_path):
                    path = alt_path
                else:
                    raise FileNotFoundError(f"Config file not found: {path}")
            else:
                raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

@dataclass
class TelChatMessage:
    """Message object following the TelChat blueprint schema."""
    sender: str
    to: str
    msg_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_json_line(self) -> str:
        """Serializes the message to a single JSON line with newline and byte_count."""
        # Use default separators to match the router's internal byte_count calculation
        data_json = json.dumps(self.data)
        byte_count = len(data_json.encode("utf-8"))

        msg_dict = {
            "from": self.sender,
            "to": self.to,
            "msg_type": self.msg_type,
            "timestamp": self.timestamp,
            "byte_count": byte_count,
            "data": self.data
        }
        return json.dumps(msg_dict) + "\n"

    @classmethod
    def from_json(cls, json_str: str) -> "TelChatMessage":
        """Parses a JSON line into a TelChatMessage object."""
        d = json.loads(json_str)
        return cls(
            sender=d.get("from", ""),
            to=d.get("to", ""),
            msg_type=d.get("msg_type", ""),
            data=d.get("data", {}),
            timestamp=d.get("timestamp", time.time())
        )
